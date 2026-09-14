"""Extrai os PDFs da pasta de nutrição para uma base JSON pesquisável."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader


DEFAULT_SOURCE_DIR = Path(__file__).resolve().parents[1] / "data" / "pdfs"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "knowledge.json"
HEADER_PATTERN = re.compile(r"Base de Conhecimento em Nutrição\s*\|\s*NotebookLM", re.I)


def clean_text(value: str) -> str:
    value = value.replace("\u00a0", " ").replace("\uf0b7", "•")
    value = HEADER_PATTERN.sub("", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def split_text(value: str, limit: int = 2200) -> list[str]:
    """Divide um texto em blocos sem cortar palavras no meio."""

    if len(value) <= limit:
        return [value]
    pieces: list[str] = []
    remaining = value
    while len(remaining) > limit:
        cut = remaining.rfind(". ", 0, limit)
        if cut < int(limit * 0.55):
            cut = remaining.rfind(" ", 0, limit)
        if cut < 1:
            cut = limit
        else:
            cut += 1
        pieces.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        pieces.append(remaining)
    return pieces


def extract(source_dir: Path, output: Path) -> dict:
    pdfs = sorted(source_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"Nenhum PDF encontrado em {source_dir}")

    chunks: list[dict] = []
    documents: list[dict] = []
    for pdf in pdfs:
        reader = PdfReader(str(pdf))
        documents.append({"file": pdf.name, "pages": len(reader.pages)})
        for page_number, page in enumerate(reader.pages, start=1):
            text = clean_text(page.extract_text() or "")
            if not text:
                continue
            for piece_number, piece in enumerate(split_text(text), start=1):
                section = piece[:120].strip()
                chunks.append(
                    {
                        "source": pdf.name,
                        "page": page_number,
                        "section": f"trecho {piece_number}",
                        "text": piece,
                    }
                )

    payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            # Evita gravar o caminho absoluto do computador no artefato versionável.
            "source_directory": source_dir.name,
            "documents": documents,
            "disclaimer": (
                "Base educacional. Não substitui avaliação clínica, diagnóstico, "
                "prescrição dietética ou acompanhamento profissional."
            ),
        },
        "chunks": chunks,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = extract(args.source_dir, args.output)
    print(f"Base criada em: {args.output}")
    print(f"Documentos: {len(payload['metadata']['documents'])}")
    print(f"Trechos: {len(payload['chunks'])}")


if __name__ == "__main__":
    main()
