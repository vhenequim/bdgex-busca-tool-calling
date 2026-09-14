"""API REST (Cap. 4, "Camada de API"): `POST /api/search`.

    uvicorn pfc_busca.api:app --port 8000

Recebe `{"query": "..."}` e devolve os parâmetros extraídos, a sequência de
tool calls, os produtos encontrados (semente sintética) e as latências de
cada etapa (RF1, RF2, RF3, RF5).

`model` na requisição é aceito só em desenvolvimento (RF4): exportar
`PFC_PERMITIR_MODELO=1`. Em operação o modelo é fixo por `PFC_MODELO_PADRAO`.
"""

from __future__ import annotations

import os
from datetime import date

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from pfc_busca import agent, db
from pfc_busca.pipeline import Pipeline

load_dotenv()

MODELO_PADRAO = os.environ.get("PFC_MODELO_PADRAO", "qwen3:4b-instruct-2507-q4_K_M")
PERMITIR_MODELO = os.environ.get("PFC_PERMITIR_MODELO", "0") == "1"

app = FastAPI(title="PFC · Busca em linguagem natural no acervo da DSG", version="0.1.0")
_pipelines: dict[str, Pipeline] = {}


class Requisicao(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    model: str | None = None
    resposta_final: bool = True


def _pipeline(modelo: str) -> Pipeline:
    if modelo not in _pipelines:
        _pipelines[modelo] = Pipeline(agent.Tradutor(modelo))
    return _pipelines[modelo]


@app.get("/api/health")
def health():
    return {
        "ollama": agent.versao_servidor(),
        "banco": db.disponivel(),
        "modelo_padrao": MODELO_PADRAO,
        "selecao_de_modelo_por_requisicao": PERMITIR_MODELO,
    }


@app.post("/api/search")
def search(req: Requisicao):
    modelo = MODELO_PADRAO
    if req.model and req.model != MODELO_PADRAO:
        if not PERMITIR_MODELO:
            raise HTTPException(403, "seleção de modelo por requisição é restrita ao ambiente de desenvolvimento")
        modelo = req.model
    try:
        pipeline = _pipeline(modelo)
    except agent.ModeloIndisponivel as erro:
        raise HTTPException(503, str(erro)) from erro

    execucao = pipeline.buscar(req.query, date.today(), resposta_final=req.resposta_final)
    t = execucao.traducao
    return {
        "consulta": req.query,
        "modelo": modelo,
        "parametros": t.predito,
        "chamou_ferramenta": t.chamou_ferramenta,
        "tool_calls": t.tool_calls,
        "produtos": ({"executado": execucao.busca.executado, "total": execucao.busca.total,
                      "itens": execucao.busca.itens, "erro": execucao.busca.erro}
                     if execucao.busca else None),
        "resposta": execucao.resposta_final if execucao.resposta_final is not None else t.texto_resposta,
        "latencias_ms": {
            "llm_traducao": t.latencia_llm_ms,
            "ferramenta_sql": execucao.busca.latencia_ms if execucao.busca else None,
            "llm_resposta_final": execucao.latencia_resposta_final_ms,
            "total": execucao.latencia_total_ms,
        },
        "erro": t.erro,
        "avisos": execucao.avisos,
    }
