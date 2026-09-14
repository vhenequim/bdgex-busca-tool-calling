"""Resolução de expressões de tempo relativo do gabarito.

O Apêndice A descreve o gabarito de datas relativas em linguagem
("ano corrente da execução, integral"), porque o intervalo correto depende do
dia em que o experimento roda. Aqui cada descrição vira uma REGRA nomeada;
`resolver(regra, hoje)` devolve `{"start": ..., "end": ...}` em ISO 8601.

A mesma data `hoje` é injetada no prompt de sistema e usada para resolver o
gabarito — sem isso a métrica de datas seria injusta com o modelo.

Convenções (documentadas no Cap. 3 e reportadas no Cap. 5):
- "esse ano" / "ano passado" / "mês passado": períodos de calendário integrais.
- "semana passada": 7 dias corridos anteriores ao dia da execução
  (D-7 .. D-1), conforme o texto do Apêndice A.
- "últimos N meses": N*30 dias corridos até hoje, inclusive (idem Apêndice).
- "depois de AAAA" / "desde AAAA": de AAAA-01-01 até hoje — convenção do
  baseline P21 do protótipo ("depois de 2020" -> 2020-01-01 a data atual).
- "antes de AAAA": só limite superior (AAAA-1)-12-31; sem `start`.
"""

from __future__ import annotations

import calendar
from collections.abc import Callable
from datetime import date, timedelta

Periodo = dict[str, str]


def _fim_de_mes(ano: int, mes: int) -> date:
    return date(ano, mes, calendar.monthrange(ano, mes)[1])


def _menos_anos(d: date, anos: int) -> date:
    try:
        return d.replace(year=d.year - anos)
    except ValueError:  # 29/fev
        return d.replace(year=d.year - anos, day=28)


def _iso(inicio: date | None, fim: date | None) -> Periodo:
    periodo: Periodo = {}
    if inicio is not None:
        periodo["start"] = inicio.isoformat()
    if fim is not None:
        periodo["end"] = fim.isoformat()
    return periodo


def _ano_corrente(h: date) -> Periodo:
    return _iso(date(h.year, 1, 1), date(h.year, 12, 31))


def _ano_anterior(h: date) -> Periodo:
    return _iso(date(h.year - 1, 1, 1), date(h.year - 1, 12, 31))


def _dois_anos_atras(h: date) -> Periodo:
    return _iso(date(h.year - 2, 1, 1), date(h.year - 2, 12, 31))


def _mes_anterior(h: date) -> Periodo:
    ano, mes = (h.year, h.month - 1) if h.month > 1 else (h.year - 1, 12)
    return _iso(date(ano, mes, 1), _fim_de_mes(ano, mes))


def _mes_corrente(h: date) -> Periodo:
    return _iso(date(h.year, h.month, 1), h)


def _semana_passada(h: date) -> Periodo:
    return _iso(h - timedelta(days=7), h - timedelta(days=1))


def _semana_corrente(h: date) -> Periodo:
    return _iso(h - timedelta(days=h.weekday()), h)


def _hoje(h: date) -> Periodo:
    return _iso(h, h)


def _ultimos_dias(n: int) -> Callable[[date], Periodo]:
    return lambda h: _iso(h - timedelta(days=n), h)


def _ultimos_anos(n: int) -> Callable[[date], Periodo]:
    return lambda h: _iso(_menos_anos(h, n), h)


def _desde_ano(ano: int) -> Callable[[date], Periodo]:
    return lambda h: _iso(date(ano, 1, 1), h)


def _antes_de_ano(ano: int) -> Callable[[date], Periodo]:
    return lambda _h: _iso(None, date(ano - 1, 12, 31))


def _primeiro_trimestre_corrente(h: date) -> Periodo:
    return _iso(date(h.year, 1, 1), date(h.year, 3, 31))


def _segundo_semestre_anterior(h: date) -> Periodo:
    return _iso(date(h.year - 1, 7, 1), date(h.year - 1, 12, 31))


