"""Ferramenta `buscar_catalogo`: executa no PostGIS os parâmetros extraídos pelo modelo.

Porte da SQL de `backend/src/services/search.ts` do protótipo, com mudanças
limitadas à sintaxe do driver (pg-promise → psycopg). A lógica dos filtros
(full-text + MI/INOM por regex, filtros exatos, períodos, interseções
espaciais com estados/municípios/áreas de suprimento) é a mesma.

O modelo NUNCA escreve SQL: ele preenche parâmetros; esta função monta a
consulta parametrizada. Um estado inventado pelo modelo aparece na métrica de
parâmetros (falso positivo em `state`), não escondido aqui.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import psycopg

from pfc_busca import db

LIMITE_PADRAO = 10

_SQL_CAMPOS = """
    SELECT nome AS name, mi, inom, escala AS scale, tipo_produto AS "productType",
           projeto AS project, data_publicacao AS "publicationDate",
           data_criacao AS "creationDate", ST_AsGeoJSON(geom)::json AS geometry
      FROM datasets
"""

_REGEX_MI = r"^([0-9]{1,4}-[1-4]-(NO|NE|SO|SE)|[0-9]{1,4}-[1-4]|[0-9]{1,4}|[0-9]{1,3})$"
_REGEX_INOM = r"^[A-Z]{2}-[0-9]{2}(-[A-Z]-[A-Z](-[IVX]{1,6}(-[1-4](-[NS][EO])?)?)?)?$"


@dataclass
class ResultadoBusca:
    executado: bool
    total: int = 0
    itens: list[dict[str, Any]] = field(default_factory=list)
    sql: str = ""
    latencia_ms: float | None = None
    erro: str | None = None


def montar_sql(params: dict[str, Any]) -> tuple[str, str, list[Any]]:
    """Devolve (sql_contagem, sql_principal, argumentos) para os parâmetros dados."""
    condicoes: list[str] = []
    args: list[Any] = []

    keyword = params.get("keyword")
    if keyword:
        condicoes.append(f"""(
            texto_busca @@ websearch_to_tsquery('portuguese', %s)
            OR CASE
                WHEN %s ~ '{_REGEX_MI}' THEN mi = %s
                WHEN %s ~ '{_REGEX_INOM}' THEN inom = %s
                ELSE lower(nome) LIKE lower(%s)
            END
        )""")
        args += [keyword, keyword, keyword, keyword, keyword, f"%{keyword}%"]

    for campo, coluna in (("scale", "escala"), ("productType", "tipo_produto"), ("project", "projeto")):
        if params.get(campo):
            condicoes.append(f"{coluna} = %s")
            args.append(params[campo])

    for campo, coluna in (("publicationPeriod", "data_publicacao"), ("creationPeriod", "data_criacao")):
        periodo = params.get(campo)
        if isinstance(periodo, dict) and periodo:
            if periodo.get("start") and periodo.get("end"):
                condicoes.append(f"date_trunc('day', {coluna}) BETWEEN date_trunc('day', %s::timestamp) "
                                 f"AND date_trunc('day', %s::timestamp)")
                args += [periodo["start"], periodo["end"]]
            elif periodo.get("start"):
                condicoes.append(f"date_trunc('day', {coluna}) >= date_trunc('day', %s::timestamp)")
                args.append(periodo["start"])
            elif periodo.get("end"):
                condicoes.append(f"date_trunc('day', {coluna}) <= date_trunc('day', %s::timestamp)")
                args.append(periodo["end"])

    if params.get("city"):
        condicoes.append("""EXISTS (SELECT 1 FROM municipios m
            WHERE unaccent(lower(m.nome)) ILIKE unaccent(lower(%s))
              AND ST_Intersects(datasets.geom, m.geom))""")
        args.append(f"%{params['city']}%")

    if params.get("state"):
        condicoes.append("""EXISTS (SELECT 1 FROM estados e
            WHERE unaccent(lower(e.nome)) ILIKE unaccent(lower(%s))
              AND ST_Intersects(datasets.geom, e.geom))""")
        args.append(f"%{params['state']}%")

    if params.get("supplyArea"):
        condicoes.append("""EXISTS (SELECT 1 FROM areas_suprimento a
            WHERE a.nome = %s AND ST_Intersects(datasets.geom, a.geom))""")
        args.append(params["supplyArea"])

    where = ("WHERE " + " AND ".join(condicoes)) if condicoes else ""
    coluna_ordem = "data_criacao" if params.get("sortField") == "creationDate" else "data_publicacao"
    direcao = "ASC" if str(params.get("sortDirection", "DESC")).upper() == "ASC" else "DESC"
    limite = params.get("limit") if isinstance(params.get("limit"), int) and params.get("limit") > 0 else LIMITE_PADRAO
    limite = min(limite, 100)

    sql_contagem = f"SELECT COUNT(*)::integer AS total FROM datasets {where}"
    sql_principal = f"{_SQL_CAMPOS} {where} ORDER BY {coluna_ordem} {direcao} LIMIT {limite}"
    return sql_contagem, sql_principal, args


def buscar_catalogo(params: dict[str, Any], dsn: str = db.DSN_PADRAO) -> ResultadoBusca:
    """Executa a busca; nunca levanta exceção (erro vira campo do resultado)."""
    sql_contagem, sql_principal, args = montar_sql(params)
    resultado = ResultadoBusca(executado=False, sql=sql_principal)
    inicio = time.perf_counter()
    try:
        with db.conectar(dsn) as conexao, conexao.cursor() as cur:
            cur.execute(sql_contagem, args)
            resultado.total = cur.fetchone()[0]
            cur.execute(sql_principal, args)
            colunas = [d.name for d in cur.description]
            resultado.itens = [dict(zip(colunas, linha, strict=True)) for linha in cur.fetchall()]
            for item in resultado.itens:
                for chave in ("publicationDate", "creationDate"):
                    if item.get(chave) is not None:
                        item[chave] = item[chave].isoformat()
        resultado.executado = True
    except psycopg.Error as erro:
        resultado.erro = f"{type(erro).__name__}: {str(erro).strip()[:200]}"
    resultado.latencia_ms = (time.perf_counter() - inicio) * 1000
    return resultado
