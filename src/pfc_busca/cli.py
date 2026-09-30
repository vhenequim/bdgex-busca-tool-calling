"""pfc: um comando só para o projeto. Cada subcomando delega ao CLI que já existe, com os mesmos argumentos.

    pfc abordagens [--json] [--hashes]      o registro das abordagens (pfc_busca.abordagens)
    pfc avaliar --modelo gemma4:e4b-it-qat --abordagem tool_calling_v3   # = pfc-avaliar ...
    pfc dataset | auditar | conferir | relatorio | comparacao | lote | lote2 [argumentos]
    pfc api [--abordagem NOME] [--modelo TAG] [--host H] [--porta P]     # a API com uvicorn
    pfc <subcomando> --help                 a ajuda do CLI de destino

Os comandos antigos (pfc-avaliar, pfc-dataset, pfc-relatorio, pfc-auditar, pfc-conferir) continuam.
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import sys
from collections.abc import Callable

# subcomando -> (módulo, descrição); todos expõem main(argv) -> int
DELEGADOS: dict[str, tuple[str, str]] = {
    "avaliar": ("pfc_busca.evaluation.run_evaluation", "roda um modelo sobre o dataset (= pfc-avaliar)"),
    "dataset": ("pfc_busca.evaluation.dataset_builder", "reconstrói data/dataset.json (= pfc-dataset)"),
    "auditar": ("pfc_busca.evaluation.audit", "auditoria automática do dataset (= pfc-auditar)"),
    "conferir": ("pfc_busca.evaluation.conferencia", "confere as rodadas antes de consolidar (= pfc-conferir)"),
    "relatorio": ("pfc_busca.evaluation.report", "tabelas, figuras e estatísticas das 310 (= pfc-relatorio)"),
    "comparacao": ("pfc_busca.evaluation.comparacao", "comparação das abordagens nas 310 consultas"),
    "lote": ("pfc_busca.evaluation.lote", "análise do lote de validação 1"),
    "lote2": ("pfc_busca.evaluation.lote2", "análise do lote 2 (teste da v3)"),
    "ab": ("pfc_busca.evaluation.ab", "teste A/B Tool Calling x Saída Estruturada"),
}


def disponiveis() -> dict[str, tuple[str, str]]:
    """Os delegados cujo módulo existe (o `ab` só aparece quando evaluation/ab.py existir)."""
    return {nome: v for nome, v in DELEGADOS.items() if importlib.util.find_spec(v[0]) is not None}


def ajuda() -> str:
    linhas = ["uso: pfc <subcomando> [argumentos do subcomando]", "",
              f"  {'abordagens':<12} lista o registro das abordagens (--json, --hashes)",
              f"  {'api':<12} sobe a API (uvicorn pfc_busca.api:app)"]
    linhas += [f"  {nome:<12} {descricao}" for nome, (_, descricao) in disponiveis().items()]
    return "\n".join(linhas + ["", "pfc <subcomando> --help mostra a ajuda do comando de destino."])


def listar_abordagens(argv: list[str], escrever: Callable[[str], None] = print) -> int:
    from pfc_busca import abordagens

    p = argparse.ArgumentParser(prog="pfc abordagens", description="Lista o registro das abordagens.")
    p.add_argument("--json", action="store_true", help="saída em JSON")
    p.add_argument("--hashes", action="store_true", help="inclui os hashes de prompt e de ferramenta do manifesto")
    args = p.parse_args(argv)
    linhas = abordagens.tabela()
    if args.hashes:
        for linha in linhas:
            linha["prompt_sha256"] = abordagens.hash_prompt(linha["nome"])
            linha["ferramenta_sha256"] = abordagens.hash_ferramenta(linha["nome"])
            linha["avisos"] = abordagens.avisos(linha["nome"])
    if args.json:
        escrever(json.dumps(linhas, ensure_ascii=False, indent=1))
        return 0
    cab = f"{'nome':<22} {'fam.':<4} {'versão':<9} {'prefixo':<11} {'só Ollama':<9}  descrição"
    escrever(cab)
    escrever("-" * len(cab))
    for x in linhas:
        marca = " *" if x["recomendada"] else ""
        escrever(f"{x['nome']:<22} {x['familia']:<4} {x['versao']:<9} {(x['prefixo'] or '(nenhum)'):<11} "
                 f"{'sim' if x['so_ollama'] else 'não':<9}  {x['descricao']}{marca}")
        if args.hashes:
            escrever(f"{'':<22} prompt {x['prompt_sha256'][:16]}… ferramenta {x['ferramenta_sha256'][:16]}…")
            for aviso in x["avisos"]:
                escrever(f"{'':<22} aviso: {aviso}")
    escrever("")
    escrever(f"* recomendada pela tese (padrão da API, com {abordagens.MODELO_RECOMENDADO}). Pastas: "
             "results/<prefixo><modelo>/. Uso: pfc avaliar --abordagem NOME; PFC_ABORDAGEM=NOME na API.")
    return 0


def servir(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="pfc api", description="Sobe a API (pfc_busca.api:app) com o uvicorn.")
    p.add_argument("--abordagem", help="define PFC_ABORDAGEM (padrão: a recomendada)")
    p.add_argument("--modelo", help="define PFC_MODELO_PADRAO")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--porta", type=int, default=8000)
    args = p.parse_args(argv)
    if args.abordagem:
        from pfc_busca import abordagens

        abordagens.obter(args.abordagem)   # nome errado falha aqui, antes de subir o servidor
        os.environ["PFC_ABORDAGEM"] = args.abordagem
    if args.modelo:
        os.environ["PFC_MODELO_PADRAO"] = args.modelo
    import uvicorn

    uvicorn.run("pfc_busca.api:app", host=args.host, port=args.porta)
    return 0


def delegar(nome: str, argv: list[str]) -> int:
    modulo, _ = disponiveis()[nome]
    principal = importlib.import_module(modulo).main
    original = list(sys.argv)
    sys.argv = [f"pfc {nome}", *argv]   # o argparse do destino mostra "pfc <subcomando>" na ajuda
    try:
        return int(principal(argv) or 0)
    finally:
        sys.argv = original


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "ajuda"):
        print(ajuda())
        return 0
    nome, resto = argv[0], argv[1:]
    if nome == "abordagens":
        return listar_abordagens(resto)
    if nome == "api":
        return servir(resto)
    if nome in disponiveis():
        return delegar(nome, resto)
    print(f"pfc: subcomando desconhecido: {nome!r}\n", file=sys.stderr)
    print(ajuda(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
