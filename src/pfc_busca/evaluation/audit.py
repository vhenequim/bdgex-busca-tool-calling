"""pfc-auditar — auditoria automática do dataset de avaliação.

    pfc-auditar                          # escreve data/auditoria/{auditoria_casos.csv, relatorio_auditoria.md, auditoria.json}
    pfc-auditar --anotacao-independente data/auditoria/anotacao_independente.json

Etapa 1 do procedimento do manual de anotação (`docs/manual_de_anotacao.md`, §5):

1. Estrutura: ids únicos, consultas não repetidas, enumerados válidos, períodos que
   resolvem em datas diversas (reusa `dataset_builder.validar`).
2. Rastreabilidade: toda consulta tem fonte; as da camada P aparecem literalmente na
   linha citada de `test-cases.ts`.
3. Evidência: um anotador por REGRAS, escrito sem olhar o gabarito, extrai da consulta
   os parâmetros que o texto sustenta e o trecho que os sustenta. A comparação com o
   gabarito aponta: campo anotado sem evidência; evidência sem campo anotado; valor
   divergente.
4. Consistência: a mesma expressão (ex.: "detalhada", "mais recentes", "semana passada")
   precisa receber a mesma anotação em todos os casos.

Com `--anotacao-independente`, compara também o gabarito com uma segunda anotação,
feita às cegas a partir apenas do manual (etapa 2), e lista toda divergência para
adjudicação (etapa 3).

O anotador por regras é deliberadamente simples e conservador: um apontamento é um
convite à revisão humana, não um veredito.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from pfc_busca import schema
from pfc_busca.evaluation import gabarito, metrics
from pfc_busca.evaluation.dataset_builder import CAMINHO_SAIDA, RAIZ_REPO, carregar_dataset, validar

DIR_AUDITORIA = RAIZ_REPO / "data" / "auditoria"
ARQUIVO_P = RAIZ_REPO.parent / "prototipo_busca_llm-main" / "backend" / "evaluation" / "test-cases.ts"
DATA_REFERENCIA = date(2026, 9, 24)


def norm(texto: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")
    return " " + " ".join(re.sub(r"[^a-z0-9:.\- ]", " ", s).split()) + " "


# ---------------------------------------------------------------------------
# Léxico do domínio (independente do gabarito)
# ---------------------------------------------------------------------------

ESTADOS = {
    "Acre": ["acre"], "Alagoas": ["alagoas"], "Amapá": ["amapa"], "Amazonas": ["amazonas"],
    "Bahia": ["bahia"], "Ceará": ["ceara"], "Distrito Federal": ["distrito federal"],
    "Espírito Santo": ["espirito santo"], "Goiás": ["goias"], "Maranhão": ["maranhao"],
    "Mato Grosso do Sul": ["mato grosso do sul"], "Mato Grosso": ["mato grosso"],
    "Minas Gerais": ["minas gerais", "minas"], "Pará": ["para"], "Paraíba": ["paraiba"],
    "Paraná": ["parana"], "Pernambuco": ["pernambuco"], "Piauí": ["piaui"],
    "Rio Grande do Norte": ["rio grande do norte"], "Rio Grande do Sul": ["rio grande do sul"],
    "Rio de Janeiro": ["rio de janeiro"], "Rondônia": ["rondonia"], "Roraima": ["roraima"],
    "Santa Catarina": ["santa catarina"], "São Paulo": ["sao paulo"], "Sergipe": ["sergipe"],
    "Tocantins": ["tocantins"],
}
SIGLAS = {"ac": "Acre", "al": "Alagoas", "ap": "Amapá", "am": "Amazonas", "ba": "Bahia", "ce": "Ceará",
          "df": "Distrito Federal", "es": "Espírito Santo", "go": "Goiás", "ma": "Maranhão", "mt": "Mato Grosso",
          "ms": "Mato Grosso do Sul", "mg": "Minas Gerais", "pa": "Pará", "pb": "Paraíba", "pr": "Paraná",
          "pe": "Pernambuco", "pi": "Piauí", "rj": "Rio de Janeiro", "rn": "Rio Grande do Norte",
          "rs": "Rio Grande do Sul", "ro": "Rondônia", "rr": "Roraima", "sc": "Santa Catarina",
          "sp": "São Paulo", "to": "Tocantins"}
MUNICIPIOS = {"Brasília": "brasilia", "Manaus": "manaus", "Porto Velho": "porto velho", "Cuiabá": "cuiaba",
              "Fortaleza": "fortaleza", "Salvador": "salvador", "Belo Horizonte": "belo horizonte",
              "Curitiba": "curitiba", "Porto Alegre": "porto alegre", "Recife": "recife",
              "Goiânia": "goiania", "Belém": "belem"}
ESTADO_OU_CAPITAL = {"Rio de Janeiro", "São Paulo"}
REGIOES = ["amazonia legal", "nordeste", "sudeste", "sul", "norte", "centro-oeste"]

PROJETOS = [
    ("Base Cartográfica Digital da Bahia", ["base cartografica digital da bahia", "bcd da bahia", "bcd bahia"]),
    ("Base Cartográfica Digital de Rondônia", ["base cartografica digital de rondonia", "bcd de rondonia",
                                               "bcd rondonia", "projeto rondonia"]),
    ("Base Cartográfica Digital do Amapá", ["base cartografica digital do amapa", "bcd do amapa", "bcd amapa"]),
    ("Mapeamento Sistemático", ["mapeamento sistematico", "cartografia sistematica"]),
    ("Olimpíadas Rio 2016", ["olimpiadas", "rio 2016", "jogos olimpicos"]),
    ("Copa do Mundo 2014", ["copa do mundo", "copa 2014"]),
    ("Copa das Confederações", ["copa das confederacoes"]),
    ("NGA-BECA", ["nga-beca", "beca"]),
    ("AMAN", ["aman"]),
]

TIPOS = [
    ("SCN Carta Ortoimagem Banda P Pol HH", [r"banda p\b"]),
    ("SCN Carta Ortoimagem Banda X Pol HH", [r"banda x\b"]),
    ("SCN Carta Topográfica Vetorial", [r"vetoria"]),
    ("SCN Carta Topográfica Matricial", [r"topografic", r"\btopo\b"]),
    ("SCN Carta Ortoimagem", [r"ortoimg", r"ortoimage", r"\bortos?\b"]),
    ("MDT — RAM", [r"\bmdts?\b", r"modelos? digita(?:l|is) d[oe] terreno"]),
    ("MDS — RAM", [r"\bmdss?\b", r"modelos? digita(?:l|is) de superficie"]),
    ("CIRC", [r"\bcirc\b"]),
    ("Cartas Temáticas Não SCN", [r"tematic"]),
]

ORDINAIS = {"primeiro": 1, "segundo": 2, "terceiro": 3, "quarto": 4, "quinto": 5, "dois": 2}
NUMEROS = {"tres": 3, "cinco": 5, "dez": 10, "dois": 2, "quatro": 4}
ESCALAS_GRANDES = ["1:25.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000"]

TEMPOS = [  # (regex sobre texto normalizado, regra ou função)
    (r"segundo semestre (?:do ano )?passado", "segundo_semestre_anterior"),
    (r"ultimo trimestre do ano passado", "ultimo_trimestre_ano_anterior"),
    (r"primeiro trimestre", "primeiro_trimestre_corrente"),
    (r"trimestre passado", "trimestre_anterior"),
    (r"\b(?:esse|este|deste|neste) ano\b", "ano_corrente"),
    (r"\bano passado\b", "ano_anterior"),
    (r"\b2 anos atras\b", "dois_anos_atras"),
    (r"\bmes passado\b", "mes_anterior"),
    (r"\b(?:este|deste|neste) mes\b", "mes_corrente"),
    (r"\bsemana passada\b", "semana_passada"),
    (r"\b(?:esta|desta|nesta) semana\b", "semana_corrente"),
    (r"\bhoje\b", "hoje"),
    (r"ultimos 3 meses", "ultimos_3_meses"),
    (r"ultimos 6 meses", "ultimos_6_meses"),
    (r"ultimos 5 anos", "ultimos_5_anos"),
    (r"\bdesde (\d{4})\b", "desde_{0}"),
    (r"\bdepois de (\d{4})\b", "depois_de_{0}"),
    (r"\bantes de (\d{4})\b", "antes_de_{0}"),
]
FORA_DO_DOMINIO = [r"fora do brasil", r"argentina", r"marte", r"previsao do tempo", r"quanto custa",
                   r"tesouro", r"\bme ajuda\b", r"mapa bonito", r"oceano", r"futuro", r"estado 42",
                   r"1:10\.000\.000"]


@dataclass
class Evidencia:
    campo: str
    valores: list[Any]          # valores que o trecho sustenta (mais de um = ambíguo)
    trecho: str
    fraca: bool = False         # evidência que depende de convenção de ordenação/limite


@dataclass
class Extracao:
    evidencias: dict[str, Evidencia] = field(default_factory=dict)
    fora_do_dominio: str | None = None
    campos_opcionais: set[str] = field(default_factory=set)

    def por(self, campo: str, valores: list[Any], trecho: str, fraca: bool = False) -> None:
        atual = self.evidencias.get(campo)
        if atual:
            for v in valores:
                if v not in atual.valores:
                    atual.valores.append(v)
            atual.trecho += " | " + trecho.strip()
        else:
            self.evidencias[campo] = Evidencia(campo, list(valores), trecho.strip(), fraca)


# ---------------------------------------------------------------------------
# Anotador por regras
# ---------------------------------------------------------------------------

def _escala_de_numero(digitos: str) -> str | None:
    n = int(re.sub(r"\D", "", digitos))
    return f"1:{n:,}".replace(",", ".") if f"1:{n:,}".replace(",", ".") in schema.ESCALAS else None


def extrair(consulta: str) -> Extracao:
    ex = Extracao()
    t = norm(consulta)
    original = consulta

    for padrao in FORA_DO_DOMINIO:
        if re.search(padrao, t):
            ex.fora_do_dominio = padrao
            break

    # --- projeto (antes de estados, porque nomes de projeto contêm UFs) ---
    for nome, apelidos in PROJETOS:
        for ap in apelidos:
            if re.search(rf"\b{re.escape(ap)}\b", t):
                ex.por("project", [nome], ap)
                t = t.replace(ap, " " * len(ap))
                break

    # --- keyword: MI, INOM, nome de carta ---
    inom = re.findall(r"\b(s[a-h])-?(\d{2})(?:-?([v-z]))?(?:-?([a-d]))?(?:-?([iv]{1,3}|vi))?(?:-?([1-4]))?(?:-?(no|ne|so|se))?\b", t)
    for partes in inom:
        codigo = "-".join(p.upper() for p in partes if p)
        ex.por("keyword", [codigo], codigo)
    t_sem_inom = re.sub(r"\bs[a-h]-?\d{2}[a-z0-9\-]*", " ", t)
    for m in re.finditer(r"\b(?:mi|carta|folha)\s+(\d{1,4}(?:-[1-4])?(?:-(?:no|ne|so|se))?)\b", t_sem_inom):
        ex.por("keyword", [m.group(1).upper()], m.group(0))
    for m in re.finditer(r"\b(?:carta|folha)(?:\s+[a-zà-ú]+)*?\s+((?:[A-ZÀ-Ú][a-zà-ú]+)(?:\s+(?:d[aeo]s?\s+)?[A-ZÀ-Ú][a-zà-ú]+)+)",
                         original):
        ex.por("keyword", [m.group(1)], m.group(0))

    # --- escala ---
    for m in re.finditer(r"\b1\s*:\s*(\d{1,3}(?:[.]?\d{3})+)\b", t):
        e = _escala_de_numero(m.group(1))
        if e:
            ex.por("scale", [e], m.group(0))
    for m in re.finditer(r"\b(\d{1,3})\s*k\b", t):
        e = _escala_de_numero(m.group(1) + "000")
        if e:
            ex.por("scale", [e], m.group(0))
    if re.search(r"\bcem k\b", t):
        ex.por("scale", ["1:100.000"], "cem k")
    for m in re.finditer(r"\bescala de (\d{1,3}) mil\b", t):
        e = _escala_de_numero(m.group(1) + "000")
        if e:
            ex.por("scale", [e], m.group(0))
    if re.search(r"detalhad", t) and not re.search(r"\(25k ou 50k\)", t):
        ex.por("scale", ["1:25.000"], "detalhada")
    if "pequena escala" in t:
        ex.por("scale", ["1:250.000"], "pequena escala")
    if "media escala" in t:
        ex.por("scale", ["1:50.000", "1:100.000"], "média escala")
    if "grande escala" in t:
        ex.por("scale", ESCALAS_GRANDES, "grande escala")
    if re.search(r"maior que 100k", t):
        ex.evidencias.pop("scale", None)
        ex.por("scale", ["1:50.000"] + ESCALAS_GRANDES, "maior que 100k")

    # --- tipo de produto ---
    for nome, padroes in TIPOS:
        achou = next((re.search(p, t) for p in padroes if re.search(p, t)), None)
        if achou:
            if nome == "SCN Carta Ortoimagem" and "productType" in ex.evidencias:
                continue  # banda P/X já capturada
            if nome == "SCN Carta Topográfica Matricial" and "productType" in ex.evidencias:
                continue  # vetorial já capturada
            ex.por("productType", [nome], achou.group(0))

    # --- CGEO ---
    for m in re.finditer(r"\b([1-5])\s*(?:o|º|°)?\s*cgeo\b", t):
        ex.por("supplyArea", [schema.CENTROS_GEOINFORMACAO[int(m.group(1)) - 1]], m.group(0))
    for palavra, n in ORDINAIS.items():
        m = re.search(rf"\b{palavra} cgeo\b", t)
        if m:
            ex.por("supplyArea", [schema.CENTROS_GEOINFORMACAO[n - 1]], m.group(0))
    for m in re.finditer(r"\b([1-5])\s*centro de geoinformacao\b", t):
        ex.por("supplyArea", [schema.CENTROS_GEOINFORMACAO[int(m.group(1)) - 1]], m.group(0))

    # --- estado / município ---
    t_geo = t
    for padrao in (r"\brio 2016\b",):
        t_geo = re.sub(padrao, " ", t_geo)
    achados_estado: list[tuple[str, str]] = []
    for nome, apelidos in ESTADOS.items():
        for ap in apelidos:
            if re.search(rf"\b{re.escape(ap)}\b", t_geo):
                if nome == "Mato Grosso" and "mato grosso do sul" in t_geo:
                    continue
                if nome == "Pará" and re.search(r"\bpara\b(?! (?:a|o)\b)", t_geo) is None:
                    continue
                achados_estado.append((nome, ap))
                break
    tokens_orig = re.findall(r"[A-Za-zÀ-ú]+", original)
    for i, tok in enumerate(tokens_orig):
        low = tok.lower()
        if low in SIGLAS:
            anterior = tokens_orig[i - 1].lower() if i else ""
            if tok.isupper() or anterior in {"de", "do", "da", "no", "na", "em"} or i == len(tokens_orig) - 1:
                if low in {"se", "to", "pa", "ma", "al", "es", "am", "go"} and not tok.isupper() and \
                        anterior not in {"de", "do", "da", "no", "na", "em"}:
                    continue
                achados_estado.append((SIGLAS[low], tok))
    rio_sozinho = re.search(r"\brio\b(?! de janeiro| grande)", t_geo)
    for nome, trecho in achados_estado:
        if nome in ESTADO_OU_CAPITAL and trecho.lower() == trecho and len(trecho) > 2 or \
                (nome in ESTADO_OU_CAPITAL and not trecho.isupper() and len(trecho) > 2):
            ex.por("state|city", [nome], trecho)
        else:
            ex.por("state", [nome], trecho)
    if rio_sozinho and not any(n == "Rio de Janeiro" for n, _ in achados_estado):
        ex.por("state|city", ["Rio de Janeiro"], "rio")
    for nome, forma in MUNICIPIOS.items():
        if re.search(rf"\b{forma}\b", t_geo):
            ex.por("city", [nome], forma)
    t_regiao = re.sub(r"rio grande do (?:sul|norte)|mato grosso do sul", " ", t_geo)
    for regiao in REGIOES:
        if re.search(rf"\b(?:do|da|no|na) {regiao}\b", t_regiao):
            ex.por("__regiao__", [regiao], regiao)

    # --- período ---
    verbo_pub = re.search(r"\b(?:publicad|lancad)\w*", t)
    verbo_cri = re.search(r"\b(?:criad|feit|elaborad|produzid)\w*", t)
    campo_per: list[str]
    if verbo_pub and not verbo_cri:
        campo_per = ["publicationPeriod"]
    elif verbo_cri and not verbo_pub:
        campo_per = ["creationPeriod"]
    else:
        campo_per = ["publicationPeriod", "creationPeriod"]
    per_valor, per_trecho = None, ""
    m = re.search(r"\bentre (\d{4}) e (\d{4})\b", t)
    if m:
        per_valor, per_trecho = {"start": f"{m.group(1)}-01-01", "end": f"{m.group(2)}-12-31"}, m.group(0)
    if per_valor is None:
        m = re.search(r"\b(?:em|ano|de) (\d{4})\b", t)
        if m and not re.search(r"\b(?:desde|depois de|antes de) \d{4}", t) and not re.search(r"rio 2016|copa 2014", t):
            per_valor, per_trecho = {"start": f"{m.group(1)}-01-01", "end": f"{m.group(1)}-12-31"}, m.group(0)
    if per_valor is None:
        for padrao, regra in TEMPOS:
            m = re.search(padrao, t)
            if m:
                per_valor, per_trecho = {"rel": regra.format(*m.groups())}, m.group(0)
                break
    if per_valor is not None:
        for c in campo_per:
            ex.por(c if len(campo_per) == 1 else "publicationPeriod|creationPeriod", [per_valor], per_trecho)
            if len(campo_per) > 1:
                break

    # --- ordenação e limite ---
    t_ord = re.sub(r"ultim[oa]s \d+ (?:meses|anos|dias)|(?:primeiro|ultimo|segundo) (?:trimestre|semestre)|"
                   r"primeiro cgeo|primeiro centro", " ", t)
    if re.search(r"da mais nova para a mais antiga", t_ord):
        desc, asc = re.search(r"mais nova", t_ord), None
    else:
        desc = re.search(r"mais recente|mais nova|\bultim\w*|atuais", t_ord)
        asc = re.search(r"mais antig\w*|\bprimeir\w*|ordem cronologica", t_ord)
    t = t_ord
    if desc or asc:
        ex.por("sortDirection", ["DESC" if desc else "ASC"], (desc or asc).group(0), fraca=True)
        pista_cri = re.search(r"(?:primeir\w*|ultim\w*)(?: \w+){0,3} (?:produzid|criad|elaborad)\w*|criad\w* mais recentemente|"
                              r"mapeamento feito|atualizac", t)
        pista_pub = re.search(r"publicacoes mais recentes|ultim\w*(?: \w+){0,3} publicad\w*|ultimas? \d* ?publicacoes|"
                              r"cronologica de publicacao", t)
        if pista_cri and not pista_pub:
            ex.por("sortField", ["creationDate"], pista_cri.group(0), fraca=True)
        elif pista_pub and not pista_cri:
            ex.por("sortField", ["publicationDate"], pista_pub.group(0), fraca=True)
        else:
            ex.por("sortField", ["publicationDate", "creationDate"], "(sem pista ligada à ordenação)", fraca=True)
        m = re.search(r"\b(\d{1,3})\s+(?:cartas|primeir\w*|ultim\w*|publicac\w*|produtos|ortoimagens|mais|\w+ mais)", t)
        if m:
            ex.por("limit", [int(m.group(1))], m.group(0), fraca=True)
        else:
            for palavra, n in NUMEROS.items():
                m = re.search(rf"\b{palavra}\s+(?:produtos|cartas|\w+)\s+mais", t)
                if m:
                    ex.por("limit", [n], m.group(0), fraca=True)
                    break
            else:
                singular = re.search(r"\b(?:a|o)\s+(?:\w+\s+)?(?:mais recente|mais antiga|primeir[ao]|ultim[ao])\b|"
                                     r"^ ?(?:primeiro|ultima)\b|\bcarta mi \S+ mais recente", t)
                if singular:
                    ex.campos_opcionais.add("limit")
    return ex


# ---------------------------------------------------------------------------
# Comparação com o gabarito
# ---------------------------------------------------------------------------

def _aceitos_no_gabarito(caso: dict, campo: str) -> list[Any]:
    """Todos os valores aceitos para `campo` em qualquer leitura (resolvidos para a data de referência)."""
    valores: list[Any] = []
    for leitura in [caso["esperado"]] + caso["alternativas"]:
        if campo in leitura:
            valores += gabarito.valores_aceitos(leitura[campo])
    return valores


def _mesmo(campo: str, a: Any, b: Any) -> bool:
    if campo in schema.CAMPOS_PERIODO and isinstance(a, dict) and isinstance(b, dict):
        if "rel" in a or "rel" in b:
            ra = gabarito.resolver_gabarito({campo: a}, DATA_REFERENCIA)[campo]
            rb = gabarito.resolver_gabarito({campo: b}, DATA_REFERENCIA)[campo]
            return any(x in gabarito.valores_aceitos(rb) for x in gabarito.valores_aceitos(ra))
        return a == b
    return metrics.campo_igual(campo, a, b)


def comparar(caso: dict, ex: Extracao) -> list[dict]:
    """Apontamentos (dicts com tipo, campo, detalhe) do confronto regra × gabarito."""
    ap: list[dict] = []
    if not caso["espera_tool_call"]:
        if not ex.fora_do_dominio:
            ap.append({"tipo": "fora_do_dominio_sem_marcador", "campo": "-", "detalhe": "gabarito diz 'não chamar'"})
        return ap
    if ex.fora_do_dominio and not caso["observacional"]:
        ap.append({"tipo": "marcador_de_fronteira", "campo": "-", "detalhe": ex.fora_do_dominio})

    campos_gab: set[str] = set()
    for leitura in [caso["esperado"]] + caso["alternativas"]:
        campos_gab |= set(leitura)

    usados: set[str] = set()
    for chave, ev in ex.evidencias.items():
        if chave == "__regiao__":
            if "state" in caso["esperado"]:
                ap.append({"tipo": "regiao_anotada_como_estado", "campo": "state", "detalhe": ev.trecho})
            continue
        candidatos = chave.split("|")
        presentes = [c for c in candidatos if c in campos_gab]
        if not presentes:
            ap.append({"tipo": "evidencia_nao_anotada", "campo": chave,
                       "detalhe": f"{ev.trecho} → {ev.valores}"})
            continue
        for c in presentes:
            usados.add(c)
            aceitos = _aceitos_no_gabarito(caso, c)
            if not any(_mesmo(c, v, g) for v in ev.valores for g in aceitos):
                ap.append({"tipo": "valor_divergente", "campo": c,
                           "detalhe": f"texto sustenta {ev.valores} ('{ev.trecho}'); gabarito aceita {aceitos}"})
            elif len(ev.valores) > 1 and c == "sortField" and not gabarito.eh_um_de(caso["esperado"].get(c)):
                ap.append({"tipo": "ambiguidade_nao_registrada", "campo": c,
                           "detalhe": f"sem pista ligada à ordenação, mas gabarito aceita só {aceitos}"})
            elif len(ev.valores) == 1 and c == "sortField" and gabarito.eh_um_de(caso["esperado"].get(c)):
                ap.append({"tipo": "pista_ignorada", "campo": c,
                           "detalhe": f"pista '{ev.trecho}' indica {ev.valores[0]}, gabarito aceita {aceitos}"})
        if len(candidatos) == 2 and len(presentes) == 1 and set(candidatos) != {"publicationPeriod", "creationPeriod"} \
                and not caso["alternativas"]:
            ap.append({"tipo": "ambiguidade_nao_registrada", "campo": chave,
                       "detalhe": f"'{ev.trecho}' admite {candidatos}, gabarito só {presentes}"})
        if set(candidatos) == {"publicationPeriod", "creationPeriod"} and len(presentes) == 1 \
                and not any(set(t) == {"publicationPeriod", "creationPeriod"} for t in caso["trocas"]):
            ap.append({"tipo": "ambiguidade_nao_registrada", "campo": chave,
                       "detalhe": f"sem verbo de publicação/criação, gabarito só {presentes}"})

    for campo, valor in caso["esperado"].items():
        if campo in usados or gabarito.eh_opcional(valor):
            continue
        if not any(campo in k.split("|") for k in ex.evidencias):
            ap.append({"tipo": "sem_evidencia", "campo": campo, "detalhe": gabarito.formatar_valor(valor)})

    if "limit" in ex.campos_opcionais:
        lim = caso["esperado"].get("limit")
        if lim is not None and not gabarito.eh_opcional(lim):
            ap.append({"tipo": "limite_singular_obrigatorio", "campo": "limit",
                       "detalhe": "singular sem número: manual pede limit 1 opcional"})
    return ap


def conferir_fonte(caso: dict, linhas_p: list[str]) -> str | None:
    if caso["origem"] != "P":
        return None
    m = re.search(r":(\d+)$", caso["fonte"])
    if not m:
        return "fonte sem número de linha"
    n = int(m.group(1))
    if n > len(linhas_p) or f"'{caso['consulta']}'" not in linhas_p[n - 1]:
        return f"consulta não encontrada na linha {n} de test-cases.ts"
    return None


# ---------------------------------------------------------------------------
# Consistência entre casos
# ---------------------------------------------------------------------------

EXPRESSOES_DE_CONVENCAO = {
    "detalhad": "scale", "pequena escala": "scale", "media escala": "scale", "grande escala": "scale",
    "mais recente": "sortDirection", "mais antig": "sortDirection", "semana passada": "publicationPeriod|creationPeriod",
    "ultimos 3 meses": "publicationPeriod|creationPeriod", "esse ano": "publicationPeriod|creationPeriod",
    "primeiro cgeo": "supplyArea", "topo\\b": "productType", "topografica(?!s? vetoria)": "productType",
    "ortoimg": "productType", "olimpiadas": "project",
}


# Exceções adjudicadas: a anotação difere da convenção por um motivo registrado.
EXCECOES_JUSTIFICADAS = {
    ("detalhad", "scale", "P14"): "as escalas explícitas '(25k ou 50k)' prevalecem sobre o qualificativo 'detalhado'",
}


def consistencia(casos: list[dict]) -> list[dict]:
    grupos: dict[tuple[str, str], set[str]] = defaultdict(set)
    exemplos: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for c in casos:
        if not c["espera_tool_call"]:
            continue
        t = norm(c["consulta"])
        t = re.sub(r"da mais nova para a mais antiga|\(25k ou 50k\)", " ", t)
        for expr, campos in EXPRESSOES_DE_CONVENCAO.items():
            if not re.search(rf"\b{expr}", t):
                continue
            for campo in campos.split("|"):
                if campo in c["esperado"]:
                    rot = json.dumps(c["esperado"][campo], ensure_ascii=False, sort_keys=True)
                    grupos[(expr, campo)].add(rot)
                    exemplos[(expr, campo, rot)].append(c["id"])
    saida = []
    for (expr, campo), rotulos in grupos.items():
        if len(rotulos) <= 1:
            continue
        anotacoes = {r: exemplos[(expr, campo, r)] for r in rotulos}
        justificadas = {i: EXCECOES_JUSTIFICADAS[(expr, campo, i)] for ids in anotacoes.values() for i in ids
                        if (expr, campo, i) in EXCECOES_JUSTIFICADAS}
        restantes = [r for r, ids in anotacoes.items() if not all(i in justificadas for i in ids)]
        saida.append({"expressao": expr, "campo": campo, "anotacoes": anotacoes,
                      "excecoes_justificadas": justificadas, "resolvido": len(restantes) <= 1})
    return saida


# ---------------------------------------------------------------------------
# Comparação com a anotação independente
# ---------------------------------------------------------------------------

def _leituras_do_anotador(a: dict) -> list[dict]:
    base = dict(a.get("parametros") or {})
    for va in a.get("valores_alternativos") or []:
        campo, valores = va.get("campo"), va.get("valores") or []
        if campo in base and valores:
            base[campo] = {gabarito.UM_DE: valores}
    for campo in a.get("campos_opcionais") or []:
        if campo in base:
            base[campo] = {gabarito.OPCIONAL: base[campo]}
    return [base] + list(a.get("leituras_estruturais") or [])


def comparar_anotacao(caso: dict, a: dict) -> list[str]:
    """Divergências entre gabarito e anotação independente (lista vazia = concordam)."""
    div: list[str] = []
    if bool(a.get("chamar_ferramenta")) != bool(caso["espera_tool_call"]):
        div.append(f"chamar_ferramenta: gabarito={caso['espera_tool_call']} anotador={a.get('chamar_ferramenta')}")
        return div
    if not caso["espera_tool_call"]:
        return div
    if bool(a.get("observacional")) != bool(caso["observacional"]):
        div.append(f"observacional: gabarito={caso['observacional']} anotador={a.get('observacional')}")
    leituras_gab = gabarito.resolver_leituras(caso, DATA_REFERENCIA)
    leituras_anot = _leituras_do_anotador(a)
    # 1) a leitura preferencial do anotador é aceita pelo gabarito?
    pref = {k: gabarito.valor_preferencial(v) for k, v in leituras_anot[0].items()}
    aval = metrics.avaliar_caso(leituras_gab[0], pref, True, leituras_gab[1:])
    if not aval.correto:
        div.append(f"leitura do anotador não aceita pelo gabarito: {json.dumps(pref, ensure_ascii=False)} "
                   f"(FP {sorted(aval.fp)}, FN {sorted(aval.fn)})")
    # 2) a leitura preferencial do gabarito é aceita pelo anotador?
    pref_gab = {k: gabarito.valor_preferencial(v) for k, v in leituras_gab[0].items()}
    aval2 = metrics.avaliar_caso(leituras_anot[0], pref_gab, True, leituras_anot[1:])
    if not aval2.correto:
        div.append(f"leitura do gabarito não aceita pelo anotador (FP {sorted(aval2.fp)}, FN {sorted(aval2.fn)}): "
                   f"{a.get('justificativa', '')}")
    return div


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------

def auditar(casos: list[dict], anotacao: dict[str, dict] | None = None) -> dict:
    linhas_p = ARQUIVO_P.read_text(encoding="utf-8").splitlines() if ARQUIVO_P.exists() else []
    por_caso = []
    for c in casos:
        ex = extrair(c["consulta"])
        aps = comparar(c, ex)
        erro_fonte = conferir_fonte(c, linhas_p) if linhas_p else None
        if erro_fonte:
            aps.append({"tipo": "rastreabilidade", "campo": "-", "detalhe": erro_fonte})
        divergencias = comparar_anotacao(c, anotacao[c["id"]]) if anotacao and c["id"] in anotacao else []
        por_caso.append({
            "id": c["id"], "origem": c["origem"], "familia": c["familia"], "fonte": c["fonte"],
            "consulta": c["consulta"], "observacional": c["observacional"],
            "gabarito": " ; ".join(gabarito.formatar_leitura(c["esperado"])) if c["espera_tool_call"] else "não chamar",
            "leituras_alternativas": len(c["alternativas"]),
            "evidencias": " ; ".join(f"{k}={v.valores} ←'{v.trecho}'" for k, v in ex.evidencias.items()),
            "apontamentos": aps,
            "divergencias_anotacao": divergencias,
        })
    return {
        "dataset_sha256": __import__("hashlib").sha256(CAMINHO_SAIDA.read_bytes()).hexdigest(),
        "estrutura": validar(casos),
        "consistencia": consistencia(casos),
        "casos": por_caso,
        "anotacao_independente": anotacao is not None,
    }


def relatorio_markdown(r: dict) -> str:
    casos = r["casos"]
    tipos = Counter(a["tipo"] for c in casos for a in c["apontamentos"])
    com_ap = [c for c in casos if c["apontamentos"]]
    out = ["# Auditoria do dataset de avaliação", "",
           f"Dataset: `data/dataset.json` (sha256 `{r['dataset_sha256'][:16]}…`), {len(casos)} consultas.", "",
           "## 1. Estrutura", "",
           ("Nenhum problema estrutural." if not r["estrutura"] else "\n".join(f"- {p}" for p in r["estrutura"])), "",
           "## 2. Consistência entre casos", "",
           ("Nenhuma expressão com anotações divergentes." if not r["consistencia"] else ""), ""]
    for g in r["consistencia"]:
        estado = "resolvido por exceção justificada" if g["resolvido"] else "PENDENTE"
        out.append(f"- **{g['expressao']}** → `{g['campo']}` ({estado}): " +
                   "; ".join(f"{k} em {', '.join(v)}" for k, v in g["anotacoes"].items()))
        for i, motivo in g["excecoes_justificadas"].items():
            out.append(f"  - {i}: {motivo}")
    out += ["", "## 3. Evidência (anotador por regras × gabarito)", "",
            f"{len(casos) - len(com_ap)} de {len(casos)} consultas sem apontamento. Apontamentos por tipo:", ""]
    out += [f"- `{t}`: {n}" for t, n in tipos.most_common()]
    out += ["", "| ID | Consulta | Gabarito | Apontamentos |", "|---|---|---|---|"]
    for c in com_ap:
        aps = "<br>".join(f"{a['tipo']} [{a['campo']}] {a['detalhe']}" for a in c["apontamentos"])
        out.append(f"| {c['id']} | {c['consulta']} | {c['gabarito']} | {aps} |")
    if r["anotacao_independente"]:
        div = [c for c in casos if c["divergencias_anotacao"]]
        out += ["", "## 4. Anotação independente às cegas", "",
                f"Concordância com o gabarito em {len(casos) - len(div)} de {len(casos)} consultas "
                f"({100 * (len(casos) - len(div)) / len(casos):.1f}%).", "",
                "| ID | Consulta | Gabarito | Divergência |", "|---|---|---|---|"]
        for c in div:
            out.append(f"| {c['id']} | {c['consulta']} | {c['gabarito']} | {'<br>'.join(c['divergencias_anotacao'])} |")
    return "\n".join(out) + "\n"


def escrever_csv(r: dict, destino: Path) -> None:
    with destino.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "origem", "familia", "fonte", "consulta", "observacional", "gabarito",
                    "leituras_alternativas", "evidencias", "apontamentos", "divergencias_anotacao"])
        for c in r["casos"]:
            w.writerow([c["id"], c["origem"], c["familia"], c["fonte"], c["consulta"], c["observacional"],
                        c["gabarito"], c["leituras_alternativas"], c["evidencias"],
                        " | ".join(f"{a['tipo']} [{a['campo']}] {a['detalhe']}" for a in c["apontamentos"]),
                        " | ".join(c["divergencias_anotacao"])])


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Auditoria automática do dataset.")
    p.add_argument("--anotacao-independente", type=Path, help="JSON {id: anotação} da anotação às cegas")
    p.add_argument("--saida", type=Path, default=DIR_AUDITORIA)
    args = p.parse_args(argv)
    anot = None
    if args.anotacao_independente:
        anot = json.loads(args.anotacao_independente.read_text(encoding="utf-8"))
    r = auditar(carregar_dataset(), anot)
    args.saida.mkdir(parents=True, exist_ok=True)
    (args.saida / "auditoria.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    (args.saida / "relatorio_auditoria.md").write_text(relatorio_markdown(r), encoding="utf-8")
    escrever_csv(r, args.saida / "auditoria_casos.csv")
    tipos = Counter(a["tipo"] for c in r["casos"] for a in c["apontamentos"])
    pendentes = sum(1 for g in r["consistencia"] if not g["resolvido"])
    print(f"estrutura: {len(r['estrutura'])} problema(s) · consistência: {pendentes} grupo(s) pendente(s) "
          f"({len(r['consistencia']) - pendentes} justificado(s)) · "
          f"apontamentos: {sum(tipos.values())} em {sum(1 for c in r['casos'] if c['apontamentos'])} casos {dict(tipos)}")
    if anot:
        div = sum(1 for c in r["casos"] if c["divergencias_anotacao"])
        print(f"anotação independente: {len(r['casos']) - div}/{len(r['casos'])} concordam")
    print(f"→ {args.saida / 'relatorio_auditoria.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
