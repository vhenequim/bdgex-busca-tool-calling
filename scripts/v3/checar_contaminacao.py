"""Contaminação: algum exemplo das descrições, ferramentas ou prompts da v3 aparece no conjunto de teste?

    python scripts/v3/checar_contaminacao.py

Extrai todos os trechos entre aspas simples das descrições da v3 (`v3.DESCRICOES_V3`, as definições das
ferramentas) e dos prompts, normaliza e procura cada um nas consultas do lote 2 (teste),
do lote 1 e das 310. Imprime SÓ contagens — nenhuma consulta do lote 2 é mostrada, para não expor o
conjunto de teste a quem desenvolve. Um exemplo que coincide com uma consulta de teste daria a resposta
ao modelo; a análise do lote 1 encontrou exatamente isso na v2 ('sf22yd' = consulta N35 das 310).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

from pfc_busca import v2, v3  # noqa: E402
from pfc_busca.ferramentas import norm  # noqa: E402

GENERICOS = {"carta", "cartas", "folha", "folhas", "mapa", "mapas", "produtos", "sul", "nordeste", "estado", "cidade",
             "municipio", "regiao", "topo", "orto", "mdt", "mds", "circ", "vetorial", "tematica", "detalhada"}


def exemplos() -> set[str]:
    textos = list(v3.DESCRICOES_V3.values()) + [json.dumps(f, ensure_ascii=False) for f in v3.ferramentas_da(
        "tool_calling_v3")] + [v2.FERRAMENTA_RECUSAR["function"]["description"], v3._TC_SIMPLES, v3._TC_FERRAMENTAS,
                                 v3._SE_V3]
    achados = set()
    for t in textos:
        for trecho in re.findall(r"'([^']{3,80})'", t):
            n = norm(trecho)
            if n and n not in GENERICOS and len(n) >= 4:
                achados.add(n)
    return achados


def main() -> int:
    conjuntos = {"lote 2 (teste)": RAIZ / "data" / "lote_validacao_2.json", "lote 1": RAIZ / "data" / "lote_validacao.json",
                 "310": RAIZ / "data" / "dataset.json"}
    ex = sorted(exemplos())
    print(f"{len(ex)} exemplos extraídos das descrições, ferramentas e prompts da v3")
    for nome, arq in conjuntos.items():
        consultas = [norm(c["consulta"]) for c in json.loads(arq.read_text(encoding="utf-8"))["casos"]]
        literais = [e for e in ex if any(e == q for q in consultas)]
        contidos = {e: sum(f" {e} " in f" {q} " for q in consultas) for e in ex}
        contidos = {e: n for e, n in contidos.items() if n}
        print(f"\n{nome}: {len(consultas)} consultas; exemplos idênticos a uma consulta inteira: {len(literais)}; "
              f"exemplos contidos em alguma consulta: {len(contidos)}")
        if nome == "lote 2 (teste)":
            for e, n in sorted(contidos.items(), key=lambda x: -x[1]):
                print(f"   {n:3d} consulta(s) contêm o exemplo {e!r}")
        else:
            for e, n in sorted(contidos.items(), key=lambda x: -x[1])[:15]:
                print(f"   {n:3d} × {e!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
