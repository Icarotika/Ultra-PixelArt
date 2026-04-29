"""Backend da assistente acadêmica com FastAPI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DADOS_PATH = BASE_DIR / "dados.json"

app = FastAPI(title="Assistente Acadêmica API", version="1.0.0")

# CORS liberado para facilitar testes locais do frontend em outro host/porta.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Payload de entrada da rota /chat."""

    pergunta: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    """Payload de saída da rota /chat."""

    resposta: str
    modo: str


def carregar_dados_secretaria() -> dict[str, Any]:
    """Carrega o arquivo dados.json com as regras da secretaria."""
    if not DADOS_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {DADOS_PATH}")

    with DADOS_PATH.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def montar_prompt_base(dados: dict[str, Any]) -> str:
    """Monta um prompt fixo com identidade e regras da assistente."""
    regras = [
        "Você é uma assistente acadêmica virtual da secretaria de faculdade.",
        "Responda sempre em português, de forma educada e objetiva.",
        "Use apenas as informações fornecidas no contexto.",
        "Não invente regras, prazos, documentos ou processos.",
        "Se a pergunta não estiver coberta pelo contexto, responda: 'Não possuo dados suficientes para responder essa pergunta com segurança.'",
    ]

    contexto = json.dumps(dados, ensure_ascii=False, indent=2)
    return "\n".join(regras) + "\n\nContexto oficial da secretaria:\n" + contexto


def responder_localmente(pergunta: str, dados: dict[str, Any]) -> str:
    """Fallback local baseado em palavras-chave para manter o projeto funcional sem API externa."""
    pergunta_lower = pergunta.lower()

    mapa_topicos = {
        "matrícula": ["matrícula", "matricula", "rematrícula", "rematricula"],
        "trancamento": ["trancamento", "trancar", "trancar curso"],
        "documentos": ["documento", "documentos", "comprovante", "histórico", "historico"],
        "prazos": ["prazo", "prazos", "data", "datas", "calendário", "calendario"],
    }

    for topico, palavras in mapa_topicos.items():
        if any(palavra in pergunta_lower for palavra in palavras):
            conteudo = dados.get(topico)
            if conteudo:
                return f"Com base nos dados da secretaria sobre {topico}:\n{json.dumps(conteudo, ensure_ascii=False, indent=2)}"

    return "Não possuo dados suficientes para responder essa pergunta com segurança."


async def consultar_openai(prompt_base: str, pergunta: str) -> str | None:
    """Tenta obter resposta via OpenAI. Retorna None se não estiver configurado."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": prompt_base},
            {"role": "user", "content": pergunta},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        # Em caso de erro externo, o backend continua funcional com fallback local.
        return None


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Recebe pergunta do usuário e devolve resposta da assistente."""
    try:
        dados = carregar_dados_secretaria()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="dados.json inválido") from exc

    prompt_base = montar_prompt_base(dados)
    resposta_openai = await consultar_openai(prompt_base, request.pergunta)

    if resposta_openai:
        return ChatResponse(resposta=resposta_openai, modo="openai")

    resposta_local = responder_localmente(request.pergunta, dados)
    return ChatResponse(resposta=resposta_local, modo="fallback_local")
