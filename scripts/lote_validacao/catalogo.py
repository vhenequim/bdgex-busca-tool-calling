"""Leitura dos catálogos reais usados para sortear os alvos do lote de validação.

- BDGEx: metadados públicos coletados por `coletar_bdgex.py` (CSW). De cada registro saem,
  a partir do título e dos campos Dublin Core: nome da folha, código MI, código INOM,
  escala, tipo de produto (heurística documentada em `tipo_do_registro`), CGEO produtor e
  ano. Só servem para sortear valores realistas (folhas, códigos, escalas, combinações
  que existem no acervo); o gabarito de cada consulta continua definido pelo texto da
  consulta, segundo o manual de anotação.
- IBGE: lista oficial de municípios (API de localidades), para os alvos de município e
  para saber quando o nome de uma folha coincide com o de um município (manual,
  `keyword`: "folha Porto Velho" aceita também `city`).

    python scripts/lote_validacao/catalogo.py      # grava data/lote_validacao/bdgex_resumo.json
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DIR = RAIZ / "data" / "lote_validacao"   # catálogos: os mesmos para todos os lotes
DIR_CSW = DIR / "bdgex_csw"
ARQ_IBGE = DIR / "ibge_municipios.json"
ARQ_RESUMO = DIR / "bdgex_resumo.json"

RE_MI = re.compile(r"^(?:MI-?)?(\d{1,4}(?:-[1-4](?:-(?:NO|NE|SO|SE))?)?)$", re.I)
RE_INOM = re.compile(r"^[NS][A-Z]-\d{2}-[VXYZ](?:-[A-D](?:-(?:I|II|III|IV|V|VI)(?:-[1-4](?:-(?:NO|NE|SO|SE))?)?)?)?$")
RE_ESCALA = re.compile(r"(?:1:)?(\d{1,3})\.?(000)\b")
MINUSCULAS = {"de", "da", "do", "das", "dos", "e", "d"}


def _texto(v) -> str:
    if isinstance(v, dict):
        return v.get("#text", "") or ""
    if isinstance(v, list):
        return "; ".join(_texto(x) for x in v)
    return v or ""


def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def normalizar(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", sem_acento(s).lower()).split())


def nome_proprio(maiusculo: str) -> str:
    """'SÃO MIGUEL DO OESTE' -> 'São Miguel do Oeste'; "PAU D'ARCO" -> "Pau d'Arco"."""
    palavras = []
    for i, p in enumerate(maiusculo.strip().split()):
        base = p.lower()
        if "'" in base:
            a, b = base.split("'", 1)
            palavras.append(f"{a}'{b.capitalize()}" if a in MINUSCULAS else f"{a.capitalize()}'{b.capitalize()}")
        elif i and base in MINUSCULAS:
            palavras.append(base)
        else:
            palavras.append(base.capitalize())
    return " ".join(palavras)


def escala_canonica(texto: str) -> str | None:
    m = RE_ESCALA.search(texto.replace(" ", ""))
    if not m:
        return None
    valor = f"1:{m.group(1)}.000"
    return valor if valor in {"1:1.000", "1:2.000", "1:5.000", "1:10.000", "1:25.000", "1:50.000",
                              "1:100.000", "1:250.000"} else None


def tipo_do_registro(titulo: str, formato: str) -> str | None:
    """Tipo de produto do PFC para um registro do BDGEx (heurística sobre título e formato)."""
    t = sem_acento(titulo).upper()
    f = sem_acento(formato).upper()
    if t.startswith("MODELO DIGITAL DE SUPERFICIE"):
        return "MDS — RAM"
    if t.startswith("MODELO DIGITAL DE TERRENO"):
        return "MDT — RAM"
    if t.startswith("MOSAICO ORTORRETIFICADO") or t.startswith("ORTOIMAGEM") or "CARTA ORTOIMAGEM" in t:
        return "SCN Carta Ortoimagem"
    if "VETORIAL" in t or "SHAPE" in f:
        return "SCN Carta Topográfica Vetorial"
    if "TIF" in f or "PDF" in f or "GIF" in f or "MRSID" in f:
        return "SCN Carta Topográfica Matricial"
    return None


def cgeo_do_registro(criador: str) -> str | None:
    m = re.match(r"^([1-5])\s*[º°o]\s*Centro de Geoinforma", criador.strip())
    return f"{m.group(1)}° Centro de Geoinformação" if m else None


def carregar_bdgex() -> list[dict]:
    registros = []
    for arquivo in sorted(DIR_CSW.glob("pagina_*.json")):
        corpo = json.loads(arquivo.read_text(encoding="utf-8"))["csw:GetRecordsResponse"]["csw:SearchResults"]
        itens = corpo.get("csw:Record") or []
        registros += itens if isinstance(itens, list) else [itens]
    saida = []
    for r in registros:
        titulo = _texto(r.get("dc:title")).strip()
        partes = [p.strip() for p in titulo.split(" - ")]
        alternativo = _texto(r.get("dct:alternative")).strip()
        mi = inom = nome = None
        for p in partes:
            if RE_INOM.match(p.upper()):
                inom = p.upper()
            elif RE_MI.match(p) and not p.replace(".", "").isdigit() or re.match(r"^MI-", p, re.I):
                m = RE_MI.match(p)
                if m:
                    mi = m.group(1).upper()
        if mi is None and RE_MI.match(alternativo):
            mi = RE_MI.match(alternativo).group(1).upper()
        primeiro = partes[0] if partes else ""
        if (primeiro and not RE_MI.match(primeiro) and not RE_INOM.match(primeiro.upper())
                and not re.match(r"^MI-", primeiro, re.I) and tipo_do_registro(primeiro, "") is None
                and not sem_acento(primeiro).upper().startswith(("VAZIO", "CARTA ", "MOSAICO", "ORTOIMAGEM", "MODELO"))
                and len(partes) >= 2 and re.search(r"[A-Za-zÀ-ú]{3}", primeiro)):
            nome = nome_proprio(primeiro)
        ano = (_texto(r.get("dc:date")) or "")[:4]
        saida.append({
            "id": _texto(r.get("dc:identifier")),
            "titulo": titulo,
            "nome_folha": nome, "mi": mi, "inom": inom,
            "escala": escala_canonica(partes[-1]) if partes else None,
            "tipo": tipo_do_registro(titulo, _texto(r.get("dc:format"))),
            "cgeo": cgeo_do_registro(_texto(r.get("dc:creator"))),
            "ano": int(ano) if ano.isdigit() and 1900 <= int(ano) <= 2026 else None,
        })
    return saida


def carregar_ibge() -> list[dict]:
    municipios = json.loads(ARQ_IBGE.read_text(encoding="utf-8"))
    saida = []
    for m in municipios:
        uf = ((m.get("microrregiao") or {}).get("mesorregiao") or {}).get("UF") or \
             ((m.get("regiao-imediata") or {}).get("regiao-intermediaria") or {}).get("UF") or {}
        saida.append({"nome": m["nome"], "uf": uf.get("nome"), "sigla": uf.get("sigla")})
    return saida


def resumo(registros: list[dict]) -> dict:
    coleta = json.loads((DIR_CSW / "coleta.json").read_text(encoding="utf-8"))
    return {
        "fonte": coleta["servico"], "coletado_em": coleta["coletado_em"],
        "registros": len(registros), "paginas_sha256": [p["sha256"] for p in coleta["paginas"]],
        "com_nome_de_folha": sum(1 for r in registros if r["nome_folha"]),
        "nomes_de_folha_distintos": len({r["nome_folha"] for r in registros if r["nome_folha"]}),
        "com_mi": sum(1 for r in registros if r["mi"]), "com_inom": sum(1 for r in registros if r["inom"]),
        "por_escala": dict(Counter(r["escala"] or "(não identificada)" for r in registros).most_common()),
        "por_tipo_pfc": dict(Counter(r["tipo"] or "(não identificado)" for r in registros).most_common()),
        "por_cgeo": dict(Counter(r["cgeo"] or "(outro produtor)" for r in registros).most_common()),
        "por_decada": dict(sorted(Counter(f"{r['ano'] // 10 * 10}s" if r["ano"] else "(sem data)"
                                          for r in registros).items())),
    }


if __name__ == "__main__":
    regs = carregar_bdgex()
    r = resumo(regs)
    ARQ_RESUMO.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in r.items() if k != "paginas_sha256"}, ensure_ascii=False, indent=1))
