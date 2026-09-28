"""Expressões de tempo relativo: regras nomeadas e suas leituras aceitas.

O intervalo correto de "semana passada" depende do dia em que o experimento roda.
Por isso o gabarito guarda o nome de uma REGRA (`{"rel": "semana_passada"}`), e o
intervalo concreto é resolvido na execução com a MESMA data de referência que é
informada ao modelo no prompt de sistema.

Cada regra devolve uma lista de leituras aceitas (a primeira é a preferencial),
exatamente como na tabela do manual de anotação (`docs/manual_de_anotacao.md`,
seção `publicationPeriod`). Expressões com mais de uma leitura razoável — "últimos
3 meses" como 90 dias ou como três meses de calendário — aceitam todas; expressões
inequívocas ("ano passado") têm uma só.
"""

from __future__ import annotations

import calendar
import re
from collections.abc import Callable
from datetime import date, timedelta

Periodo = dict[str, str]


# ---------------------------------------------------------------------------
# Aritmética de datas
# ---------------------------------------------------------------------------

def _fim_de_mes(ano: int, mes: int) -> date:
    return date(ano, mes, calendar.monthrange(ano, mes)[1])


def _menos_anos(d: date, anos: int) -> date:
    try:
        return d.replace(year=d.year - anos)
    except ValueError:  # 29/fev
        return d.replace(year=d.year - anos, day=28)


def _menos_meses(d: date, meses: int) -> date:
    total = d.year * 12 + (d.month - 1) - meses
    ano, mes = divmod(total, 12)
    mes += 1
    return date(ano, mes, min(d.day, calendar.monthrange(ano, mes)[1]))


def _p(inicio: date | None, fim: date | None) -> Periodo:
    periodo: Periodo = {}
    if inicio is not None:
        periodo["start"] = inicio.isoformat()
    if fim is not None:
        periodo["end"] = fim.isoformat()
    return periodo


def _segunda(d: date) -> date:
    return d - timedelta(days=d.weekday())


# ---------------------------------------------------------------------------
# Regras (cada uma devolve as leituras aceitas; a primeira é a preferencial)
# ---------------------------------------------------------------------------

def _ano_corrente(h: date) -> list[Periodo]:
    return [_p(date(h.year, 1, 1), date(h.year, 12, 31)), _p(date(h.year, 1, 1), h)]


def _ano_anterior(h: date) -> list[Periodo]:
    return [_p(date(h.year - 1, 1, 1), date(h.year - 1, 12, 31))]


def _dois_anos_atras(h: date) -> list[Periodo]:
    return [_p(date(h.year - 2, 1, 1), date(h.year - 2, 12, 31)), _p(_menos_anos(h, 2), h)]


def _mes_anterior(h: date) -> list[Periodo]:
    ano, mes = (h.year, h.month - 1) if h.month > 1 else (h.year - 1, 12)
    return [_p(date(ano, mes, 1), _fim_de_mes(ano, mes))]


def _mes_corrente(h: date) -> list[Periodo]:
    return [_p(date(h.year, h.month, 1), h), _p(date(h.year, h.month, 1), _fim_de_mes(h.year, h.month))]


def _semana_passada(h: date) -> list[Periodo]:
    seg_anterior = _segunda(h) - timedelta(days=7)
    return [_p(h - timedelta(days=7), h - timedelta(days=1)),
            _p(h - timedelta(days=7), h),
            _p(seg_anterior, seg_anterior + timedelta(days=6))]


def _semana_corrente(h: date) -> list[Periodo]:
    seg = _segunda(h)
    return [_p(seg, h), _p(seg, seg + timedelta(days=6))]


def _hoje(h: date) -> list[Periodo]:
    return [_p(h, h)]


def _ultimos_meses(n: int) -> Callable[[date], list[Periodo]]:
    return lambda h: [_p(h - timedelta(days=30 * n), h), _p(_menos_meses(h, n), h)]


def _ultimos_anos(n: int) -> Callable[[date], list[Periodo]]:
    return lambda h: [_p(_menos_anos(h, n), h), _p(date(h.year - n, 1, 1), h)]


def _desde(ano: int) -> Callable[[date], list[Periodo]]:
    return lambda h: [_p(date(ano, 1, 1), h), _p(date(ano, 1, 1), None)]


def _depois_de(ano: int) -> Callable[[date], list[Periodo]]:
    return lambda h: [_p(date(ano, 1, 1), h), _p(date(ano, 1, 1), None),
                      _p(date(ano + 1, 1, 1), h), _p(date(ano + 1, 1, 1), None)]


def _antes_de(ano: int) -> Callable[[date], list[Periodo]]:
    return lambda _h: [_p(None, date(ano - 1, 12, 31))]


def _primeiro_trimestre_corrente(h: date) -> list[Periodo]:
    return [_p(date(h.year, 1, 1), date(h.year, 3, 31))]


def _segundo_semestre_anterior(h: date) -> list[Periodo]:
    return [_p(date(h.year - 1, 7, 1), date(h.year - 1, 12, 31))]


def _ultimo_trimestre_ano_anterior(h: date) -> list[Periodo]:
    return [_p(date(h.year - 1, 10, 1), date(h.year - 1, 12, 31))]


