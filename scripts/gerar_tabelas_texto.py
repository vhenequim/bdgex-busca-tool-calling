"""Regenera todas as tabelas, figuras e macros do texto a partir de data/ e results/.

    python scripts/gerar_tabelas_texto.py                 # destino padrão: ../paper_revisado
    python scripts/gerar_tabelas_texto.py --texto texto   # ou a cópia do repositório

Executa, na ordem: pfc-dataset --apendice, pfc-auditar --paper e pfc-relatorio para as
rodadas completas, a validação na estação, a reexecução na estação, a referência em nuvem e
a referência em nuvem restrita às consultas das rodadas completas, e a comparação entre Tool Calling
e Saída Estruturada (linhas de base), quando houver. Um modelo da nuvem só entra quando a sua rodada
cobre todas as consultas do dataset.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pfc_busca.evaluation import audit, comparacao, dataset_builder, report
from pfc_busca.evaluation.run_evaluation import DIR_RESULTADOS, carregar_execucoes, repontuar

LOCAIS = ["qwen3:4b-instruct-2507-q4_K_M", "gemma4:e4b-it-qat", "gemma4:e2b-it-qat", "mistral-nemo:12b"]
ESTACAO = ["qwen3:4b-instruct-2507-q4_K_M", "gemma4:e2b-it-qat"]
NUVEM = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"]


def nuvem_completos() -> list[str]:
    total = len(dataset_builder.carregar_dataset())
    completos = []
    for pasta in sorted(DIR_RESULTADOS.glob("groq-*")):
        if not (pasta / "execucoes.jsonl").exists():
            continue
        linhas, _ = repontuar(carregar_execucoes(pasta))
        if linhas and len({lin["id"] for lin in linhas}) == total:
            completos.append(linhas[0]["modelo"])
    return [m for m in NUVEM if m in completos]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--texto", type=Path, default=Path(__file__).resolve().parents[2] / "paper_revisado")
    args = p.parse_args()
    texto = str(args.texto)
    nuvem = nuvem_completos()
    print(f"nuvem com rodada completa: {', '.join(nuvem) or 'nenhum'}")
    passos = [
        (dataset_builder.main, ["--apendice", texto]),
        (audit.main, ["--anotacao-independente", str(audit.DIR_AUDITORIA / "anotacao_independente.json"),
                      "--paper", texto]),
        (report.main, ["--modelos", ",".join(LOCAIS), "--comparar-com", str(DIR_RESULTADOS / "estacao"),
                       "--sufixo", "", "--titulo", "", "--paper", texto]),
        (report.main, ["--resultados", str(DIR_RESULTADOS / "estacao"), "--modelos", ",".join(ESTACAO),
                       "--sufixo", "_estacao", "--titulo", ", na estação de referência (camadas P e N)",
                       "--paper", texto]),
        (report.main, ["--resultados", str(DIR_RESULTADOS / "estacao"), "--modelos", ESTACAO[0],
                       "--comparar-com", str(DIR_RESULTADOS / "_descartados" / "estacao_14set_vram_disputada"),
                       "--nome-comparacao", "reexecucao", "--rotulos-comparacao", "24/set,14/set",
                       "--legenda-comparacao", "Qwen 3 4B executado duas vezes na estação de referência, com os "
                       "mesmos pesos, prompt, ferramenta e data de referência (camadas P e N)",
                       "--so-comparacao", "--saida", str(DIR_RESULTADOS / "estacao" / "consolidado"),
                       "--paper", texto]),
    ]
    if nuvem:
        passos += [
            (report.main, ["--modelos", ",".join(nuvem), "--sufixo", "_groq",
                           "--titulo", ", na referência em nuvem (Groq)", "--paper", texto]),
            (report.main, ["--modelos", ",".join(nuvem), "--sufixo", "_groqcomum",
                           "--titulo", ", na referência em nuvem, só com as consultas das rodadas completas",
                           "--mesmas-consultas-de", str(DIR_RESULTADOS), "--modelos-referencia", ",".join(LOCAIS),
                           "--saida", str(DIR_RESULTADOS / "consolidado_groqcomum"), "--paper", texto]),
        ]
    passos += [
        (comparacao.main, ["--resultados", str(DIR_RESULTADOS), "--paper", texto]),
        (comparacao.main, ["--resultados", str(DIR_RESULTADOS / "estacao"), "--sufixo", "_estacao", "--paper", texto]),
    ]
    for funcao, argv in passos:
        # cada comando lê SUFIXO/TITULO globais do relatório; zere entre as chamadas
        report.SUFIXO, report.TITULO = "", ""
        codigo = funcao(argv)
        if codigo:
            print(f"falhou: {funcao.__module__} {' '.join(argv[:4])}", file=sys.stderr)
            return codigo
    print(f"tabelas, figuras e macros regeneradas em {texto}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
