"""Autoteste do validador: ele não deve reclamar das respostas CORRETAS.

    python scripts/v3/validador_no_gabarito.py [--dataset data/lote_validacao.json]

Aplica `ferramentas.validar_parametros` à leitura preferencial resolvida do gabarito de cada consulta
(que busca) e lista os erros e avisos — todo aviso sobre a resposta certa é um defeito do validador
(falso alarme), que custaria ao modelo uma rodada ou, pior, o induziria a errar. Roda só nos conjuntos
de DESENVOLVIMENTO (310 consultas e lote 1).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

from pfc_busca import ferramentas  # noqa: E402
from pfc_busca.evaluation import gabarito  # noqa: E402
from pfc_busca.evaluation.dataset_builder import carregar_dataset  # noqa: E402

HOJE = date(2026, 9, 24)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", type=Path, default=RAIZ / "data" / "lote_validacao.json")
    p.add_argument("--exemplos", type=int, default=3)
    args = p.parse_args()
    if "lote_validacao_2" in str(args.dataset):
        print("o lote 2 é de teste: não é usado no desenvolvimento")
        return 2
    casos = [c for c in carregar_dataset(args.dataset) if c["espera_tool_call"] and not c.get("observacional")]
    tipos, exemplos, com_problema = Counter(), {}, 0
    for c in casos:
        leitura = gabarito.resolver_leituras(c, HOJE)[0]
        pref = {k: gabarito.valor_preferencial(v) for k, v in leitura.items()}
        erros, avisos = ferramentas.validar_parametros(pref, c["consulta"], HOJE)
        if erros or avisos:
            com_problema += 1
        for m in erros + avisos:
            chave = re.sub(r"'[^']*'", "…", m)[:70]
            tipos[chave] += 1
            exemplos.setdefault(chave, []).append((c["id"], c["consulta"], pref))
    print(f"{com_problema}/{len(casos)} respostas corretas com algum erro ou aviso do validador ({args.dataset.name})")
    for chave, n in tipos.most_common():
        print(f"{n:4d}  {chave}")
        for i, q, pref in exemplos[chave][:args.exemplos]:
            print(f"        {i}: {q[:90]!r} -> {pref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