def _trimestre_anterior(h: date) -> list[Periodo]:
    trimestre_atual = (h.month - 1) // 3  # 0..3
    if trimestre_atual == 0:
        return [_p(date(h.year - 1, 10, 1), date(h.year - 1, 12, 31))]
    mes_inicio = (trimestre_atual - 1) * 3 + 1
    return [_p(date(h.year, mes_inicio, 1), _fim_de_mes(h.year, mes_inicio + 2))]


REGRAS: dict[str, Callable[[date], list[Periodo]]] = {
    "ano_corrente": _ano_corrente,
    "ano_anterior": _ano_anterior,
    "dois_anos_atras": _dois_anos_atras,
    "mes_anterior": _mes_anterior,
    "mes_corrente": _mes_corrente,
    "semana_passada": _semana_passada,
    "semana_corrente": _semana_corrente,
    "hoje": _hoje,
    "ultimos_3_meses": _ultimos_meses(3),
    "ultimos_6_meses": _ultimos_meses(6),
    "ultimos_5_anos": _ultimos_anos(5),
    "desde_2020": _desde(2020),
    "depois_de_2020": _depois_de(2020),
    "depois_de_2022": _depois_de(2022),
    "antes_de_2020": _antes_de(2020),
    "primeiro_trimestre_corrente": _primeiro_trimestre_corrente,
    "segundo_semestre_anterior": _segundo_semestre_anterior,
    "ultimo_trimestre_ano_anterior": _ultimo_trimestre_ano_anterior,
    "trimestre_anterior": _trimestre_anterior,
}

# Texto exibido no Apêndice A e nos relatórios.
TEXTO_REGRA: dict[str, str] = {
    "ano_corrente": "ano corrente",
    "ano_anterior": "ano anterior, inteiro",
    "dois_anos_atras": "ano de dois anos antes",
    "mes_anterior": "mês anterior, inteiro",
    "mes_corrente": "mês corrente",
    "semana_passada": "semana passada",
    "semana_corrente": "semana corrente",
    "hoje": "dia da execução",
    "ultimos_3_meses": "últimos 3 meses",
    "ultimos_6_meses": "últimos 6 meses",
    "ultimos_5_anos": "últimos 5 anos",
    "desde_2020": "desde 2020",
    "depois_de_2020": "depois de 2020",
    "depois_de_2022": "depois de 2022",
    "antes_de_2020": "antes de 2020",
    "primeiro_trimestre_corrente": "1º trimestre do ano corrente",
    "segundo_semestre_anterior": "2º semestre do ano anterior",
    "ultimo_trimestre_ano_anterior": "4º trimestre do ano anterior",
    "trimestre_anterior": "trimestre anterior",
}


def _ultimos_dias(n: int) -> Callable[[date], list[Periodo]]:
    return lambda h: [_p(h - timedelta(days=n), h), _p(h - timedelta(days=n - 1), h)]


# Regras parametrizadas (lote de validação): o mesmo padrão de leituras da tabela do manual,
# para qualquer quantidade ou ano — "últimos 12 meses", "desde 2015", "antes de 2010".
PARAMETRIZADAS: list[tuple[re.Pattern, Callable[..., Callable[[date], list[Periodo]]], str]] = [
    (re.compile(r"^ultimos_(\d+)_meses$"), lambda n: _ultimos_meses(int(n)), "últimos {} meses"),
    (re.compile(r"^ultimos_(\d+)_anos$"), lambda n: _ultimos_anos(int(n)), "últimos {} anos"),
    (re.compile(r"^ultimos_(\d+)_dias$"), lambda n: _ultimos_dias(int(n)), "últimos {} dias"),
    (re.compile(r"^desde_(\d{4})$"), lambda a: _desde(int(a)), "desde {}"),
    (re.compile(r"^depois_de_(\d{4})$"), lambda a: _depois_de(int(a)), "depois de {}"),
    (re.compile(r"^antes_de_(\d{4})$"), lambda a: _antes_de(int(a)), "antes de {}"),
]


def _regra(regra: str) -> Callable[[date], list[Periodo]]:
    if regra in REGRAS:
        return REGRAS[regra]
    for padrao, fabrica, _texto in PARAMETRIZADAS:
        m = padrao.match(regra)
        if m:
            return fabrica(m.group(1))
    raise KeyError(f"regra de tempo relativo desconhecida: {regra!r}")


def texto_regra(regra: str) -> str:
    if regra in TEXTO_REGRA:
        return TEXTO_REGRA[regra]
    for padrao, _fabrica, texto in PARAMETRIZADAS:
        m = padrao.match(regra)
        if m:
            return texto.format(m.group(1))
    return regra


def existe(regra: str) -> bool:
    try:
        _regra(regra)
    except KeyError:
        return False
    return True


def leituras(regra: str, hoje: date) -> list[Periodo]:
    """Todas as leituras aceitas de `regra` no dia `hoje` (sem repetição, preferencial primeiro)."""
    brutas = _regra(regra)(hoje)
    unicas: list[Periodo] = []
    for p in brutas:
        if p not in unicas:
            unicas.append(p)
    return unicas


def resolver(regra: str, hoje: date) -> Periodo:
    """Leitura preferencial de `regra` no dia `hoje`."""
    return leituras(regra, hoje)[0]
