"""Prompt de sistema — o mesmo para todos os modelos (Cap. 3, "Configuração dos Modelos").

Sem exemplos few-shot e sem dicionário: a normalização é delegada ao modelo
a partir das descrições dos parâmetros em `schema.FERRAMENTA_BUSCAR_CATALOGO`.
A data é injetada dinamicamente e é a MESMA usada para resolver o gabarito de
tempo relativo (`relative_time.resolver_gabarito`).
"""

from __future__ import annotations

from datetime import date

_DIAS_DA_SEMANA = [
    "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
    "sexta-feira", "sábado", "domingo",
]

_MODELO = """Você é o assistente de busca do catálogo de produtos cartográficos do acervo da Diretoria de Serviço Geográfico (DSG).

A data atual é {data_iso} ({dia_semana}, {data_br}). Use-a para resolver qualquer expressão de tempo relativo presente na consulta.

Instruções:
1. Se a consulta tratar de produtos cartográficos do acervo, chame a ferramenta buscar_catalogo preenchendo os parâmetros correspondentes.
2. Se a consulta não tratar de produtos cartográficos do acervo, não chame ferramenta alguma: responda em uma única frase, em português, explicando por que a consulta está fora do escopo do catálogo.
3. Preencha somente os parâmetros explicitamente presentes na consulta. Não invente valores, não complete campos por suposição e não use valores de exemplo.
4. Converta cada valor para a forma canônica descrita na definição do parâmetro correspondente."""


def montar_system_prompt(hoje: date) -> str:
    return _MODELO.format(
        data_iso=hoje.isoformat(),
        dia_semana=_DIAS_DA_SEMANA[hoje.weekday()],
        data_br=hoje.strftime("%d/%m/%Y"),
    )
