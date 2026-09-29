"""Reaplica o validador ATUAL às respostas finais de uma rodada de desenvolvimento.

    python scripts/v3/replay_validador.py --ciclo 1 --config tc3-

Para cada resposta errada, mostra o que o validador de agora diria (ele pegaria o erro?); para as certas,
conta os alarmes (um alarme numa resposta certa pode empurrar o modelo para o erro). É uma estimativa
barata antes de rodar o ciclo seguinte: não reproduz o que o modelo faria com o retorno. Só desenvolvimento.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ciclo_dev import linhas_de  # noqa: E402
from erros_ciclo import pasta_de  # noqa: E402

from pfc_busca import ferramentas  # noqa: E402
from pfc_busca.evaluation import metrics  # noqa: E402

HOJE = date(2026, 9, 24)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ciclo", type=int, required=True)
    p.add_argument("--config", required=True)
    args = p.parse_args()
    linhas = [x for x in linhas_de(pasta_de(args.ciclo, args.config)) if x["espera_tool_call"]]
    pegos, erradas, alarmes_certas = 0, 0, []
    for x in linhas:
        a = metrics.avaliar_linha(x)
        if x["predito"] is None:
            continue
        erros, avisos = ferramentas.validar_parametros(x["predito"], x["consulta"], HOJE)
        msgs = erros + avisos
        if a.correto:
            if msgs:
                alarmes_certas.append((x, msgs))
            continue
        erradas += 1
        pegos += bool(msgs)
        print(f"{'PEGO ' if msgs else 'SOLTO'} {x['id']}: {x['consulta'][:80]!r}")
        print(f"      FP {sorted(a.fp)} FN {sorted(a.fn)}")
        for m in msgs:
            print(f"      -> {m[:160]}")
    print(f"\nerradas com busca: {erradas}; o validador atual reclamaria de {pegos}")
    print(f"certas com alarme: {len(alarmes_certas)}")
    for x, msgs in alarmes_certas:
        print(f"  {x['id']}: {x['consulta'][:80]!r} -> {x['predito']}")
        for m in msgs:
            print(f"      -> {m[:160]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
