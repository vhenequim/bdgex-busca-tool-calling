"""Ciclo de desenvolvimento da v3 no conjunto de DESENVOLVIMENTO (160 consultas do lote 1).

    python scripts/v3/ciclo_dev.py --ciclo 1 --rodar tool_calling_v3 saida_estruturada_v3 ...   # roda e resume
    python scripts/v3/ciclo_dev.py --ciclo 1                                                 # só resume

As rodadas vão para results/dev_v3/ciclo<N>/ (Gemma 4 E4B local, mesma tag e digest da T4, data de
referência 2026-09-24, sem SQL). O resumo compara com as rodadas v1/v2 da T4 restritas às mesmas
consultas e grava results/dev_v3/ciclo<N>/resumo_ciclo.md. O lote 2 (teste) nunca entra aqui.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

from pfc_busca.evaluation import metrics  # noqa: E402
from pfc_busca.evaluation.run_evaluation import (  # noqa: E402
    PREFIXO_ABORDAGEM,
    carregar_execucoes,
    dataset_da_rodada,
    repontuar,
)

MODELO = "gemma4:e4b-it-qat"
SLUG = "gemma4-e4b-it-qat"
IDS = (RAIZ / "data" / "lote_validacao" / "dev_v3_ids.txt").read_text(encoding="utf-8").strip().split(",")
REFERENCIAS = {"tc1 (T4)": RAIZ / "results" / "lote" / SLUG, "se1 (T4)": RAIZ / "results" / "lote" / f"se-{SLUG}",
               "tc2 (T4)": RAIZ / "results" / "lote" / f"tc2-{SLUG}", "se2 (T4)": RAIZ / "results" / "lote" / f"se2-{SLUG}"}


def rodar(abordagem: str, saida: Path) -> int:
    cmd = [str(RAIZ / ".venv" / "Scripts" / "pfc-avaliar.exe"), "--modelo", MODELO, "--abordagem", abordagem,
           "--dataset", "data/lote_validacao.json", "--ids", ",".join(IDS), "--saida", str(saida),
           "--hoje", "2026-09-24", "--sem-sql", "--repeticoes", "1"]
    return subprocess.run(cmd, cwd=RAIZ, env={**os.environ, "PYTHONIOENCODING": "utf-8"}).returncode


def linhas_de(pasta: Path) -> list[dict]:
    brutas = [x for x in carregar_execucoes(pasta) if x["id"] in set(IDS)]
    validas, _ = repontuar(brutas, dataset_da_rodada(pasta))
    return [x for x in validas if not x.get("observacional")]


def hibrido(decisor: list[dict], extrator: list[dict]) -> list[dict]:
    """Arquitetura em duas etapas simulada: o `decisor` decide se busca; quando busca, valem os parâmetros do
    `extrator`. Latência = soma das duas chamadas quando há busca."""
    por_id = {x["id"]: x for x in extrator}
    saida = []
    for d in decisor:
        e = por_id.get(d["id"])
        if e is None:
            continue
        x = dict(e)
        if d["predito"] is None:
            x.update(predito=None, chamou_ferramenta=False, latencia_llm_ms=d.get("latencia_llm_ms"))
        else:
            x["latencia_llm_ms"] = (d.get("latencia_llm_ms") or 0) + (e.get("latencia_llm_ms") or 0)
        x["extras"] = {}
        saida.append(x)
    return saida


def medidas(linhas: list[dict]) -> dict:
    avals = [(x, metrics.avaliar_linha(x)) for x in linhas]
    dominio = [(x, a) for x, a in avals if x["espera_tool_call"] and not x.get("aceita_nao_chamar")]
    fora = [(x, a) for x, a in avals if not x["espera_tool_call"]]
    fp, fn = Counter(), Counter()
    for _, a in avals:
        fp.update(a.fp)
        fn.update(a.fn)
    ext = [x.get("extras") or {} for x in linhas]
    g = metrics.agregar(linhas)
    return {
        "n": len(linhas), "acuracia": sum(a.correto for _, a in avals) / len(avals),
        "dominio": sum(a.correto for _, a in dominio) / len(dominio),
        "falsa_recusa": sum(x["predito"] is None for x, _ in dominio) / len(dominio),
        "recusa_f": sum(x["predito"] is None for x, _ in fora) / len(fora) if fora else None,
        "f1": g["f1_ponderado"],
        "chamadas": statistics.fmean(e.get("chamadas_modelo", 1) for e in ext),
        "perguntas": sum(e.get("perguntas", 0) > 0 for e in ext), "texto": sum(e.get("chamadas_em_texto", 0) > 0 for e in ext),
        "latencia": statistics.median(x["latencia_llm_ms"] for x in linhas if x.get("latencia_llm_ms")) / 1000,
        "fp": dict(fp.most_common(6)), "fn": dict(fn.most_common(6)),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ciclo", type=int, required=True)
    p.add_argument("--rodar", nargs="*", default=[])
    args = p.parse_args()
    pasta = RAIZ / "results" / "dev_v3" / f"ciclo{args.ciclo}"
    for abordagem in args.rodar:
        print(f"== {abordagem}", flush=True)
        rodar(abordagem, pasta)
    ref = {nome: linhas_de(p) for nome, p in REFERENCIAS.items() if p.exists()}
    tabela = {nome: medidas(linhas) for nome, linhas in ref.items()}
    if "tc2 (T4)" in ref and "se1 (T4)" in ref:
        tabela["hib: tc2 decide, se1 extrai (T4)"] = medidas(hibrido(ref["tc2 (T4)"], ref["se1 (T4)"]))
    for abordagem in PREFIXO_ABORDAGEM:
        d = pasta / (PREFIXO_ABORDAGEM[abordagem] + SLUG)
        if (d / "execucoes.jsonl").exists():
            tabela[abordagem] = medidas(linhas_de(d))
    tc3, se3 = pasta / ("tc3-" + SLUG), pasta / ("se3-" + SLUG)
    if (tc3 / "execucoes.jsonl").exists() and (se3 / "execucoes.jsonl").exists():
        tabela["hib: tc3 decide, se3 extrai"] = medidas(hibrido(linhas_de(tc3), linhas_de(se3)))
    linhas = [f"# Ciclo {args.ciclo} — desenvolvimento da v3 (160 consultas do lote 1)", "",
              "| Configuração | n | Acurácia | Domínio | Falsa recusa | Recusa F | F1 | Chamadas/consulta | "
              "Com pergunta | Chamada em texto | Latência mediana (s) | FP mais comuns | FN mais comuns |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for nome, m in tabela.items():
        linhas.append(f"| {nome} | {m['n']} | {m['acuracia']:.1%} | {m['dominio']:.1%} | {m['falsa_recusa']:.1%} | "
                      f"{(m['recusa_f'] or 0):.1%} | {m['f1']:.3f} | {m['chamadas']:.2f} | {m['perguntas']} | "
                      f"{m['texto']} | {m['latencia']:.1f} | {m['fp']} | {m['fn']} |")
    (pasta / "resumo_ciclo.md").parent.mkdir(parents=True, exist_ok=True)
    (pasta / "resumo_ciclo.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    (pasta / "resumo_ciclo.json").write_text(json.dumps(tabela, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(linhas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
