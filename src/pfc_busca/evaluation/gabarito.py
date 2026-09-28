"""Representação do gabarito com leituras múltiplas (manual de anotação, princípio P3).

Um caso do dataset tem:

    "esperado":     leitura preferencial — {campo: valor}
    "trocas":       leituras estruturais alternativas, como pares [campo_origem, campo_destino]
                    (ex.: ["state", "city"]: o mesmo valor aceito em `city`)
    "alternativas": as leituras alternativas já expandidas a partir de `trocas`

Dentro de qualquer leitura, o valor de um campo pode ser:

    "1:25.000"                          valor único
    {"$um_de": ["a", "b"]}              qualquer um dos valores (valor alternativo)
    {"$opcional": 1}                    pode faltar; se presente, deve valer 1
    {"rel": "semana_passada"}           período relativo — resolvido na execução
    {"start": "...", "end": "..."}      período absoluto

`resolver_gabarito` transforma regras relativas em períodos concretos (com todas
as leituras aceitas da regra) para uma data de referência.
"""

from __future__ import annotations

from datetime import date
from itertools import combinations
from typing import Any

from pfc_busca.evaluation import relative_time

UM_DE = "$um_de"
OPCIONAL = "$opcional"


def um_de(*valores: Any) -> dict:
    return {UM_DE: list(valores)}


def opcional(valor: Any) -> dict:
    return {OPCIONAL: valor}


def rel(regra: str) -> dict:
    return {"rel": regra}


def periodo(start: str | None = None, end: str | None = None) -> dict:
    p: dict[str, str] = {}
    if start:
        p["start"] = start
    if end:
        p["end"] = end
    return p


def eh_um_de(v: Any) -> bool:
    return isinstance(v, dict) and UM_DE in v


def eh_opcional(v: Any) -> bool:
    return isinstance(v, dict) and OPCIONAL in v


def eh_rel(v: Any) -> bool:
    return isinstance(v, dict) and "rel" in v


def valores_aceitos(v: Any) -> list[Any]:
    """Lista plana dos valores aceitos para um campo (desembrulha $opcional/$um_de)."""
    if eh_opcional(v):
        return valores_aceitos(v[OPCIONAL])
    if eh_um_de(v):
        saida: list[Any] = []
        for x in v[UM_DE]:
            saida.extend(valores_aceitos(x))
        return saida
    return [v]


def valor_preferencial(v: Any) -> Any:
    if eh_opcional(v):
        return valor_preferencial(v[OPCIONAL])
    if eh_um_de(v):
        return valor_preferencial(v[UM_DE][0])
    return v


# ---------------------------------------------------------------------------
# Expansão das trocas estruturais
# ---------------------------------------------------------------------------

def expandir_trocas(esperado: dict, trocas: list[list[str]] | list[tuple[str, str]]) -> list[dict]:
    """Todas as leituras alternativas geradas por subconjuntos não vazios de `trocas`."""
    alternativas: list[dict] = []
    trocas = [tuple(t) for t in trocas]
    for k in range(1, len(trocas) + 1):
        for subconjunto in combinations(trocas, k):
            leitura = dict(esperado)
            valido = True
            for origem, destino in subconjunto:
                if origem not in leitura or destino in leitura:
                    valido = False
                    break
                leitura[destino] = leitura.pop(origem)
            if valido and leitura not in alternativas and leitura != esperado:
                alternativas.append(leitura)
    return alternativas


# ---------------------------------------------------------------------------
# Resolução para uma data de referência
# ---------------------------------------------------------------------------

def _resolver_valor(v: Any, hoje: date) -> Any:
    if eh_opcional(v):
        return {OPCIONAL: _resolver_valor(v[OPCIONAL], hoje)}
    if eh_um_de(v):
        return {UM_DE: [_resolver_valor(x, hoje) for x in v[UM_DE]]}
    if eh_rel(v):
        leituras = relative_time.leituras(v["rel"], hoje)
        return leituras[0] if len(leituras) == 1 else {UM_DE: leituras}
    return v


def resolver_gabarito(esperado: dict, hoje: date) -> dict:
    """Substitui toda regra relativa pelo(s) intervalo(s) concreto(s) de `hoje`."""
    return {campo: _resolver_valor(valor, hoje) for campo, valor in esperado.items()}


def resolver_leituras(caso: dict, hoje: date) -> list[dict]:
    """Leitura preferencial + alternativas, resolvidas para `hoje`."""
    leituras = [caso.get("esperado", {})] + list(caso.get("alternativas", []))
    return [resolver_gabarito(leitura, hoje) for leitura in leituras]


# ---------------------------------------------------------------------------
# Formatação legível (Apêndice A e relatórios)
# ---------------------------------------------------------------------------

def _fmt_periodo(p: dict) -> str:
    if "start" in p and "end" in p:
        return f"{p['start']} a {p['end']}"
    if "start" in p:
        return f"a partir de {p['start']}"
    if "end" in p:
        return f"até {p['end']}"
    return "(vazio)"


def formatar_valor(v: Any) -> str:
    if eh_opcional(v):
        return f"{formatar_valor(v[OPCIONAL])} (opcional)"
    if eh_um_de(v):
        return " ou ".join(formatar_valor(x) for x in v[UM_DE])
    if eh_rel(v):
        return relative_time.texto_regra(v["rel"])
    if isinstance(v, dict):
        return _fmt_periodo(v)
    if isinstance(v, str):
        return f'"{v}"'
    return str(v)


def formatar_leitura(leitura: dict) -> list[str]:
    return [f"{campo}: {formatar_valor(valor)}" for campo, valor in leitura.items()]
