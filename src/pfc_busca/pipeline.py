"""Pipeline ponta a ponta: consulta → tradução → (SQL) → (resposta final).

`traduzir` é o que se mede; `executar_sql` prova que a arquitetura fecha
(RF3); `resposta_final` é a segunda chamada ao modelo com o resultado da
ferramenta, para a API devolver texto ao usuário (RF1). Na avaliação, a
resposta final fica desligada por padrão: ela dobra o custo e não entra em
métrica alguma.

Três desfechos chegam ao usuário: (1) o modelo recusa a consulta (fora do domínio) e
a resposta é a frase dele, sem busca; (2) a busca devolve produtos, sempre lidos do
banco, e o modelo só os resume; (3) a busca não encontra nada, e a resposta é uma
mensagem fixa com os critérios usados, sem nova chamada ao modelo — nenhum produto
é inventado em nenhum dos casos.

O tradutor é qualquer objeto com `traduzir(consulta, hoje) -> Traducao` (as abordagens de
`pfc_busca.abordagens`: Tool Calling v1 a v3 e Saída Estruturada). A resposta final usa o
modelo de chat do tradutor (`tradutor.llm`); a Saída Estruturada do Ollama não tem um, e a
pipeline cria um `ChatOllama` com a mesma tag; um tradutor sem modelo algum recebe uma
resposta fixa com a contagem. Uma falha na resposta final vira aviso, não erro: a tradução e
a busca já feitas voltam ao usuário.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any, Protocol

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from pfc_busca import agent, db, schema, tools
from pfc_busca.agent import Traducao
from pfc_busca.prompts import montar_system_prompt

MENSAGEM_SEM_RESULTADOS = ("Nenhum produto do acervo atende aos critérios da busca ({criterios}). "
                           "Tente retirar ou ampliar algum dos critérios.")
MENSAGEM_COM_RESULTADOS = "{total} produto(s) do acervo atendem aos critérios da busca ({criterios})."
MENSAGEM_SEM_BUSCA = "Critérios extraídos da consulta: {criterios}. A busca no catálogo não foi executada."


class TradutorDeConsultas(Protocol):
    """O que a pipeline exige de um tradutor (todas as abordagens do registro atendem)."""

    modelo: str

    def traduzir(self, consulta: str, hoje: date) -> Traducao: ...


def _criterios(parametros: dict[str, Any]) -> str:
    partes = []
    for campo, valor in parametros.items():
        if isinstance(valor, dict):
            valor = " a ".join(str(valor[k]) for k in ("start", "end") if valor.get(k))
        partes.append(f"{campo}: {valor}")
    return "; ".join(partes) or "nenhum filtro"


def mensagem_sem_resultados(parametros: dict[str, Any]) -> str:
    """Resposta determinística para busca sem resultado: nada a resumir, nada a inventar."""
    return MENSAGEM_SEM_RESULTADOS.format(criterios=_criterios(parametros))


def mensagem_sem_modelo(parametros: dict[str, Any], busca: tools.ResultadoBusca | None) -> str:
    """Resposta fixa quando o tradutor não tem modelo de chat para resumir o resultado."""
    if busca is not None and busca.executado:
        return MENSAGEM_COM_RESULTADOS.format(total=busca.total, criterios=_criterios(parametros))
    return MENSAGEM_SEM_BUSCA.format(criterios=_criterios(parametros))


@dataclass
class Execucao:
    traducao: Traducao
    busca: tools.ResultadoBusca | None = None
    resposta_final: str | None = None
    latencia_resposta_final_ms: float | None = None
    latencia_total_ms: float | None = None
    avisos: list[str] = field(default_factory=list)

    def para_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if self.busca is not None:
            d["busca"]["itens"] = self.busca.itens[:10]
        return d


class Pipeline:
    def __init__(self, tradutor: TradutorDeConsultas, *, dsn: str | None = db.DSN_PADRAO,
                 executar_sql: bool = True):
        self.tradutor = tradutor
        self.dsn = dsn
        self.executar_sql = executar_sql and dsn is not None and db.disponivel(dsn)
        self.banco_indisponivel = executar_sql and not self.executar_sql
        self._llm_resposta: Any = None

    def buscar(self, consulta: str, hoje: date | None = None, *, resposta_final: bool = False) -> Execucao:
        hoje = hoje or date.today()
        inicio = time.perf_counter()
        traducao = self.tradutor.traduzir(consulta, hoje)
        execucao = Execucao(traducao=traducao)
        if self.banco_indisponivel:
            execucao.avisos.append("banco indisponível: SQL não executada")

        if traducao.predito is not None and self.executar_sql:
            execucao.busca = tools.buscar_catalogo(traducao.predito, self.dsn)

        # houve busca: o Tool Calling chamou buscar_catalogo, ou a Saída Estruturada devolveu parâmetros
        if resposta_final and traducao.predito is not None and traducao.chamou_ferramenta:
            if execucao.busca is not None and execucao.busca.executado and execucao.busca.total == 0:
                execucao.resposta_final = mensagem_sem_resultados(traducao.predito)
                execucao.latencia_resposta_final_ms = 0.0
            else:
                try:
                    execucao.resposta_final, execucao.latencia_resposta_final_ms = self._responder(
                        consulta, hoje, traducao, execucao.busca)
                except Exception as erro:  # noqa: BLE001 — a tradução e a busca já feitas voltam ao usuário
                    execucao.avisos.append(f"resposta final indisponível: {agent._classificar_erro(erro)[1]}")

        execucao.latencia_total_ms = (time.perf_counter() - inicio) * 1000
        return execucao

    def modelo_de_resposta(self) -> Any:
        """Modelo de chat que redige a resposta final: o do tradutor; na SE do Ollama, um ChatOllama com a
        mesma tag; None se o tradutor não tiver modelo (resposta fixa)."""
        if self._llm_resposta is None:
            llm = getattr(self.tradutor, "llm", None)
            tag = getattr(self.tradutor, "tag", None)
            if llm is None and tag:
                from langchain_ollama import ChatOllama

                kwargs: dict[str, Any] = {"reasoning": False} if getattr(self.tradutor, "thinking_desativado",
                                                                         False) else {}
                llm = ChatOllama(model=tag, base_url=getattr(self.tradutor, "base_url", agent.BASE_URL_PADRAO),
                                 temperature=0, num_predict=agent.MAX_TOKENS_SAIDA,
                                 keep_alive=getattr(self.tradutor, "keep_alive", agent.KEEP_ALIVE),
                                 client_kwargs={"timeout": agent.TIMEOUT_S}, **kwargs)
            self._llm_resposta = llm
        return self._llm_resposta

    def _responder(self, consulta: str, hoje: date, traducao: Traducao,
                   busca: tools.ResultadoBusca | None) -> tuple[str, float]:
        llm = self.modelo_de_resposta()
        if llm is None:
            return mensagem_sem_modelo(traducao.predito or {}, busca), 0.0
        # a chamada que o modelo vê no histórico leva os parâmetros de fato buscados (na v3, os da última
        # tentativa aceita; na SE, os do objeto JSON, que não tem chamada)
        chamada = next((c for c in traducao.tool_calls if c.get("name") == schema.NOME_FERRAMENTA and c.get("id")),
                       {})
        id_chamada = chamada.get("id") or "call_1"
        conteudo_ferramenta = (
            {"total": busca.total, "itens": busca.itens[:10]} if busca and busca.executado
            else {"aviso": "busca não executada", "parametros": traducao.predito}
        )
        mensagens = [
            SystemMessage(content=montar_system_prompt(hoje)),
            HumanMessage(content=consulta),
            AIMessage(content="" if not traducao.tool_calls else (traducao.texto_resposta or ""),
                      tool_calls=[{"name": schema.NOME_FERRAMENTA, "args": traducao.predito or {},
                                   "id": id_chamada, "type": "tool_call"}]),
            ToolMessage(content=str(conteudo_ferramenta), tool_call_id=id_chamada),
        ]
        inicio = time.perf_counter()
        resposta = llm.invoke(mensagens)
        return (str(resposta.content).strip(), (time.perf_counter() - inicio) * 1000)
