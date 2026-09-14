"""Leitura e recuperação simples da base de conhecimento nutricional."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


STOPWORDS = {
    "a", "as", "ao", "aos", "com", "como", "da", "das", "de", "do", "dos",
    "e", "em", "entre", "é", "essa", "esse", "esta", "este", "eu", "faz",
    "fazer", "foi", "há", "isso", "mais", "mas", "me", "meu", "minha", "na",
    "nas", "no", "nos", "o", "os", "ou", "para", "por", "qual", "que", "se",
    "sem", "ser", "sua", "suas", "também", "um", "uma", "umas", "uns", "você",
    "vocês", "sobre", "pode", "posso", "quero", "preciso", "tenho", "tem",
    "funcao", "papel", "serve", "servem", "significa", "significam", "sao",
}


@dataclass(frozen=True)
class Chunk:
    """Trecho pesquisável extraído de uma fonte."""

    source: str
    page: int
    section: str
    text: str


def _without_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _normalize_token(token: str) -> str:
    # Ajuda a aproximar plurais regulares sem depender de uma biblioteca pesada.
    if len(token) > 4 and token.endswith("s"):
        return token[:-1]
    return token


def _token_list(value: str) -> list[str]:
    """Tokeniza português de forma determinística para busca lexical."""

    normalized = _without_accents(value).lower()
    words = re.findall(r"[a-z0-9]{3,}", normalized)
    return [_normalize_token(word) for word in words if word not in STOPWORDS]


def tokenize(value: str) -> set[str]:
    return set(_token_list(value))


def load_chunks(path: Path | str) -> list[Chunk]:
    """Carrega os trechos produzidos por prepare_knowledge.py."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Base não encontrada em {path}. Execute src/prepare_knowledge.py primeiro."
        )

    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    chunks: list[Chunk] = []
    for item in raw.get("chunks", []):
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        chunks.append(
            Chunk(
                source=str(item.get("source", "fonte não informada")),
                page=int(item.get("page", 0)),
                section=str(item.get("section", "")),
                text=text,
            )
        )
    if not chunks:
        raise ValueError(f"A base {path} não contém trechos utilizáveis.")
    return chunks


def _score(query_terms: set[str], chunk: Chunk) -> tuple[int, int, int]:
    chunk_tokens = _token_list(f"{chunk.section} {chunk.text}")
    chunk_terms = set(chunk_tokens)
    overlap = len(query_terms & chunk_terms)
    frequency = sum(chunk_tokens.count(term) for term in query_terms)
    # O terceiro valor favorece trechos com maior cobertura dos termos da pergunta.
    coverage = int(100 * overlap / max(len(query_terms), 1))
    return overlap, frequency, coverage


def retrieve(question: str, chunks: Iterable[Chunk], limit: int = 4) -> list[tuple[Chunk, int]]:
    """Retorna os trechos com maior sobreposição lexical com a pergunta."""

    available = list(chunks)
    query_terms = tokenize(question)
    ranked = [(_score(query_terms, chunk), index, chunk) for index, chunk in enumerate(available)]
    ranked.sort(key=lambda item: (item[0][0], item[0][1], item[0][2], -item[1]), reverse=True)

    if not query_terms:
        return [(chunk, 0) for chunk in available[:limit]]

    selected = [(chunk, score[0]) for score, _index, chunk in ranked if score[0] > 0][:limit]
    if selected:
        return selected
    # Mesmo sem correspondência, entregar um pequeno contexto inicial permite ao agente
    # declarar a limitação com honestidade e evita inventar uma resposta.
    return [(chunk, 0) for chunk in available[:limit]]


def format_context(results: Iterable[tuple[Chunk, int]], max_chars: int = 9000) -> str:
    """Formata os trechos para o prompt e preserva a origem de cada evidência."""

    blocks: list[str] = []
    used = 0
    for chunk, score in results:
        label = f"{chunk.source}, p. {chunk.page}"
        if chunk.section:
            label += f" — {chunk.section}"
        block = f"[Fonte: {label} | relevância lexical: {score}]\n{chunk.text}"
        remaining = max_chars - used
        if remaining <= 0:
            break
        blocks.append(block[:remaining])
        used += len(block) + 2
    return "\n\n".join(blocks) or "Nenhum trecho da base foi recuperado."


def source_labels(results: Iterable[tuple[Chunk, int]]) -> list[str]:
    """Retorna rótulos únicos para exibição na interface."""

    labels: list[str] = []
    for chunk, _score_value in results:
        label = f"{chunk.source} (p. {chunk.page})"
        if label not in labels:
            labels.append(label)
    return labels
