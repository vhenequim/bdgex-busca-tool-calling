"""Qual lote de validação os scripts desta pasta constroem (variável de ambiente PFC_LOTE).

    PFC_LOTE=1 (padrão)  lote 1: data/lote_validacao/, data/lote_validacao.json, sementes 2026-2029
    PFC_LOTE=2           lote 2: data/lote_validacao_2/, data/lote_validacao_2.json, sementes 2031-2034

O lote 2 é o conjunto de TESTE da v3 (docs/lote_validacao.md, seção 12): mesma receita do lote 1,
outra semente, outros redatores e anotadores, metade do tamanho, e nenhum dos seus textos é lido
durante o desenvolvimento da v3. Os catálogos (BDGEx, IBGE) são os mesmos, em data/lote_validacao/.
"""

from __future__ import annotations

import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
LOTE = os.environ.get("PFC_LOTE", "1").strip() or "1"

if LOTE == "1":
    DIR = RAIZ / "data" / "lote_validacao"
    DATASET = RAIZ / "data" / "lote_validacao.json"
    PREFIXO_ID = ""
    SEMENTES = {"alvos": 2026, "tarefas": 2027, "ids": 2028, "amostra_b": 2029}
    FATOR = 1.0
    N_TAREFAS = 15
    SUFIXO_TEX = ""
    OUTROS_DATASETS: list[Path] = []
else:
    DIR = RAIZ / "data" / f"lote_validacao_{LOTE}"
    DATASET = RAIZ / "data" / f"lote_validacao_{LOTE}.json"
    PREFIXO_ID = "B"
    SEMENTES = {"alvos": 2031, "tarefas": 2032, "ids": 2033, "amostra_b": 2034}
    FATOR = 0.5
    N_TAREFAS = 8
    SUFIXO_TEX = LOTE
    OUTROS_DATASETS = [RAIZ / "data" / "lote_validacao.json"]   # deduplicação também contra o lote 1

DIR_CATALOGOS = RAIZ / "data" / "lote_validacao"