def _ultimo_trimestre_ano_anterior(h: date) -> Periodo:
    return _iso(date(h.year - 1, 10, 1), date(h.year - 1, 12, 31))


def _trimestre_anterior(h: date) -> Periodo:
    trimestre_atual = (h.month - 1) // 3  # 0..3
    if trimestre_atual == 0:
        return _iso(date(h.year - 1, 10, 1), date(h.year - 1, 12, 31))
    mes_inicio = (trimestre_atual - 1) * 3 + 1
    return _iso(date(h.year, mes_inicio, 1), _fim_de_mes(h.year, mes_inicio + 2))


REGRAS: dict[str, Callable[[date], Periodo]] = {
    "ano_corrente": _ano_corrente,
    "ano_anterior": _ano_anterior,
    "dois_anos_atras": _dois_anos_atras,
    "mes_anterior": _mes_anterior,
    "mes_corrente": _mes_corrente,
    "semana_passada": _semana_passada,
    "semana_corrente": _semana_corrente,
    "hoje": _hoje,
    "ultimos_90_dias": _ultimos_dias(90),
    "ultimos_180_dias": _ultimos_dias(180),
    "ultimos_5_anos": _ultimos_anos(5),
    "desde_2020": _desde_ano(2020),
    "desde_2022": _desde_ano(2022),
    "antes_de_2020": _antes_de_ano(2020),
    "primeiro_trimestre_corrente": _primeiro_trimestre_corrente,
    "segundo_semestre_anterior": _segundo_semestre_anterior,
    "ultimo_trimestre_ano_anterior": _ultimo_trimestre_ano_anterior,
    "trimestre_anterior": _trimestre_anterior,
}

# Texto do Apêndice A / do gerador -> regra. Chaves em minúsculas, sem espaços
# duplicados. Quem mantém `generate_dataset.py` mantém esta tabela também.
DESCRICAO_PARA_REGRA: dict[str, str] = {
    "ano corrente da execução, integral": "ano_corrente",
    "ano anterior à execução, integral": "ano_anterior",
    "mês anterior à execução, integral": "mes_anterior",
    "7 dias corridos anteriores à execução": "semana_passada",
    "90 dias corridos anteriores à execução": "ultimos_90_dias",
    "180 dias corridos anteriores à execução": "ultimos_180_dias",
    "5 anos anteriores à execução": "ultimos_5_anos",
    "2020-01-01 a data da execução": "desde_2020",
    "2022-01-01 a data da execução": "desde_2022",
    "sem limite inferior a 2019-12-31": "antes_de_2020",
    "1º trimestre do ano da execução": "primeiro_trimestre_corrente",
    "jul--dez do ano anterior": "segundo_semestre_anterior",
    "semana corrente": "semana_corrente",
    "dia da execução": "hoje",
    # descrições das camadas P/N
    "mês corrente da execução": "mes_corrente",
    "2 anos antes, integral": "dois_anos_atras",
    "trimestre anterior integral": "trimestre_anterior",
    "último trimestre do ano anterior": "ultimo_trimestre_ano_anterior",
    "7 dias anteriores à execução": "semana_passada",
    "2020-01-01 a data atual": "desde_2020",
}


def regra_de_descricao(descricao: str) -> str | None:
    return DESCRICAO_PARA_REGRA.get(" ".join(descricao.strip().split()))


def resolver(regra: str, hoje: date) -> Periodo:
    """Intervalo ISO para `regra` no dia `hoje`."""
    try:
        return REGRAS[regra](hoje)
    except KeyError as erro:
        raise KeyError(f"regra de tempo relativo desconhecida: {regra!r}") from erro


def resolver_gabarito(esperado: dict, hoje: date) -> dict:
    """Substitui todo `{"rel": regra}` do gabarito pelo intervalo concreto."""
    resolvido = {}
    for campo, valor in esperado.items():
        if isinstance(valor, dict) and "rel" in valor:
            resolvido[campo] = resolver(valor["rel"], hoje)
        else:
            resolvido[campo] = valor
    return resolvido
