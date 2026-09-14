"""Constrói `data/dataset.json` — as 310 consultas do Apêndice A em forma legível por máquina.

    pfc-dataset                       # gera data/dataset.json + data/dataset_resumo.md
    pfc-dataset --verificar <apendice_dataset_gerado.tex>   # confere a amostra do PDF
    pfc-dataset --apendice  <apendice_dataset_gerado.tex>   # regera o .tex do paper

Camadas P e N vêm de `manual_cases.py`. A camada G vem do MESMO script que
gera o Apêndice A (`scripts/generate_dataset_paper.py`, cópia de
`paper_revisado/generate_dataset.py`), importado e executado na mesma ordem e
com a mesma semente (42): os IDs e as consultas do JSON são, por construção,
os do PDF. A única diferença é que aqui os parâmetros deixam de ser texto
LaTeX e viram dicionários.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from types import ModuleType

from pfc_busca import schema
from pfc_busca.evaluation.manual_cases import CASOS_MANUAIS
from pfc_busca.evaluation.relative_time import REGRAS, regra_de_descricao

RAIZ_REPO = Path(__file__).resolve().parents[3]
CAMINHO_GERADOR = RAIZ_REPO / "scripts" / "generate_dataset_paper.py"
CAMINHO_SAIDA = RAIZ_REPO / "data" / "dataset.json"
CAMINHO_RESUMO = RAIZ_REPO / "data" / "dataset_resumo.md"

CATEGORIAS_VALIDAS = {"S", "C", "M", "T", "O", "A"}

# Mesma ordem e mesmos prefixos do `main()` do gerador — NÃO reordenar.
FAMILIAS_G = [
    ("gen_simples", "GS"),
    ("gen_compostas", "GC"),
    ("gen_micodes", "GM"),
    ("gen_tempo", "GT"),
    ("gen_ordenacao", "GO"),
    ("gen_ambiguas_extras", "GA"),
    ("gen_multi_produto", "GP"),
    ("gen_fronteira", "GF"),
]
FAMILIAS_OBSERVACIONAIS = {"GF"}

_PERIODO_LITERAL = re.compile(r"^(\d{4}-\d{2}-\d{2}) a (\d{4}-\d{2}-\d{2})$")


# ---------------------------------------------------------------------------
# Camada G
# ---------------------------------------------------------------------------

def carregar_gerador(caminho: Path = CAMINHO_GERADOR) -> ModuleType:
    """Importa o gerador do paper sem executar o `main()` dele.

    O módulo faz `random.seed(42)` no import; os `gen_*` consomem o gerador
    global em sequência. Por isso ele é importado uma única vez por build.
    """
    spec = importlib.util.spec_from_file_location("gerador_paper", caminho)
    modulo = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(modulo)
    return modulo


def _parse_periodo(valor: str) -> dict:
    valor = " ".join(valor.split())
    m = _PERIODO_LITERAL.match(valor)
    if m:
        return {"start": m.group(1), "end": m.group(2)}
    regra = regra_de_descricao(valor)
    if regra is None:
        raise ValueError(f"descrição de tempo relativo sem regra: {valor!r}")
    return {"rel": regra}


def _parse_parametro(texto: str) -> tuple[str, object]:
    campo, sep, valor = texto.partition(": ")
    if not sep:
        raise ValueError(f"parâmetro sem separador ': ' -> {texto!r}")
    campo, valor = campo.strip(), valor.strip()
    if campo == "expected":
        return "__nota__", valor
    if campo in schema.CAMPOS_PERIODO:
        return campo, _parse_periodo(valor)
    if len(valor) >= 2 and valor[0] == '"' and valor[-1] == '"':
        return campo, valor[1:-1]
    if valor.isdigit():
        return campo, int(valor)
    raise ValueError(f"valor não reconhecido para {campo}: {valor!r}")


def _caso_g(id_: str, familia: str, consulta: str, cats: str, params: list[str]) -> dict:
    esperado: dict = {}
    notas: list[str] = []
    for texto in params:
        campo, valor = _parse_parametro(texto)
        if campo == "__nota__":
            notas.append(str(valor))
        else:
            esperado[campo] = valor
    return {
        "id": id_,
        "origem": "G",
        "familia": familia,
        "categorias": [c.strip() for c in cats.split("·")],
        "consulta": consulta,
        "esperado": esperado,
        "espera_tool_call": bool(esperado),
        "observacional": familia in FAMILIAS_OBSERVACIONAIS,
        "notas": "; ".join(notas),
    }


def gerar_camada_g(gerador: ModuleType) -> tuple[list[dict], dict[str, list]]:
    """Devolve os casos G e, para regerar o .tex, as tuplas brutas por família."""
    casos: list[dict] = []
    brutos: dict[str, list] = {}
    for nome_funcao, prefixo in FAMILIAS_G:
        tuplas = getattr(gerador, nome_funcao)()
        brutos[prefixo] = tuplas
        for indice, (consulta, cats, params) in enumerate(tuplas, start=1):
            casos.append(_caso_g(f"{prefixo}{indice:03d}", prefixo, consulta, cats, params))
    return casos, brutos


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------

def validar(casos: list[dict]) -> list[str]:
    """Lista de problemas; vazia quando o dataset está consistente."""
    problemas: list[str] = []
    ids = Counter(c["id"] for c in casos)
    for id_, n in ids.items():
        if n > 1:
            problemas.append(f"id duplicado: {id_}")
    for c in casos:
        rotulo = c["id"]
        if not set(c["categorias"]) <= CATEGORIAS_VALIDAS:
            problemas.append(f"{rotulo}: categorias inválidas {c['categorias']}")
        if not c["consulta"].strip():
            problemas.append(f"{rotulo}: consulta vazia")
        for campo, valor in c["esperado"].items():
            if campo not in schema.CAMPOS:
                problemas.append(f"{rotulo}: campo fora do schema: {campo}")
                continue
            enum = schema.valores_validos(campo)
            if enum is not None and valor not in enum:
                problemas.append(f"{rotulo}: {campo}={valor!r} fora do enum")
            if campo in schema.CAMPOS_PERIODO:
                if not isinstance(valor, dict):
                    problemas.append(f"{rotulo}: {campo} não é objeto")
                elif "rel" in valor and valor["rel"] not in REGRAS:
                    problemas.append(f"{rotulo}: regra desconhecida {valor['rel']}")
            if campo in schema.CAMPOS_INTEIRO and not isinstance(valor, int):
                problemas.append(f"{rotulo}: {campo} não é inteiro")
        if c["espera_tool_call"] and not c["esperado"]:
            problemas.append(f"{rotulo}: espera tool call mas gabarito vazio")
    return problemas


# ---------------------------------------------------------------------------
# Resumo e verificação contra o PDF
# ---------------------------------------------------------------------------

def resumo_markdown(casos: list[dict]) -> str:
    por_origem = Counter(c["origem"] for c in casos)
    por_familia = Counter(c["familia"] for c in casos)
    observacionais = [c for c in casos if c["observacional"]]
    principais = [c for c in casos if not c["observacional"]]
    linhas = [
        "# Dataset de avaliação — resumo",
        "",
        f"Gerado em {datetime.now():%Y-%m-%d %H:%M}. Total: **{len(casos)}** consultas "
        f"({len(principais)} nas métricas principais, {len(observacionais)} observacionais).",
        "",
        "## Por origem",
        "",
        "| Origem | Casos |", "|---|---|",
    ]
    linhas += [f"| {o} | {n} |" for o, n in sorted(por_origem.items())]
    linhas += ["", "## Por família", "", "| Família | Casos | Observacional |", "|---|---|---|"]
    for fam, n in sorted(por_familia.items()):
        obs = sum(1 for c in casos if c["familia"] == fam and c["observacional"])
        linhas.append(f"| {fam} | {n} | {obs} |")
    linhas += ["", "## Por categoria (uma consulta pode ter várias) × origem", "",
               "| Categoria | P | N | G | Total |", "|---|---|---|---|---|"]
    for cat in ["S", "C", "M", "T", "O", "A"]:
        conta = {o: sum(1 for c in principais if cat in c["categorias"] and c["origem"] == o)
                 for o in "PNG"}
        linhas.append(f"| {cat} | {conta['P']} | {conta['N']} | {conta['G']} | {sum(conta.values())} |")
    linhas += ["", "## Frequência de cada campo no gabarito (métricas principais)", "",
               "| Campo | Ocorrências |", "|---|---|"]
    freq = Counter(campo for c in principais for campo in c["esperado"])
    linhas += [f"| {campo} | {freq.get(campo, 0)} |" for campo in schema.CAMPOS]
    linhas += ["", "## Observacionais", "", "| ID | Consulta | Motivo |", "|---|---|---|"]
    linhas += [f"| {c['id']} | {c['consulta']} | {c['notas']} |" for c in observacionais]
    return "\n".join(linhas) + "\n"


_DTCASE = re.compile(r"\\dtcase\{([^}]*)\}\{([^}]*)\}\{(.*?)\}\{", re.S)


def _desescapar_latex(texto: str) -> str:
    return (texto.replace(r"\&", "&").replace(r"\_", "_")
            .replace(r"\%", "%").replace(r"\#", "#"))


def verificar_contra_apendice(casos: list[dict], caminho_tex: Path) -> list[str]:
    """Confere que cada `\\dtcase` do .tex tem o mesmo texto de consulta no JSON."""
    por_id = {c["id"]: c for c in casos}
    divergencias: list[str] = []
    conteudo = caminho_tex.read_text(encoding="utf-8")
    encontrados = 0
    for m in _DTCASE.finditer(conteudo):
        id_, _cats, consulta_tex = m.group(1), m.group(2), _desescapar_latex(m.group(3))
        encontrados += 1
        caso = por_id.get(id_)
        if caso is None:
            divergencias.append(f"{id_}: existe no .tex mas não no JSON")
        elif caso["consulta"] != consulta_tex:
            divergencias.append(f"{id_}: tex={consulta_tex!r} json={caso['consulta']!r}")
    if encontrados == 0:
        divergencias.append(f"nenhum \\dtcase encontrado em {caminho_tex}")
    return divergencias


def emitir_apendice(gerador: ModuleType, brutos: dict[str, list], destino: Path) -> None:
    """Regera o .tex do Apêndice A com o `emit_section` do próprio gerador."""
    nomes = {
        "GS": "Consultas simples geradas por \\textit{templates} (G-S)",
        "GC": "Consultas compostas geradas por \\textit{templates} (G-C)",
        "GM": "Consultas com c\\'odigo MI/INOM geradas por \\textit{templates} (G-M)",
        "GT": "Consultas com tempo relativo geradas por \\textit{templates} (G-T)",
        "GO": "Consultas com ordena\\c{c}\\~ao geradas por \\textit{templates} (G-O)",
        "GA": "Consultas amb\\'iguas/informais adicionais (G-A)",
        "GP": "Consultas multi-produto (G-P)",
        "GF": "Consultas de fronteira / erro esperado (G-F)",
    }
    total = sum(len(v) for v in brutos.values())
    partes = [f"% ─── AUTO-GERADO: {total} consultas por templates ───", ""]
    for _, prefixo in FAMILIAS_G:
        partes.append(gerador.emit_section(nomes[prefixo], brutos[prefixo], prefixo))
    partes.append(f"% Total gerado: {total}")
    partes.append("% Detalhamento:")
    partes += [f"%   {prefixo}: {len(brutos[prefixo])} consultas" for _, prefixo in FAMILIAS_G]
    destino.write_text("\n".join(partes) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def construir() -> tuple[list[dict], ModuleType, dict[str, list]]:
    gerador = carregar_gerador()
    casos_g, brutos = gerar_camada_g(gerador)
    casos = [dict(c) for c in CASOS_MANUAIS] + casos_g
    return casos, gerador, brutos


def escrever_dataset(casos: list[dict], destino: Path = CAMINHO_SAIDA) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    conteudo = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "fonte": "Apêndice A do PFC (P01-P22, N01-N40) + generate_dataset.py seed=42 (G*)",
        "total": len(casos),
        "por_origem": dict(sorted(Counter(c["origem"] for c in casos).items())),
        "campos": schema.CAMPOS,
        "casos": casos,
    }
    destino.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")


def carregar_dataset(caminho: Path = CAMINHO_SAIDA) -> list[dict]:
    return json.loads(caminho.read_text(encoding="utf-8-sig"))["casos"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Constrói o dataset de avaliação (310 consultas).")
    parser.add_argument("--saida", type=Path, default=CAMINHO_SAIDA)
    parser.add_argument("--verificar", type=Path, metavar="APENDICE.tex",
                        help="confere consultas do JSON contra os \\dtcase do .tex")
    parser.add_argument("--apendice", type=Path, metavar="DESTINO.tex",
                        help="regera o apendice_dataset_gerado.tex do paper")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    casos, gerador, brutos = construir()
    problemas = validar(casos)
    if problemas:
        print("DATASET INCONSISTENTE:", file=sys.stderr)
        for p in problemas:
            print("  -", p, file=sys.stderr)
        return 1

    escrever_dataset(casos, args.saida)
    CAMINHO_RESUMO.write_text(resumo_markdown(casos), encoding="utf-8")
    por_origem = Counter(c["origem"] for c in casos)
    print(f"✓ {len(casos)} consultas -> {args.saida.relative_to(RAIZ_REPO)} "
          f"(P={por_origem['P']}, N={por_origem['N']}, G={por_origem['G']}; "
          f"{sum(c['observacional'] for c in casos)} observacionais)")

    if args.verificar:
        divergencias = verificar_contra_apendice(casos, args.verificar)
        if divergencias:
            print("× divergências contra o apêndice:")
            for d in divergencias:
                print("  -", d)
            return 2
        print(f"✓ consultas conferem com {args.verificar.name}")

    if args.apendice:
        emitir_apendice(gerador, brutos, args.apendice)
        print(f"✓ apêndice regerado em {args.apendice}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
