"""Preenche o campo `origem` das orientações com a contagem dos erros que as motivaram.

    python experimentos/orientacoes/contar_origens.py            # grava nos .md e imprime
    python experimentos/orientacoes/contar_origens.py --so-ver   # só imprime

Critério, o mesmo para todas: uma execução errada conta para a orientação se a consulta dispara a orientação
(gatilho ou `sempre`) e o erro envolve um dos campos dela (campo a mais ou a menos); orientações sem campos
(esclarecimento, finalidade) contam as consultas do domínio em que a configuração não buscou. Fontes, só de
DESENVOLVIMENTO: ciclo 1 ← rodadas v1/v2 da T4 no lote 1 inteiro; ciclo N > 1 ← a rodada tc3 do ciclo N−1 nas
160 consultas de desenvolvimento. A contagem mede o alcance do padrão de erro, não o efeito da orientação.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(RAIZ / "scripts" / "v3"))

import orientacoes  # noqa: E402
from ciclo_dev import SLUG, linhas_de  # noqa: E402

from pfc_busca.evaluation import metrics  # noqa: E402
from pfc_busca.evaluation.run_evaluation import (  # noqa: E402
    carregar_execucoes,
    dataset_da_rodada,
    repontuar,
)

T4 = {"tc1": "", "se1": "se-", "tc2": "tc2-", "se2": "se2-"}


def _lote1(prefixo: str) -> list[dict]:
    pasta = RAIZ / "results" / "lote" / (prefixo + SLUG)
    validas, _ = repontuar(carregar_execucoes(pasta), dataset_da_rodada(pasta))
    return [x for x in validas if not x.get("observacional")]


def conta(o: orientacoes.Orientacao, linhas: list[dict]) -> int:
    n = 0
    for x in linhas:
        if not o.aplica(x["consulta"]):
            continue
        a = metrics.avaliar_linha(x)
        if a.correto:
            continue
        if o.campos:
            n += bool(set(o.campos) & (a.fp | a.fn))
        else:
            n += x["espera_tool_call"] and not x.get("aceita_nao_chamar") and x["predito"] is None
    return n


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--so-ver", action="store_true")
    args = p.parse_args()
    fontes = {1: {nome: _lote1(pref) for nome, pref in T4.items()}}
    todas = orientacoes.carregar()
    for ciclo in sorted({o.ciclo for o in todas} - {1}):
        pasta = RAIZ / "results" / "dev_v3" / f"ciclo{ciclo - 1}" / ("tc3-" + SLUG)
        fontes[ciclo] = {"tc3": linhas_de(pasta)}
    for o in todas:
        contagens = {nome: conta(o, linhas) for nome, linhas in fontes[o.ciclo].items()}
        onde = ("lote 1, rodadas v1/v2 da T4" if o.ciclo == 1 else
                f"ciclo {o.ciclo - 1} de desenvolvimento, tc3 nas 160 consultas")
        criterio = f"erro em {', '.join(o.campos)}" if o.campos else "não buscou no domínio"
        texto = (f"{onde}: {sum(contagens.values())} execuções erradas com o gatilho e {criterio} ("
                 + ", ".join(f"{k} {v}" for k, v in contagens.items()) + ")")
        print(f"{o.nome}: {texto}")
        if not args.so_ver:
            arq = orientacoes.DIR / o.arquivo
            bruto = arq.read_text(encoding="utf-8")
            novo = re.sub(r"^origem: .*$", "origem: '" + texto.replace("'", "''") + "'", bruto, count=1, flags=re.M)
            arq.write_text(novo, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
