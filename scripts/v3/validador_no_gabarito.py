"""Autoteste do validador: ele não deve reclamar das respostas CORRETAS.

    python scripts/v3/validador_no_gabarito.py [--dataset data/lote_validacao.json]
    python scripts/v3/validador_no_gabarito.py --tex      # os dois conjuntos -> macros res{v3}{autoteste}{...}

Aplica `ferramentas.validar_parametros` à leitura preferencial resolvida do gabarito de cada consulta
(que busca) e lista os erros e avisos — todo aviso sobre a resposta certa é um defeito do validador
(falso alarme), que custaria ao modelo uma rodada ou, pior, o induziria a errar. Roda só nos conjuntos
de DESENVOLVIMENTO (310 consultas e lote 1).
"""

from __future__ import annotations

import argparse
import json
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
PAPER = RAIZ.parent / "paper_revisado"
HISTORICO = RAIZ / "data" / "v3" / "autoteste_historico.json"


def contar(dataset: Path) -> tuple[int, int]:
    """(respostas corretas com algum erro ou aviso, respostas corretas) num conjunto de desenvolvimento."""
    casos = [c for c in carregar_dataset(dataset) if c["espera_tool_call"] and not c.get("observacional")]
    com_problema = 0
    for c in casos:
        leitura = gabarito.resolver_leituras(c, HOJE)[0]
        pref = {k: gabarito.valor_preferencial(v) for k, v in leitura.items()}
        erros, avisos = ferramentas.validar_parametros(pref, c["consulta"], HOJE)
        com_problema += bool(erros or avisos)
    return com_problema, len(casos)


def escrever_tex() -> None:
    lote1, n1 = contar(RAIZ / "data" / "lote_validacao.json")
    base, n310 = contar(RAIZ / "data" / "dataset.json")
    hist = json.loads(HISTORICO.read_text(encoding="utf-8"))
    milhar = lambda n: f"{n:,}".replace(",", ".")   # noqa: E731 — como o resto do texto (1.929)
    valores = {"n": milhar(n1), "final": lote1, "n310": n310, "final310": base,
               "inicial": hist["lote1_inicial"]}
    # recusa com retorno: quantas consultas fora do domínio do lote 1 teriam a recusa contestada
    fora = [c for c in carregar_dataset(RAIZ / "data" / "lote_validacao.json") if not c["espera_tool_call"]]
    recusa = {"nF": len(fora), "contestadasF": sum(bool(ferramentas.evidencias_de_catalogo(c["consulta"])) for c in fora)}
    macros = ["% AUTO-GERADO por scripts/v3/validador_no_gabarito.py --tex — não editar à mão",
              r"\providecommand{\res}[3]{\ifcsname res@#1@#2@#3\endcsname\csname res@#1@#2@#3\endcsname"
              r"\else\textbf{??}\fi}"]
    macros += [rf"\expandafter\def\csname res@v3@autoteste@{k}\endcsname{{{v}}}" for k, v in sorted(valores.items())]
    macros += [rf"\expandafter\def\csname res@v3@recusa@{k}\endcsname{{{v}}}" for k, v in sorted(recusa.items())]
    valores.update(recusa)
    # experimento descartado (docs/v3_desenvolvimento.md): a mesma v3 com e sem orientações no ciclo 2
    from ciclo_dev import SLUG, linhas_de

    from pfc_busca.evaluation import metrics
    ciclo2 = RAIZ / "results" / "dev_v3" / "ciclo2"
    if (ciclo2 / f"tc3-{SLUG}").exists() and (ciclo2 / f"tc3f-{SLUG}").exists():
        com = {x["id"]: metrics.avaliar_linha(x).correto for x in linhas_de(ciclo2 / f"tc3-{SLUG}")}
        sem = {x["id"]: metrics.avaliar_linha(x).correto for x in linhas_de(ciclo2 / f"tc3f-{SLUG}")}
        orient = {"n": len(sem), "com": sum(com.values()), "sem": sum(sem.values()),
                  "socom": sum(com[i] and not sem[i] for i in sem), "sosem": sum(sem[i] and not com[i] for i in sem)}
        macros += [rf"\expandafter\def\csname res@v3dev@orientacoes@{k}\endcsname{{{v}}}"
                   for k, v in sorted(orient.items())]
        valores.update({f"orientacoes_{k}": v for k, v in orient.items()})
    conteudo = "\n".join(macros) + "\n"
    (RAIZ / "data" / "v3" / "numeros_v3.tex").write_text(conteudo, encoding="utf-8", newline="\n")
    if PAPER.is_dir():
        (PAPER / "tabelas" / "numeros_v3.tex").write_text(conteudo, encoding="utf-8", newline="\n")
    print(valores)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", type=Path, default=RAIZ / "data" / "lote_validacao.json")
    p.add_argument("--exemplos", type=int, default=3)
    p.add_argument("--tex", action="store_true", help="conta nos dois conjuntos de desenvolvimento e grava as macros")
    args = p.parse_args()
    if args.tex:
        escrever_tex()
        return 0
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
