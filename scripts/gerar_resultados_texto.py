"""Regenera todas as tabelas, figuras e macros de resultado usadas no texto (paper_revisado/).

    python scripts/gerar_resultados_texto.py [--paper ../paper_revisado]

Ordem: Apêndice A (dataset) e auditoria; rodadas completas (com a comparação com a estação);
estação de referência; reexecução na estação; referência em nuvem (só modelos com rodada
completa, isto é, com todas as consultas do dataset executadas) e a mesma referência restrita
às consultas pontuadas nas rodadas completas. Antes, confere as rodadas (conferencia.py) e
para se houver problema bloqueante.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pfc_busca.evaluation import audit, conferencia, dataset_builder, report
from pfc_busca.evaluation.dataset_builder import carregar_dataset
from pfc_busca.evaluation.run_evaluation import carregar_execucoes, repontuar

RAIZ = Path(__file__).resolve().parents[1]
RESULTADOS = RAIZ / "results"
LOCAIS = ["qwen3:4b-instruct-2507-q4_K_M", "gemma4:e4b-it-qat", "gemma4:e2b-it-qat", "mistral-nemo:12b"]
ESTACAO = ["qwen3:4b-instruct-2507-q4_K_M", "gemma4:e2b-it-qat"]
NUVEM = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]
REEXECUCAO = RESULTADOS / "_descartados" / "estacao_14set_vram_disputada"


def nuvem_completos() -> list[str]:
    total = len(carregar_dataset())
    completos = []
    for m in NUVEM:
        pasta = RESULTADOS / ("groq-" + m.replace("/", "-").replace(":", "-"))
        if (pasta / "execucoes.jsonl").exists():
            ids = {lin["id"] for lin in repontuar(carregar_execucoes(pasta))[0]}
            if len(ids) == total:
                completos.append(m)
    return completos


def rodar(args: list[str]) -> None:
    print("pfc-relatorio", " ".join(args))
    if report.main(args) != 0:
        raise SystemExit(f"falhou: pfc-relatorio {' '.join(args)}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--paper", type=Path, default=RAIZ.parent / "paper_revisado")
    args = p.parse_args()
    paper = str(args.paper)

    pastas = [RESULTADOS / p.name for p in RESULTADOS.iterdir() if (p / "execucoes.jsonl").exists()]
    pastas += [p for p in (RESULTADOS / "estacao").iterdir() if (p / "execucoes.jsonl").exists()]
    if conferencia.main([str(x) for x in pastas]) != 0:
        print("há problema bloqueante nas rodadas (acima); nada foi gerado", file=sys.stderr)
        return 1

    dataset_builder.main(["--apendice", paper])
    audit.main(["--anotacao-independente", str(RAIZ / "data" / "auditoria" / "anotacao_independente.json"),
                "--paper", paper])

    locais = ",".join(LOCAIS)
    rodar(["--modelos", locais, "--comparar-com", str(RESULTADOS / "estacao"), "--paper", paper])
    rodar(["--resultados", str(RESULTADOS / "estacao"), "--modelos", ",".join(ESTACAO), "--sufixo", "_estacao",
           "--titulo", " --- estação de referência (camadas P e N)", "--paper", paper])
    if REEXECUCAO.is_dir():
        rodar(["--resultados", str(RESULTADOS / "estacao"), "--modelos", ESTACAO[0], "--comparar-com", str(REEXECUCAO),
               "--nome-comparacao", "reexecucao", "--rotulos-comparacao", "24/set,14/set",
               "--legenda-comparacao", "Qwen 3 4B executado duas vezes na estação de referência, com os mesmos pesos, "
               "prompt, ferramenta e data de referência (camadas P e N)",
               "--so-comparacao", "--saida", str(RESULTADOS / "estacao" / "consolidado"), "--paper", paper])
    nuvem = nuvem_completos()
    if nuvem:
        print("referência em nuvem com rodada completa:", ", ".join(nuvem))
        rodar(["--modelos", ",".join(nuvem), "--sufixo", "_groq", "--titulo", " --- referência em nuvem (Groq)",
               "--saida", str(RESULTADOS / "consolidado_groq"), "--paper", paper])
        rodar(["--modelos", ",".join(nuvem), "--sufixo", "_groqcomum",
               "--titulo", " --- referência em nuvem, consultas das rodadas completas",
               "--mesmas-consultas-de", str(RESULTADOS), "--modelos-referencia", locais,
               "--saida", str(RESULTADOS / "consolidado_groqcomum"), "--paper", paper])
    print("pronto: recompile o texto (pdflatex main.tex duas vezes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
