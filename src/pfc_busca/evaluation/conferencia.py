"""pfc-conferir — confere as rodadas antes de levar qualquer número ao texto.

    python -m pfc_busca.evaluation.conferencia                 # todas as rodadas em results/ e results/estacao/
    python -m pfc_busca.evaluation.conferencia results/<modelo> ...

Para cada pasta de rodada verifica, a partir do manifesto e de `execucoes.jsonl`:
- prompt e definição da ferramenta iguais aos vigentes (hash);
- rodada completa: cada consulta selecionada × cada repetição, sem duplicatas;
- linhas descartadas na repontuação (texto da consulta alterado depois da execução);
- erros de infraestrutura (timeout, indisponibilidade) e erros do modelo;
- uma única data de referência em todas as linhas.

Sai com código 1 se houver problema bloqueante. Nada é alterado.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from pfc_busca.evaluation import metrics
from pfc_busca.evaluation.dataset_builder import carregar_dataset
from pfc_busca.evaluation.run_evaluation import (
    DIR_RESULTADOS,
    carregar_execucoes,
    hash_ferramenta,
    hash_prompt,
    repontuar,
)


def conferir(pasta: Path) -> dict:
    manifesto = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8")) \
        if (pasta / "manifesto.json").exists() else {}
    linhas = carregar_execucoes(pasta)
    validas, descartadas = repontuar(linhas)
    problemas, avisos = [], []

    if not manifesto:
        problemas.append("sem manifesto.json")
    if manifesto.get("ferramenta_sha256") and manifesto["ferramenta_sha256"] != hash_ferramenta():
        problemas.append("definição da ferramenta diferente da vigente")
    if manifesto.get("prompt_sha256") is None:
        avisos.append("manifesto sem hash do prompt (rodada anterior ao registro do hash)")
    elif manifesto["prompt_sha256"] != hash_prompt():
        problemas.append("prompt de sistema diferente do vigente")

    chaves = Counter((x["id"], x["repeticao"]) for x in linhas)
    duplicadas = sorted(k for k, n in chaves.items() if n > 1)
    if duplicadas:
        problemas.append(f"{len(duplicadas)} execução(ões) duplicada(s), ex.: {duplicadas[:3]}")
    if descartadas:
        avisos.append(f"{len(set(descartadas))} consulta(s) descartada(s) na repontuação (texto alterado): "
                      f"{sorted(set(descartadas))[:6]}")

    datas = sorted({x["hoje"] for x in linhas})
    if len(datas) > 1:
        problemas.append(f"mais de uma data de referência: {datas}")

    reps = sorted({x["repeticao"] for x in validas})
    ids_validos = {x["id"] for x in validas}
    esperadas = manifesto.get("repeticoes") or (max(reps) if reps else 0)
    faltando = [(i, r) for r in range(1, esperadas + 1) for i in ids_validos
                if (i, r) not in {(x["id"], x["repeticao"]) for x in validas}]
    if faltando:
        problemas.append(f"{len(faltando)} execução(ões) faltando para completar {esperadas} repetição(ões)")
    total_dataset = len(carregar_dataset())
    if len(ids_validos) not in (total_dataset, 62, 22, 40):
        avisos.append(f"{len(ids_validos)} consultas distintas (dataset tem {total_dataset}): subconjunto?")

    infra = [x for x in validas if metrics.erro_de_infra(x)]
    if infra:
        problemas.append(f"{len(infra)} erro(s) de infraestrutura — retomar a rodada antes de consolidar")
    erros_modelo = Counter(x["classe_erro"] for x in validas if x.get("erro") and not metrics.erro_de_infra(x))

    sessoes = manifesto.get("sessoes") or []
    if len(sessoes) > 1:
        avisos.append(f"rodada feita em {len(sessoes)} sessões — conferir se a VRAM/ambiente foi o mesmo")

    return {"pasta": str(pasta), "modelo": manifesto.get("modelo"), "provedor": manifesto.get("provedor"),
            "consultas": len(ids_validos), "repeticoes": reps, "linhas_validas": len(validas),
            "data_referencia": datas, "erros_do_modelo": dict(erros_modelo),
            "problemas": problemas, "avisos": avisos}


def pastas_padrao() -> list[Path]:
    candidatas = []
    for base in (DIR_RESULTADOS, DIR_RESULTADOS / "estacao"):
        if base.is_dir():
            candidatas += [p for p in sorted(base.iterdir()) if (p / "execucoes.jsonl").exists()]
    return candidatas


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Confere as rodadas de avaliação antes da consolidação.")
    p.add_argument("pastas", nargs="*", type=Path)
    args = p.parse_args(argv)
    pastas = args.pastas or pastas_padrao()
    if not pastas:
        print("nenhuma rodada encontrada", file=sys.stderr)
        return 1
    bloqueantes = 0
    for pasta in pastas:
        r = conferir(pasta)
        marca = "OK " if not r["problemas"] else "ERRO"
        print(f"[{marca}] {r['pasta']} · {r['modelo']} ({r['provedor']}) · {r['consultas']} consultas × "
              f"rep. {r['repeticoes']} · data {', '.join(r['data_referencia'])} · erros do modelo {r['erros_do_modelo']}")
        for x in r["problemas"]:
            print(f"       ✗ {x}")
        for x in r["avisos"]:
            print(f"       · {x}")
        bloqueantes += bool(r["problemas"])
    return 1 if bloqueantes else 0


if __name__ == "__main__":
    raise SystemExit(main())
