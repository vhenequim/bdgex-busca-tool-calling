"""Conexão com o PostgreSQL/PostGIS (camada de persistência, Cap. 4).

O banco tem o MESMO esquema do protótipo (`db/init_schema_prototipo.sql`).
Os dados são uma semente sintética rotulada (`db/seed_sintetico.sql`) — servem
apenas para demonstrar que a arquitetura fecha ponta a ponta; nenhuma métrica
do PFC depende deles.
"""

from __future__ import annotations

import os

import psycopg

DSN_PADRAO = os.environ.get("PFC_DB_DSN", "postgresql://postgres:pfc@localhost:5433/geospatial_search")


def conectar(dsn: str = DSN_PADRAO, timeout_s: int = 5) -> psycopg.Connection:
    return psycopg.connect(dsn, connect_timeout=timeout_s, autocommit=True)


def disponivel(dsn: str = DSN_PADRAO) -> bool:
    try:
        with conectar(dsn, timeout_s=2) as conexao, conexao.cursor() as cur:
            cur.execute("SELECT 1")
            return True
    except psycopg.Error:
        return False


def resumo(dsn: str = DSN_PADRAO) -> dict[str, int]:
    """Contagem por tabela — para o cabeçalho dos relatórios."""
    with conectar(dsn) as conexao, conexao.cursor() as cur:
        saida = {}
        for tabela in ("datasets", "estados", "municipios", "areas_suprimento"):
            cur.execute(f"SELECT COUNT(*) FROM {tabela}")
            saida[tabela] = cur.fetchone()[0]
        return saida
