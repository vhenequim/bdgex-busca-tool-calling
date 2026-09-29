"""Lista os erros de uma configuração num ciclo de desenvolvimento, para escrever orientações.

    python scripts/v3/erros_ciclo.py --ciclo 1 --config tc3-          # -> results/dev_v3/ciclo1/erros_tc3.md

Uma linha por consulta errada: consulta, esperado, predito, campos a mais (FP) e a menos (FN), ferramentas
usadas, avisos recebidos e orientações injetadas. Com --comparar, marca também as consultas que a outra
configuração acertou e esta errou (regressões) e vice-versa. Só no desenvolvimento: recusa o lote 2.
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ciclo_dev import SLUG, linhas_de  # noqa: E402

from pfc_busca.evaluation import metrics  # noqa: E402


def _extra(linha: dict, chave: str, padrao=None):
    v = (linha.get("extras") or {}).get(chave, padrao)
    if isinstance(v, str):
        try:
            return ast.literal_eval(v)
        except (ValueError, SyntaxError):
            return v
    return v


def pasta_de(ciclo: int, prefixo: str) -> Path:
    if prefixo.startswith("t4:"):   # rodadas de referência da T4 (lote 1 completo)
        return RAIZ / "results" / "lote" / (prefixo[3:] + SLUG)
    return RAIZ / "results" / "dev_v3" / f"ciclo{ciclo}" / (prefixo + SLUG)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ciclo", type=int, required=True)
    p.add_argument("--config", required=True, help="prefixo da configuração (tc3-, se3-, tc3o-...) ou t4:<prefixo>")
    p.add_argument("--comparar", help="outra configuração do mesmo ciclo (ou t4:<prefixo>) para regressões")
    args = p.parse_args()
    pasta = pasta_de(args.ciclo, args.config)
    if "lote_validacao_2" in str(pasta):
        return 2
    linhas = linhas_de(pasta)
    avals = {x["id"]: (x, metrics.avaliar_linha(x)) for x in linhas}
    outra = {}
    if args.comparar:
        outra = {x["id"]: metrics.avaliar_linha(x).correto for x in linhas_de(pasta_de(args.ciclo, args.comparar))}
    erradas = [(x, a) for x, a in avals.values() if not a.correto]
    tipos = Counter()
    for _, a in erradas:
        tipos.update(f"FP:{c}" for c in a.fp)
        tipos.update(f"FN:{c}" for c in a.fn)
        if not a.fp and not a.fn:
            tipos["valor errado"] += 1
    nome = args.config.rstrip("-").replace("t4:", "t4_") or "tc1"
    saida = RAIZ / "results" / "dev_v3" / f"ciclo{args.ciclo}" / f"erros_{nome}.md"
    out = [f"# Erros de {args.config} no ciclo {args.ciclo}: {len(erradas)} de {len(avals)}", "",
           "Campos: " + ", ".join(f"{k} {v}" for k, v in tipos.most_common()), ""]
    if outra:
        reg = [i for i, (_, a) in avals.items() if not a.correto and outra.get(i)]
        ganho = [i for i, (_, a) in avals.items() if a.correto and outra.get(i) is False]
        out += [f"Regressões (a outra, {args.comparar}, acertou): {len(reg)} — {', '.join(reg)}",
                f"Ganhos (a outra errou): {len(ganho)}", ""]
    for x, a in sorted(erradas, key=lambda t: t[0]["id"]):
        marca = " **(regressão)**" if outra.get(x["id"]) else ""
        out += [f"## {x['id']} [{','.join(x.get('categorias', []))}]{marca}",
                f"- consulta: {x['consulta']}",
                f"- esperado: {x['esperado_resolvido']}" + (f" | alternativas: {x['alternativas_resolvidas']}"
                                                          if x.get("alternativas_resolvidas") else ""),
                f"- predito: {x['predito']}",
                f"- FP {sorted(a.fp)} FN {sorted(a.fn)}",
                f"- ferramentas: {_extra(x, 'ferramentas_usadas', {})}; avisos: {_extra(x, 'avisos_recebidos', 0)}; "
                f"perguntas: {_extra(x, 'perguntas', 0)}; orientações: {_extra(x, 'orientacoes', [])}", ""]
    saida.write_text("\n".join(out), encoding="utf-8")
    print(f"{len(erradas)} erros de {len(avals)} -> {saida.relative_to(RAIZ)}")
    print(tipos.most_common(12))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
