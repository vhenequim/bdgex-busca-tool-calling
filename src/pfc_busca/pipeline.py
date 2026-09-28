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
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from pfc_busca import db, schema, tools
from pfc_busca.agent import Traducao, Tradutor
from pfc_busca.prompts import montar_system_prompt

MENSAGEM_SEM_RESULTADOS = ("Nenhum produto do acervo atende aos critérios da busca ({criterios}). "
                           "Tente retirar ou ampliar algum dos critérios.")


def mensagem_sem_resultados(parametros: dict[str, Any]) -> str:
    """Resposta determinística para busca sem resultado: nada a resumir, nada a inventar."""
    partes = []
    for campo, valor in parametros.items():
        if isinstance(valor, dict):
            valor = " a ".join(str(valor[k]) for k in ("start", "end") if valor.get(k))
        partes.append(f"{campo}: {valor}")
    return MENSAGEM_SEM_RESULTADOS.format(criterios="; ".join(partes) or "nenhum filtro")


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
    def __init__(self, tradutor: Tradutor, *, dsn: str | None = db.DSN_PADRAO,
                 executar_sql: bool = True):
        self.tradutor = tradutor
        self.dsn = dsn
        self.executar_sql = executar_sql and dsn is not None and db.disponivel(dsn)
        self.banco_indisponivel = executar_sql and not self.executar_sql

    def buscar(self, consulta: str, hoje: date | None = None, *, resposta_final: bool = False) -> Execucao:
        hoje = hoje or date.today()
        inicio = time.perf_counter()
        traducao = self.tradutor.traduzir(consulta, hoje)
        execucao = Execucao(traducao=traducao)
        if self.banco_indisponivel:
            execucao.avisos.append("banco indisponível: SQL não executada")

        if traducao.predito is not None and self.executar_sql:
            execucao.busca = tools.buscar_catalogo(traducao.predito, self.dsn)

        if resposta_final and traducao.predito is not None and traducao.tool_calls:
            if execucao.busca is not None and execucao.busca.executado and execucao.busca.total == 0:
                execucao.resposta_final = mensagem_sem_resultados(traducao.predito)
                execucao.latencia_resposta_final_ms = 0.0
            else:
                execucao.resposta_final, execucao.latencia_resposta_final_ms = self._responder(
                    consulta, hoje, traducao, execucao.busca)

        execucao.latencia_total_ms = (time.perf_counter() - inicio) * 1000
        return execucao

    def _responder(self, consulta: str, hoje: date, traducao: Traducao,
                   busca: tools.ResultadoBusca | None) -> tuple[str, float]:
        chamada = next(c for c in traducao.tool_calls if c.get("name") == schema.NOME_FERRAMENTA)
        conteudo_ferramenta = (
            {"total": busca.total, "itens": busca.itens[:10]} if busca and busca.executado
            else {"aviso": "busca não executada", "parametros": traducao.predito}
        )
        mensagens = [
            SystemMessage(content=montar_system_prompt(hoje)),
            HumanMessage(content=consulta),
            AIMessage(content=traducao.texto_resposta or "",
                      tool_calls=[{"name": chamada["name"], "args": chamada["args"] or {},
                                   "id": chamada.get("id") or "call_1", "type": "tool_call"}]),
            ToolMessage(content=str(conteudo_ferramenta), tool_call_id=chamada.get("id") or "call_1"),
        ]
        inicio = time.perf_counter()
        resposta = self.tradutor.llm.invoke(mensagens)
        return (str(resposta.content).strip(), (time.perf_counter() - inicio) * 1000)
