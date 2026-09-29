"""De onde vem o acerto da v3: primeira resposta do modelo × correção pelo retorno do código.

    python scripts/v3/decompor_ganho.py results/dev_v3/ciclo2/tc3-gemma4-e4b-it-qat [outra pasta ...]

Para cada execução, reconstrói a PRIMEIRA decisão do modelo (os parâmetros da primeira chamada a
buscar_catalogo, ou a recusa, se ela veio antes de qualquer busca) a partir do traço gravado, e a pontua com
o mesmo gabarito da resposta final. A diferença entre as duas é o que o retorno (validação, recusa com
retorno, resposta do usuário simulado) acrescentou. Na Saída Estruturada v3, a primeira decisão é o primeiro
objeto do histórico de tentativas.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

# a lógica da primeira decisão e da decomposição está em pfc_busca.evaluation.lote2 (usada na análise do lote 2)
from pfc_busca.evaluation import lote2  # noqa: E402
from pfc_busca.evaluation.run_evaluation import (  # noqa: E402
    carregar_execucoes,
    dataset_da_rodada,
    repontuar,
)


def decompor(pasta: Path) -> dict:
    validas, _ = repontuar(carregar_execucoes(pasta), dataset_da_rodada(pasta))
    ids = (RAIZ / "data" / "lote_validacao" / "dev_v3_ids.txt")
    if "dev_v3" in str(pasta) and ids.exists():
        dev = set(ids.read_text(encoding="utf-8").strip().split(","))
        validas = [x for x in validas if x["id"] in dev]
    linhas = [x for x in validas if not x.get("observacional")]
    return lote2.decompor(linhas)


def main() -> int:
    for arg in sys.argv[1:]:
        c = decompor(Path(arg))
        n = c.get("n", 0) or 1
        print(f"{Path(arg).name}: n={c.get('n')}  primeira decisão {c.get('primeira', 0)}/{n} = {c.get('primeira', 0)/n:.1%}  "
              f"final {c.get('final', 0)}/{n} = {c.get('final', 0)/n:.1%}  | retorno consertou {c.get('consertou', 0)}, "
              f"estragou {c.get('estragou', 0)} | com aviso {c.get('com_aviso', 0)} | recusas contestadas "
              f"{c.get('contestadas', 0)} {({k: v for k, v in c.items() if k.startswith('contestada_')})}"
              + (f" | sem traço {c['sem_traco']}" if c.get("sem_traco") else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
