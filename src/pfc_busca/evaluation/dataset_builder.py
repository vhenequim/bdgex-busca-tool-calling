"""Constrói `data/dataset.json` — as 310 consultas do dataset de avaliação.

    pfc-dataset                                # gera data/dataset.json + data/dataset_resumo.md
    pfc-dataset --apendice ../paper_revisado   # regera os blocos do Apêndice A do texto

Fonte única: camadas P e N em `manual_cases.py`; camada G em
`scripts/generate_dataset_paper.py` (o mesmo arquivo copiado para o texto como
`generate_dataset.py`, semente 42). O Apêndice A é gerado a partir desta mesma
fonte, de modo que o PDF e o JSON não podem divergir.

Cada caso sai com: id, origem, família, categorias, consulta, esperado (leitura
preferencial), trocas, alternativas (leituras expandidas), fonte (rastreabilidade),
espera_tool_call, observacional, notas.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from types import ModuleType

from pfc_busca import schema
from pfc_busca.evaluation import gabarito, relative_time
from pfc_busca.evaluation.manual_cases import CASOS_MANUAIS
from pfc_busca.evaluation.relative_time import existe as regra_existe

RAIZ_REPO = Path(__file__).resolve().parents[3]
CAMINHO_GERADOR = RAIZ_REPO / "scripts" / "generate_dataset_paper.py"
CAMINHO_SAIDA = RAIZ_REPO / "data" / "dataset.json"
CAMINHO_RESUMO = RAIZ_REPO / "data" / "dataset_resumo.md"
# E: consulta subespecificada (lote de validação) — buscar ou pedir esclarecimento são ambos aceitos
CATEGORIAS_VALIDAS = {"S", "C", "M", "T", "O", "A", "F", "E"}


def normalizar_consulta(texto: str) -> str:
    sem_acento = "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                         if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", sem_acento).split())


def carregar_gerador(caminho: Path = CAMINHO_GERADOR) -> ModuleType:
    spec = importlib.util.spec_from_file_location("gerador_dataset", caminho)
    modulo = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(modulo)
    return modulo


def _completar(c: dict) -> dict:
    c = dict(c)
    c.setdefault("trocas", [])
    c["alternativas"] = gabarito.expandir_trocas(c["esperado"], c["trocas"])
    return c


def construir() -> tuple[list[dict], ModuleType, dict[str, list[dict]]]:
    gerador = carregar_gerador()
    familias = gerador.gerar()
    casos = [_completar(c) for c in CASOS_MANUAIS]
    for prefixo, lista in familias.items():
        for c in lista:
            casos.append(_completar({
                "id": c["id"], "origem": "G", "familia": prefixo, "categorias": c["categorias"],
                "consulta": c["consulta"], "esperado": c["esperado"], "trocas": c["trocas"],
                "fonte": f"generate_dataset.py:{c['funcao']} · modelo \"{c['modelo']}\" · semente {gerador.SEMENTE}",
                "espera_tool_call": c["espera_tool_call"], "observacional": c["observacional"],
                "notas": c["notas"],
            }))
    return casos, gerador, familias


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------

def _problemas_valor(rotulo: str, campo: str, valor) -> list[str]:
    problemas = []
    if gabarito.eh_opcional(valor):
        return _problemas_valor(rotulo, campo, valor[gabarito.OPCIONAL])
    if gabarito.eh_um_de(valor):
        if len(valor[gabarito.UM_DE]) < 2:
            problemas.append(f"{rotulo}: {campo} com $um_de de um só valor")
        for v in valor[gabarito.UM_DE]:
            problemas += _problemas_valor(rotulo, campo, v)
        return problemas
    enum = schema.valores_validos(campo)
    if enum is not None and valor not in enum:
        problemas.append(f"{rotulo}: {campo}={valor!r} fora do enumerado")
    if campo in schema.CAMPOS_PERIODO:
        if not isinstance(valor, dict):
            problemas.append(f"{rotulo}: {campo} não é objeto")
        elif "rel" in valor:
            if not regra_existe(valor["rel"]):
                problemas.append(f"{rotulo}: regra desconhecida {valor['rel']}")
        elif not set(valor) <= {"start", "end"} or not valor:
            problemas.append(f"{rotulo}: {campo} com chaves inválidas {sorted(valor)}")
    if campo in schema.CAMPOS_INTEIRO and not isinstance(valor, int):
        problemas.append(f"{rotulo}: {campo} não é inteiro")
    if campo in schema.CAMPOS_TEXTO_LIVRE and not isinstance(valor, str):
        problemas.append(f"{rotulo}: {campo} não é texto")
    return problemas


def validar(casos: list[dict]) -> list[str]:
    """Lista de problemas; vazia quando o dataset está consistente."""
    problemas: list[str] = []
    for id_, n in Counter(c["id"] for c in casos).items():
        if n > 1:
            problemas.append(f"id duplicado: {id_}")
    por_texto: dict[str, list[str]] = {}
    for c in casos:
        por_texto.setdefault(normalizar_consulta(c["consulta"]), []).append(c["id"])
    for texto, ids in por_texto.items():
        if len(ids) > 1:
            problemas.append(f"consulta repetida {ids}: {texto!r}")
    for c in casos:
        rotulo = c["id"]
        if not c["categorias"] or not set(c["categorias"]) <= CATEGORIAS_VALIDAS:
            problemas.append(f"{rotulo}: categorias inválidas {c['categorias']}")
        if not c["consulta"].strip():
            problemas.append(f"{rotulo}: consulta vazia")
        if not c.get("fonte"):
            problemas.append(f"{rotulo}: sem fonte (rastreabilidade)")
        for leitura in [c["esperado"]] + c["alternativas"]:
            for campo, valor in leitura.items():
                if campo not in schema.CAMPOS:
                    problemas.append(f"{rotulo}: campo fora do schema: {campo}")
                    continue
                problemas += _problemas_valor(rotulo, campo, valor)
        for origem, destino in c["trocas"]:
            if origem not in c["esperado"]:
                problemas.append(f"{rotulo}: troca {origem}->{destino} sem o campo de origem")
        if c["espera_tool_call"] and not c["esperado"] and not c.get("aceita_nao_chamar"):
            problemas.append(f"{rotulo}: espera tool call mas gabarito vazio")
        if not c["espera_tool_call"] and c["esperado"]:
            problemas.append(f"{rotulo}: 'não chamar' deve ter gabarito vazio")
        if ("F" in c["categorias"]) != (not c["espera_tool_call"] and not c["observacional"]):
            problemas.append(f"{rotulo}: categoria F é exatamente 'não chamar' fora dos observacionais")
        if "F" in c["categorias"] and len(c["categorias"]) > 1:
            problemas.append(f"{rotulo}: categoria F não se combina com outras")
        for hoje in (date(2026, 1, 1), date(2026, 9, 24), date(2028, 2, 29)):
            for leitura in gabarito.resolver_leituras(c, hoje):
                for campo in schema.CAMPOS_PERIODO:
                    if campo in leitura:
                        for p in gabarito.valores_aceitos(leitura[campo]):
                            if not (isinstance(p, dict) and p and set(p) <= {"start", "end"}):
                                problemas.append(f"{rotulo}: {campo} não resolve em {hoje}")
    return problemas


# ---------------------------------------------------------------------------
# Resumo
# ---------------------------------------------------------------------------

def resumo_markdown(casos: list[dict]) -> str:
    principais = [c for c in casos if not c["observacional"]]
    observacionais = [c for c in casos if c["observacional"]]
    com_alternativa = [c for c in principais if c["alternativas"] or any(
        gabarito.eh_um_de(v) or gabarito.eh_opcional(v) for v in c["esperado"].values())]
    linhas = [
        "# Dataset de avaliação — resumo",
        "",
        f"Gerado em {datetime.now():%Y-%m-%d %H:%M}. Total: **{len(casos)}** consultas "
        f"({len(principais)} nas métricas principais, {len(observacionais)} observacionais). "
        f"Com mais de uma leitura aceita: {len(com_alternativa)}.",
        "",
        "## Por origem e família",
        "",
        "| Família | Casos | Observacionais | Com leitura alternativa |",
        "|---|---|---|---|",
    ]
    for fam in sorted({c["familia"] for c in casos}, key=lambda f: ("PNG".index(f[0]), f)):
        sub = [c for c in casos if c["familia"] == fam]
        linhas.append(f"| {fam} | {len(sub)} | {sum(c['observacional'] for c in sub)} | "
                      f"{sum(c in com_alternativa for c in sub)} |")
    linhas += ["", "## Categorias × origem (métricas principais; uma consulta pode ter várias)", "",
               "| Categoria | P | N | G | Total |", "|---|---|---|---|---|"]
    for cat in "SCMTOAF":
        conta = {o: sum(1 for c in principais if cat in c["categorias"] and c["origem"] == o) for o in "PNG"}
        linhas.append(f"| {cat} | {conta['P']} | {conta['N']} | {conta['G']} | {sum(conta.values())} |")
    freq = Counter(campo for c in principais for campo in c["esperado"])
    linhas += ["", "## Frequência de cada campo na leitura preferencial (métricas principais)", "",
               "| Campo | Ocorrências |", "|---|---|"]
    linhas += [f"| {campo} | {freq.get(campo, 0)} |" for campo in schema.CAMPOS]
    linhas += ["", "## Observacionais", "", "| ID | Consulta | Motivo |", "|---|---|---|"]
    linhas += [f"| {c['id']} | {c['consulta']} | {c['notas']} |" for c in observacionais]
    return "\n".join(linhas) + "\n"



NOMES_FAMILIA = {"P": "Protótipo do 1º CGEO (P)", "N": "Autores (N)", "GS": "Geradas --- simples (G-S)",
                 "GC": "Geradas --- compostas (G-C)", "GM": "Geradas --- código MI/INOM (G-M)",
                 "GT": "Geradas --- tempo relativo (G-T)", "GO": "Geradas --- ordenação (G-O)",
                 "GA": "Geradas --- informais (G-A)", "GP": "Geradas --- amplas (G-P)",
                 "GF": "Geradas --- fronteira (G-F)"}
NOMES_CATEGORIA = {"S": "Simples", "C": "Compostas", "M": "Código MI/INOM", "T": "Tempo relativo",
                   "O": "Ordenação", "A": "Ambíguas/informais", "F": "Fora do domínio"}


def _tem_leitura_alternativa(c: dict) -> bool:
    """Alternativas explícitas ou regra de tempo relativo com mais de uma leitura aceita."""
    if c["alternativas"] or any(gabarito.eh_um_de(v) or gabarito.eh_opcional(v) for v in c["esperado"].values()):
        return True
    return any(gabarito.eh_rel(v) and len(relative_time.leituras(v["rel"], date(2026, 9, 24))) > 1
               for v in c["esperado"].values())


def tabelas_latex(casos: list[dict]) -> dict[str, str]:
    """Tabelas do Cap. 3 geradas a partir do dataset (nenhum número digitado à mão)."""
    principais = [c for c in casos if not c["observacional"]]
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              r"\caption{Composição do \textit{dataset} de avaliação por origem e família}",
              r"\label{tab:dataset-composicao}", r"\small",
              r"\begin{tabular}{|l|>{\centering\arraybackslash}p{1.9cm}|>{\centering\arraybackslash}p{2.3cm}|>{\centering\arraybackslash}p{2.9cm}|}", r"\hline",
              r"\textbf{Origem / família} & \textbf{Consultas} & \textbf{Observa\-cionais} & \textbf{Com mais de uma leitura aceita} \\",
              r"\hline"]
    for fam in ["P", "N", "GS", "GC", "GM", "GT", "GO", "GA", "GP", "GF"]:
        sub = [c for c in casos if c["familia"] == fam]
        linhas.append(f"{NOMES_FAMILIA[fam]} & {len(sub)} & {sum(c['observacional'] for c in sub)} & "
                      f"{sum(_tem_leitura_alternativa(c) for c in sub if not c['observacional'])} \\\\")
    linhas += [r"\hline",
               f"\\textbf{{Total}} & \\textbf{{{len(casos)}}} & \\textbf{{{sum(c['observacional'] for c in casos)}}} & "
               f"\\textbf{{{sum(_tem_leitura_alternativa(c) for c in principais)}}} \\\\",
               r"\hline", r"\end{tabular}",
               r"\fonte{Elaborada pelos autores a partir de \texttt{dataset.json}.}", r"\end{table}"]
    composicao = "\n".join(linhas) + "\n"

    linhas = [r"\begin{table}[htbp!]", r"\centering",
              r"\caption{Consultas por categoria e por camada (métricas principais; uma consulta pode ter mais de uma categoria)}",
              r"\label{tab:dataset-categorias}", r"\small",
              r"\begin{tabular}{|l|c|c|c|c|}", r"\hline",
              r"\textbf{Categoria} & \textbf{P} & \textbf{N} & \textbf{G} & \textbf{Total} \\", r"\hline"]
    for cat in "SCMTOAF":
        conta = {o: sum(1 for c in principais if cat in c["categorias"] and c["origem"] == o) for o in "PNG"}
        linhas.append(f"{NOMES_CATEGORIA[cat]} ({cat}) & {conta['P']} & {conta['N']} & {conta['G']} & "
                      f"{sum(conta.values())} \\\\")
    linhas += [r"\hline", r"\end{tabular}", r"\fonte{Elaborada pelos autores.}", r"\end{table}"]
    categorias = "\n".join(linhas) + "\n"

    freq = Counter(campo for c in principais for campo in c["esperado"])
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              r"\caption{Frequência de cada campo na leitura preferencial do gabarito (métricas principais)}",
              r"\label{tab:dataset-campos}", r"\small",
              r"\begin{tabular}{|l|c||l|c|}", r"\hline",
              r"\textbf{Campo} & \textbf{Ocorr.} & \textbf{Campo} & \textbf{Ocorr.} \\", r"\hline"]
    metade = (len(schema.CAMPOS) + 1) // 2
    for a, b in zip(schema.CAMPOS[:metade], schema.CAMPOS[metade:], strict=False):
        linhas.append(f"\\texttt{{{a}}} & {freq.get(a, 0)} & \\texttt{{{b}}} & {freq.get(b, 0)} \\\\")
    linhas += [r"\hline", r"\end{tabular}", r"\fonte{Elaborada pelos autores.}", r"\end{table}"]
    campos = "\n".join(linhas) + "\n"
    return {"tab_dataset_composicao.tex": composicao, "tab_dataset_categorias.tex": categorias,
            "tab_dataset_campos.tex": campos}

# ---------------------------------------------------------------------------
# Apêndice A
# ---------------------------------------------------------------------------

def _tipografia(texto: str) -> str:
    """Aspas simples retas viram aspas tipográficas do LaTeX ('x' -> `x'), e o rótulo (G-M) não quebra no sumário."""
    texto = re.sub(r"(?<![\w`'])'([^'\n{}\\]{1,60})'(?![\w])", r"`\1'", texto)
    return texto.replace(r"\textit{templates} (G-M)}", r"\textit{templates} \texorpdfstring{\mbox{(G-M)}}{(G-M)}}")


def emitir_apendice(gerador: ModuleType, casos: list[dict], familias: dict[str, list[dict]], destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    for origem, nome in (("P", "apendice_dataset_P.tex"), ("N", "apendice_dataset_N.tex")):
        blocos = ["% AUTO-GERADO por pfc-dataset --apendice a partir de manual_cases.py — não editar à mão", ""]
        blocos += [gerador.dtcase(c) for c in casos if c["origem"] == origem]
        (destino / nome).write_text(_tipografia("\n".join(blocos) + "\n"), encoding="utf-8")
    gerado = destino / "apendice_dataset_gerado.tex"
    gerador.emitir_apendice(familias, gerado)
    gerado.write_text(_tipografia(gerado.read_text(encoding="utf-8")), encoding="utf-8")
    (destino / "tabelas").mkdir(exist_ok=True)
    for nome, conteudo in tabelas_latex(casos).items():
        (destino / "tabelas" / nome).write_text(conteudo, encoding="utf-8")
    (destino / "generate_dataset.py").write_text(CAMINHO_GERADOR.read_text(encoding="utf-8"), encoding="utf-8")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def escrever_dataset(casos: list[dict], destino: Path = CAMINHO_SAIDA) -> str:
    destino.parent.mkdir(parents=True, exist_ok=True)
    corpo = {
        "fonte": "manual_cases.py (P01-P22, N01-N40) + generate_dataset.py semente 42 (G*)",
        "manual": "docs/manual_de_anotacao.md",
        "total": len(casos),
        "por_origem": dict(sorted(Counter(c["origem"] for c in casos).items())),
        "campos": schema.CAMPOS,
        "casos": casos,
    }
    texto = json.dumps(corpo, ensure_ascii=False, indent=2)
    destino.write_text(texto, encoding="utf-8", newline="\n")  # LF em qualquer SO: mesmo hash no Windows e no Linux
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def caminho_dataset() -> Path:
    """Dataset ativo: `data/dataset.json` ou o indicado em PFC_DATASET (ex.: o lote de validação)."""
    alternativo = os.environ.get("PFC_DATASET")
    if alternativo:
        p = Path(alternativo)
        return p if p.is_absolute() else RAIZ_REPO / p
    return CAMINHO_SAIDA


def carregar_dataset(caminho: Path | None = None) -> list[dict]:
    return json.loads((caminho or caminho_dataset()).read_text(encoding="utf-8-sig"))["casos"]


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Constrói o dataset de avaliação (310 consultas).")
    parser.add_argument("--saida", type=Path, default=CAMINHO_SAIDA)
    parser.add_argument("--apendice", type=Path, metavar="DIR_DO_TEXTO",
                        help="regera apendice_dataset_{P,N,gerado}.tex e generate_dataset.py no diretório do texto")
    args = parser.parse_args(argv)

    casos, gerador, familias = construir()
    problemas = validar(casos)
    if problemas:
        print("DATASET INCONSISTENTE:", file=sys.stderr)
        for p in problemas:
            print("  -", p, file=sys.stderr)
        return 1
    sha = escrever_dataset(casos, args.saida)
    CAMINHO_RESUMO.write_text(resumo_markdown(casos), encoding="utf-8")
    por_origem = Counter(c["origem"] for c in casos)
    print(f"✓ {len(casos)} consultas -> {args.saida.name} (P={por_origem['P']}, N={por_origem['N']}, "
          f"G={por_origem['G']}; {sum(c['observacional'] for c in casos)} observacionais; sha256 {sha[:12]})")
    if args.apendice:
        emitir_apendice(gerador, casos, familias, args.apendice)
        print(f"✓ Apêndice A regerado em {args.apendice}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
