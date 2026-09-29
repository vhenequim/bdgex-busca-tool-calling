"""Gera os dados consultados pelas ferramentas auxiliares da v3 (`src/pfc_busca/ferramentas.py`).

    python scripts/v3/gerar_dados_ferramentas.py

- `src/pfc_busca/dados/municipios_ibge.json` (versionado): [nome, sigla da UF, nome da UF] de cada
  um dos 5.571 municípios da lista oficial do IBGE (dado público).
- `src/pfc_busca/dados/indice_folhas.json` (NÃO versionado; .gitignore): nomes de folha, códigos MI e
  INOM e escalas extraídos dos metadados públicos do BDGEx coletados por
  `scripts/lote_validacao/coletar_bdgex.py`. Fica fora do repositório pelo mesmo motivo da cópia
  bruta (a política do BDGEx não trata de redistribuição); vai no pacote do Colab. Sem ele, as
  ferramentas funcionam e só deixam de conferir a existência de folhas e códigos no acervo.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "scripts" / "lote_validacao"))
import catalogo  # noqa: E402

DADOS = RAIZ / "src" / "pfc_busca" / "dados"


def main() -> int:
    DADOS.mkdir(parents=True, exist_ok=True)
    municipios = sorted({(m["nome"], m["sigla"], m["uf"]) for m in catalogo.carregar_ibge()})
    (DADOS / "municipios_ibge.json").write_text(json.dumps([list(m) for m in municipios], ensure_ascii=False),
                                               encoding="utf-8", newline="\n")
    print(f"{len(municipios)} municípios -> {(DADOS / 'municipios_ibge.json').relative_to(RAIZ)}")
    if not catalogo.DIR_CSW.is_dir():
        print("sem a coleta do BDGEx (data/lote_validacao/bdgex_csw/): índice de folhas não gerado")
        return 0
    registros = catalogo.carregar_bdgex()
    folhas: dict[str, dict] = defaultdict(lambda: {"escalas": set(), "registros": 0})
    mi, inom = defaultdict(int), defaultdict(int)
    for r in registros:
        if r["nome_folha"]:
            f = folhas[r["nome_folha"]]
            f["registros"] += 1
            if r["escala"]:
                f["escalas"].add(r["escala"])
        if r["mi"]:
            mi[r["mi"]] += 1
        if r["inom"]:
            inom[r["inom"]] += 1
    indice = {
        "fonte": "metadados públicos do BDGEx (CSW), coleta de scripts/lote_validacao/coletar_bdgex.py",
        "folhas": {n: {"registros": f["registros"], "escalas": sorted(f["escalas"])} for n, f in sorted(folhas.items())},
        "mi": dict(sorted(mi.items())), "inom": dict(sorted(inom.items())),
    }
    (DADOS / "indice_folhas.json").write_text(json.dumps(indice, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(f"{len(folhas)} folhas, {len(mi)} MI, {len(inom)} INOM -> {(DADOS / 'indice_folhas.json').relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
