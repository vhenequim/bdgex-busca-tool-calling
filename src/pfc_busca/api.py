"""API REST (Cap. 4, "Camada de API"): `POST /api/search` e `GET /api/health`.

    uvicorn pfc_busca.api:app --port 8000                               # abordagem recomendada
    PFC_ABORDAGEM=tool_calling PFC_MODELO_PADRAO=qwen3:4b-instruct-2507-q4_K_M uvicorn pfc_busca.api:app
    pfc api --abordagem saida_estruturada_v3 --porta 8000               # o mesmo, pelo comando único

Configuração (variáveis de ambiente ou `.env`; `pfc abordagens` lista as abordagens):

    PFC_ABORDAGEM          abordagem do registro (`pfc_busca.abordagens`); padrão: tool_calling_v3, a recomendada
    PFC_MODELO_PADRAO      tag do Ollama; padrão: gemma4:e4b-it-qat, o modelo em que a recomendada foi avaliada
    PFC_PERMITIR_MODELO=1  aceita `model` na requisição (só em desenvolvimento, RF4)
    OLLAMA_BASE_URL, PFC_DB_DSN   servidor do Ollama e banco (sem banco, a API só traduz)

Recebe `{"query": "..."}` e devolve os parâmetros extraídos, a sequência de tool calls, os
produtos encontrados (semente sintética) e as latências de cada etapa (RF1, RF2, RF3, RF5).

`/api/health` diz qual configuração está no ar: abordagem, modelo e os hashes de prompt e de
ferramenta (os mesmos do manifesto de cada rodada), com as rodadas de results/ feitas com essa
mesma configuração. Se faltar um dado de que a abordagem depende (na v3, o índice de folhas do
BDGEx, que não é versionado), a API sobe mesmo assim, em modo degradado, e o aviso aparece no
log e no `/api/health`.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from pfc_busca import abordagens, agent, db
from pfc_busca.pipeline import Pipeline

load_dotenv()

log = logging.getLogger("pfc_busca.api")
if not log.hasHandlers():
    # o uvicorn configura só os loggers dele: sem isto, a linha de subida (INFO) não apareceria
    _saida = logging.StreamHandler()
    _saida.setFormatter(logging.Formatter("%(levelname)s:     %(name)s: %(message)s"))
    log.addHandler(_saida)
    log.setLevel(logging.INFO)


@dataclass(frozen=True)
class Configuracao:
    abordagem: str = abordagens.RECOMENDADA
    modelo: str = abordagens.MODELO_RECOMENDADO
    permitir_modelo: bool = False
    base_url: str = agent.BASE_URL_PADRAO
    dsn: str | None = db.DSN_PADRAO
    executar_sql: bool = True

    @classmethod
    def do_ambiente(cls, env: Mapping[str, str] | None = None) -> Configuracao:
        env = os.environ if env is None else env
        return cls(abordagem=(env.get("PFC_ABORDAGEM") or abordagens.RECOMENDADA).strip(),
                   modelo=(env.get("PFC_MODELO_PADRAO") or abordagens.MODELO_RECOMENDADO).strip(),
                   permitir_modelo=env.get("PFC_PERMITIR_MODELO", "0") == "1",
                   base_url=env.get("OLLAMA_BASE_URL") or agent.BASE_URL_PADRAO,
                   dsn=env.get("PFC_DB_DSN") or db.DSN_PADRAO)


class Requisicao(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    model: str | None = None
    resposta_final: bool = True


def criar_app(config: Configuracao | None = None, *, fabrica: Callable[[str], Any] | None = None,
              versao_ollama: Callable[[], str | None] | None = None,
              banco_disponivel: Callable[[], bool] | None = None) -> FastAPI:
    """App com a configuração dada (padrão: a do ambiente).

    `fabrica(modelo) -> tradutor` substitui a do registro (os testes passam um tradutor falso);
    `versao_ollama` e `banco_disponivel` substituem as sondagens do `/api/health`.
    Um nome de abordagem fora do registro impede a subida (`abordagens.AbordagemDesconhecida`).
    """
    config = config or Configuracao.do_ambiente()
    abordagem = abordagens.obter(config.abordagem)
    fabrica = fabrica or (lambda modelo: abordagem.criar(modelo, base_url=config.base_url))
    versao_ollama = versao_ollama or (lambda: agent.versao_servidor(config.base_url))
    banco_disponivel = banco_disponivel or (lambda: config.dsn is not None and db.disponivel(config.dsn))

    avisos = abordagens.avisos(abordagem.nome)
    identidade = abordagens.configuracao(abordagem.nome, config.modelo)
    rodadas = abordagens.rodadas_com_a_mesma_configuracao(abordagem.nome, config.modelo)
    log.info("abordagem %s · modelo %s · configuração %s · rodadas com a mesma configuração: %s",
             abordagem.nome, config.modelo, identidade["sha256"][:12], ", ".join(rodadas) or "nenhuma")
    for aviso in avisos:
        log.warning("modo degradado: %s", aviso)

    app = FastAPI(title="PFC · Busca em linguagem natural no acervo da DSG", version="0.2.0")
    pipelines: dict[str, Pipeline] = {}
    app.state.config, app.state.abordagem, app.state.pipelines = config, abordagem, pipelines

    def pipeline_de(modelo: str) -> Pipeline:
        if modelo not in pipelines:
            pipelines[modelo] = Pipeline(fabrica(modelo), dsn=config.dsn, executar_sql=config.executar_sql)
        return pipelines[modelo]

    @app.get("/api/health")
    def health():
        return {
            "status": "degradada" if avisos else "ok",
            "abordagem": abordagem.nome,
            "familia": abordagem.familia,
            "versao": abordagem.versao,
            "descricao": abordagem.descricao,
            "recomendada": abordagem.recomendada,
            "modelo": config.modelo,
            "modelo_padrao": config.modelo,   # nome anterior do campo, mantido
            "selecao_de_modelo_por_requisicao": config.permitir_modelo,
            "configuracao": {"sha256": identidade["sha256"], "prompt_sha256": identidade["prompt_sha256"],
                             "ferramenta_sha256": identidade["ferramenta_sha256"],
                             "rodadas_com_a_mesma_configuracao": rodadas},
            "dados_ferramentas": abordagens.estado_dos_dados(abordagem.nome),
            "degradada": bool(avisos),
            "avisos": avisos,
            "ollama": versao_ollama(),
            "banco": banco_disponivel(),
        }

    @app.post("/api/search")
    def search(req: Requisicao):
        modelo = config.modelo
        if req.model and req.model != config.modelo:
            if not config.permitir_modelo:
                raise HTTPException(403, "seleção de modelo por requisição é restrita ao ambiente de desenvolvimento")
            modelo = req.model
        try:
            pipeline = pipeline_de(modelo)
        except agent.ModeloIndisponivel as erro:
            raise HTTPException(503, str(erro)) from erro

        execucao = pipeline.buscar(req.query, date.today(), resposta_final=req.resposta_final)
        t = execucao.traducao
        return {
            "consulta": req.query,
            "abordagem": abordagem.nome,
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
            "extras": t.extras,
            "avisos": avisos + execucao.avisos,
        }

    return app


app = criar_app()
