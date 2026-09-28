"""Coleta os metadados públicos do catálogo do BDGEx pelo serviço CSW (OGC CSW 2.0.2).

    python scripts/lote_validacao/coletar_bdgex.py [--saida data/lote_validacao/bdgex_csw]

O serviço https://bdgex.eb.mil.br/csw é público: o GetCapabilities declara "None" em taxas
e restrições de acesso, e a política de acesso do BDGEx permite a qualquer visitante, sem
cadastro, pesquisar e visualizar os metadados (o download dos produtos é que exige
cadastro). Só metadados são lidos; nenhum produto é baixado.

A cópia bruta NÃO é versionada no repositório (a política não trata de redistribuição):
fica em `data/lote_validacao/bdgex_csw/` (ignorada pelo git), e o repositório guarda este
script, o resumo `data/lote_validacao/bdgex_resumo.json` (data da coleta, número de
registros, hash de cada página e distribuições agregadas) e os valores usados nos alvos
do lote de validação, que são códigos públicos de articulação de folhas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
URL = ("https://bdgex.eb.mil.br/csw?service=CSW&version=2.0.2&request=GetRecords&typeNames=csw:Record"
       "&elementSetName=full&resultType=results&outputFormat=application/json"
       "&maxRecords={n}&startPosition={inicio}")
POR_PAGINA = 10000


def baixar(inicio: int, n: int) -> bytes:
    pedido = urllib.request.Request(URL.format(n=n, inicio=inicio), headers={"User-Agent": "pfc-busca/lote-validacao"})
    with urllib.request.urlopen(pedido, timeout=600) as resposta:
        return resposta.read()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--saida", type=Path, default=RAIZ / "data" / "lote_validacao" / "bdgex_csw")
    args = p.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)
    inicio, paginas, total = 1, [], None
    while total is None or inicio <= total:
        bruto = baixar(inicio, POR_PAGINA)
        resultado = json.loads(bruto)["csw:GetRecordsResponse"]["csw:SearchResults"]
        total = int(resultado["@numberOfRecordsMatched"])
        devolvidos = int(resultado["@numberOfRecordsReturned"])
        arquivo = args.saida / f"pagina_{len(paginas) + 1:02d}.json"
        arquivo.write_bytes(bruto)
        paginas.append({"arquivo": arquivo.name, "inicio": inicio, "registros": devolvidos,
                        "sha256": hashlib.sha256(bruto).hexdigest()})
        print(f"{arquivo.name}: {devolvidos} registros (de {total})")
        if not devolvidos:
            break
        inicio += devolvidos
        time.sleep(2)   # gentileza com o servidor
    (args.saida / "coleta.json").write_text(json.dumps({
        "servico": "https://bdgex.eb.mil.br/csw", "coletado_em": datetime.now(UTC).isoformat(timespec="seconds"),
        "registros_no_catalogo": total, "paginas": paginas}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
