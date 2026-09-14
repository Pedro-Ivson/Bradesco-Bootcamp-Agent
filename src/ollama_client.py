"""Cliente mínimo para a API local de chat do Ollama."""

from __future__ import annotations

import os
from typing import Any

import requests


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")


def chat(messages: list[dict[str, str]], model: str = DEFAULT_MODEL) -> str:
    """Envia uma conversa ao Ollama e retorna somente o texto do assistente."""

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_ctx": 8192,
        },
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=240)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            "Não foi possível acessar o Ollama. Verifique se ele está em execução "
            f"em {OLLAMA_URL} e se o modelo '{model}' está instalado."
        ) from exc

    body = response.json()
    content = body.get("message", {}).get("content")
    if not content:
        raise RuntimeError(f"Ollama devolveu uma resposta sem conteúdo: {body}")
    return str(content).strip()

