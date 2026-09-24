#!/usr/bin/env python3
"""Gerador programático da camada G do dataset de avaliação do PFC.

Produz 248 consultas sintetizadas a partir de catálogos fechados do domínio
(UFs, municípios de referência, escalas do SCN, tipos de produto das ET-PCDG,
CGEOs, projetos, códigos MI/INOM, expressões de tempo relativo e padrões de
ordenação). O gabarito de cada consulta é conhecido POR CONSTRUÇÃO: a frase é
montada a partir dos parâmetros que ela deve produzir, e as regras de anotação
seguem `docs/manual_de_anotacao.md`.

Determinístico: um único gerador pseudoaleatório com semente 42, consumido em
ordem fixa. Nenhuma consulta se repete (comparação normalizada, sem acentos e
sem pontuação), nem dentro da camada G nem em relação às camadas P e N.

Uso isolado (regera o apêndice do texto):
    python generate_dataset.py            # escreve apendice_dataset_gerado.tex ao lado deste arquivo

Uso pelo pipeline: `pfc_busca.evaluation.dataset_builder` importa `gerar()`.
"""

from __future__ import annotations

import random
import re
import unicodedata
from pathlib import Path

SEMENTE = 42

# ─────────────────────────────────────────────────────────────
# Catálogos do domínio
# ─────────────────────────────────────────────────────────────
# (nome canônico, apelidos, preposição "de", preposição locativa "em")
ESTADOS = [
    ("Acre", ["AC", "acre"], "do", "no"),
    ("Alagoas", ["AL", "alagoas"], "de", "em"),
    ("Amapá", ["AP", "amapá"], "do", "no"),
    ("Amazonas", ["AM", "amazonas"], "do", "no"),
    ("Bahia", ["BA", "bahia"], "da", "na"),
    ("Ceará", ["CE", "ceará"], "do", "no"),
    ("Distrito Federal", ["DF", "distrito federal"], "do", "no"),
    ("Espírito Santo", ["ES", "espírito santo"], "do", "no"),
    ("Goiás", ["GO", "goiás"], "de", "em"),
    ("Maranhão", ["MA", "maranhão"], "do", "no"),
    ("Mato Grosso", ["MT", "mato grosso"], "de", "em"),
    ("Mato Grosso do Sul", ["MS", "mato grosso do sul"], "de", "em"),
    ("Minas Gerais", ["MG", "minas gerais", "minas"], "de", "em"),
    ("Pará", ["PA", "pará"], "do", "no"),
    ("Paraíba", ["PB", "paraíba"], "da", "na"),
    ("Paraná", ["PR", "paraná"], "do", "no"),
    ("Pernambuco", ["PE", "pernambuco"], "de", "em"),
    ("Piauí", ["PI", "piauí"], "do", "no"),
    ("Rio de Janeiro", ["RJ", "rio de janeiro"], "do", "no"),
    ("Rio Grande do Norte", ["RN", "rio grande do norte"], "do", "no"),
    ("Rio Grande do Sul", ["RS", "rio grande do sul"], "do", "no"),
    ("Rondônia", ["RO", "rondônia"], "de", "em"),
    ("Roraima", ["RR", "roraima"], "de", "em"),
    ("Santa Catarina", ["SC", "santa catarina"], "de", "em"),
    ("São Paulo", ["SP", "são paulo"], "de", "em"),
    ("Sergipe", ["sergipe"], "de", "em"),
    ("Tocantins", ["TO", "tocantins"], "do", "no"),
]
# Estados cujo nome coincide com o da capital: sem sigla, a leitura é ambígua (manual, state/city).
ESTADO_OU_CAPITAL = {"Rio de Janeiro", "São Paulo"}

# Municípios de referência sem ambiguidade com o nome de uma UF.
MUNICIPIOS = ["Brasília", "Manaus", "Porto Velho", "Cuiabá", "Fortaleza", "Salvador",
              "Belo Horizonte", "Curitiba", "Porto Alegre", "Recife", "Goiânia", "Belém"]

# (canônica, apelidos) — apenas grafias usuais
ESCALAS = [
    ("1:1.000", ["1:1000", "1:1.000"]),
    ("1:2.000", ["1:2000", "1:2.000"]),
    ("1:5.000", ["1:5000", "1:5.000"]),
    ("1:10.000", ["1:10000", "1:10.000", "10 mil"]),
    ("1:25.000", ["25k", "1:25000", "25 mil", "detalhada"]),
    ("1:50.000", ["50k", "1:50000", "50 mil"]),
    ("1:100.000", ["100k", "1:100000", "100 mil"]),
    ("1:250.000", ["250k", "1:250000", "250 mil", "pequena escala"]),
]

# (canônico, frases nominais no plural, rótulos para "do tipo X")
TIPOS = [
    ("SCN Carta Topográfica Matricial", ["cartas topográficas", "cartas topo"], ["topográfica", "topo"]),
    ("SCN Carta Topográfica Vetorial", ["cartas topográficas vetoriais", "cartas vetoriais"], ["vetorial"]),
    ("SCN Carta Ortoimagem", ["ortoimagens", "cartas ortoimagem", "ortos"], ["ortoimagem", "ortoimg"]),
    ("SCN Carta Ortoimagem Banda P Pol HH", ["ortoimagens banda P HH"], ["banda P HH"]),
    ("SCN Carta Ortoimagem Banda X Pol HH", ["ortoimagens banda X HH"], ["banda X HH"]),
    ("MDT — RAM", ["MDTs", "modelos digitais do terreno"], ["MDT"]),
    ("MDS — RAM", ["MDSs", "modelos digitais de superfície"], ["MDS"]),
    ("CIRC", ["cartas CIRC"], ["CIRC"]),
    ("Cartas Temáticas Não SCN", ["cartas temáticas", "mapas temáticos"], ["temática"]),
]

CGEOS = [
    ("1° Centro de Geoinformação", ["1º CGEO", "1o cgeo", "primeiro cgeo", "1 CGEO"]),
    ("2° Centro de Geoinformação", ["2º CGEO", "2o cgeo", "segundo cgeo", "2 CGEO"]),
    ("3° Centro de Geoinformação", ["3º CGEO", "3o cgeo", "terceiro cgeo", "3 CGEO"]),
    ("4° Centro de Geoinformação", ["4º CGEO", "4o cgeo", "quarto cgeo", "4 CGEO"]),
    ("5° Centro de Geoinformação", ["5º CGEO", "5o cgeo", "quinto cgeo", "5 CGEO"]),
]

PROJETOS = [
    ("Mapeamento Sistemático", ["mapeamento sistemático", "mapeamento sistematico"]),
    ("Olimpíadas Rio 2016", ["olimpíadas", "olimpiadas", "rio 2016"]),
    ("Copa do Mundo 2014", ["copa do mundo", "copa 2014"]),
    ("Copa das Confederações", ["copa das confederações", "copa das confederacoes"]),
    ("Base Cartográfica Digital da Bahia", ["base cartográfica digital da bahia", "BCD da Bahia"]),
    ("Base Cartográfica Digital de Rondônia", ["base cartográfica digital de rondônia", "BCD de Rondônia"]),
    ("Base Cartográfica Digital do Amapá", ["base cartográfica digital do amapá", "BCD do Amapá"]),
    ("NGA-BECA", ["NGA-BECA", "beca"]),
    ("AMAN", ["AMAN"]),
]

MI_CODES = ["2965-2-NE", "2866-3", "2901", "530", "3010", "2965", "2866-2-SO",
            "2901-4-NE", "531-1-NE", "2965-3", "2866-3-NO", "3010-2-SE"]
INOM_CODES = ["SF-22-Y-D", "SF-22-Y-D-II", "SF-22-Y-D-II-4", "SF-22-Y-D-II-4-SE",
              "SG-22-X-A", "SF-23-V-C", "SG-21-Z-B", "SH-22-W-A-III-1-NE",
              "SG-22-Z-D-II-3", "SF-24-Y-A"]

# (expressão, período) — período = {"rel": regra} ou intervalo absoluto
TEMPOS = [
    ("esse ano", {"rel": "ano_corrente"}),
    ("no ano passado", {"rel": "ano_anterior"}),
    ("no mês passado", {"rel": "mes_anterior"}),
    ("na semana passada", {"rel": "semana_passada"}),
    ("nos últimos 3 meses", {"rel": "ultimos_3_meses"}),
    ("nos últimos 6 meses", {"rel": "ultimos_6_meses"}),
    ("nos últimos 5 anos", {"rel": "ultimos_5_anos"}),
    ("desde 2020", {"rel": "desde_2020"}),
    ("depois de 2022", {"rel": "depois_de_2022"}),
    ("antes de 2020", {"rel": "antes_de_2020"}),
    ("entre 2022 e 2023", {"start": "2022-01-01", "end": "2023-12-31"}),
    ("no primeiro trimestre deste ano", {"rel": "primeiro_trimestre_corrente"}),
    ("no segundo semestre do ano passado", {"rel": "segundo_semestre_anterior"}),
    ("nesta semana", {"rel": "semana_corrente"}),
    ("hoje", {"rel": "hoje"}),
]

# Verbos que decidem o campo de período (manual: publicationPeriod × creationPeriod)
VERBOS_PUB = {"f": "publicadas", "m": "publicados"}
VERBOS_CRI = {"f": ["criadas", "produzidas", "elaboradas"], "m": ["criados", "produzidos", "elaborados"]}

UM_DE = "$um_de"
OPCIONAL = "$opcional"
ORDENACAO_SEM_PISTA = {UM_DE: ["publicationDate", "creationDate"]}


# ─────────────────────────────────────────────────────────────
# Utilitários
# ─────────────────────────────────────────────────────────────

def normalizar(texto: str) -> str:
    sem_acento = "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                         if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", sem_acento).split())


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def frase_escala(apelido: str) -> str:
    if apelido.endswith("k"):
        return f"em {apelido}"
    if apelido.endswith(" mil"):
        return f"na escala de {apelido}"
    if apelido == "detalhada":
        return "em escala detalhada"
    if apelido == "pequena escala":
        return "em pequena escala"
    return f"na escala {apelido}"


def caso(consulta: str, cats: list[str], esperado: dict, *, trocas=(), modelo: str,
         notas: str = "", observacional: bool = False, espera_tool_call: bool = True) -> dict:
    return {
        "consulta": consulta,
        "categorias": sorted(set(cats), key="SCMTOAF".index),
        "esperado": esperado,
        "trocas": [list(t) for t in trocas],
        "modelo": modelo,
        "notas": notas,
        "observacional": observacional,
        "espera_tool_call": espera_tool_call,
    }


class Gerador:
    """Sorteia com uma única fonte pseudoaleatória e rejeita consultas repetidas."""

    def __init__(self, semente: int = SEMENTE):
        self.rng = random.Random(semente)
        self.vistas: set[str] = set()

    def registrar(self, c: dict) -> bool:
        chave = normalizar(c["consulta"])
        if chave in self.vistas:
            return False
        self.vistas.add(chave)
        return True

    def tentar(self, construtor, tentativas: int = 50) -> dict:
        for _ in range(tentativas):
            c = construtor()
            if self.registrar(c):
                return c
        raise RuntimeError("não foi possível gerar consulta inédita")

    def estado(self, excluir_ambiguos: bool = False):
        pool = [e for e in ESTADOS if not (excluir_ambiguos and e[0] in ESTADO_OU_CAPITAL)]
        nome, apelidos, prep, loc = self.rng.choice(pool)
        apelido = self.rng.choice(apelidos + [nome])
        informal = apelido != nome
        trocas = [("state", "city")] if (nome in ESTADO_OU_CAPITAL and not apelido.isupper()) else []
        return nome, apelido, prep, loc, informal, trocas


# ─────────────────────────────────────────────────────────────
# Famílias
# ─────────────────────────────────────────────────────────────

def gen_simples(g: Gerador) -> list[dict]:
    """G-S: um único parâmetro."""
    out = []
    for nome, apelidos, prep, _loc in ESTADOS[:15]:
        apelido = g.rng.choice(apelidos + [nome])
        c = caso(f"cartas {prep} {apelido}", ["S"] + (["A"] if apelido != nome else []),
                 {"state": nome}, modelo="cartas {prep} {estado}")
        assert g.registrar(c), c["consulta"]
        out.append(c)
    for escala, apelidos in ESCALAS:
        apelido = g.rng.choice(apelidos)
        c = caso(f"produtos {frase_escala(apelido)}", ["S"] + (["A"] if apelido != escala else []),
                 {"scale": escala}, modelo="produtos {frase de escala}")
        assert g.registrar(c), c["consulta"]
        out.append(c)
    for tipo, frases, _rot in TIPOS:
        frase = g.rng.choice(frases)
        c = caso(f"{frase} disponíveis", ["S", "A"], {"productType": tipo}, modelo="{tipo} disponíveis")
        assert g.registrar(c), c["consulta"]
        out.append(c)
    for cgeo, apelidos in CGEOS:
        c = caso(f"produtos do {g.rng.choice(apelidos)}", ["S", "A"], {"supplyArea": cgeo},
                 modelo="produtos do {cgeo}")
        assert g.registrar(c), c["consulta"]
        out.append(c)
    for cidade in MUNICIPIOS[:10]:
        c = caso(f"cartas de {cidade}", ["S"], {"city": cidade}, modelo="cartas de {município}")
        assert g.registrar(c), c["consulta"]
        out.append(c)
    for mi in MI_CODES[:8]:
        c = caso(f"carta MI {mi}", ["S", "M"], {"keyword": mi}, modelo="carta MI {mi}")
        assert g.registrar(c), c["consulta"]
        out.append(c)
    for inom in INOM_CODES[:6]:
        c = caso(f"folha INOM {inom}", ["S", "M"], {"keyword": inom}, modelo="folha INOM {inom}")
        assert g.registrar(c), c["consulta"]
        out.append(c)
    return out


def gen_compostas(g: Gerador) -> list[dict]:
    """G-C: dois parâmetros independentes."""
    out = []

    def estado_escala():
        nome, apelido, prep, _loc, informal, trocas = g.estado()
        escala, apelidos = g.rng.choice(ESCALAS)
        ap = g.rng.choice(apelidos)
        return caso(f"cartas {prep} {apelido} {frase_escala(ap)}",
                    ["C"] + (["A"] if informal or ap != escala else []),
                    {"state": nome, "scale": escala}, trocas=trocas,
                    modelo="cartas {prep} {estado} {frase de escala}")

    def cidade_escala():
        cidade = g.rng.choice(MUNICIPIOS)
        escala, apelidos = g.rng.choice(ESCALAS)
        ap = g.rng.choice(apelidos)
        return caso(f"mapas de {cidade} {frase_escala(ap)}", ["C"] + (["A"] if ap != escala else []),
                    {"city": cidade, "scale": escala}, modelo="mapas de {município} {frase de escala}")

    def tipo_estado():
        tipo, frases, _rot = g.rng.choice(TIPOS)
        nome, apelido, prep, _loc, informal, trocas = g.estado()
        return caso(f"{g.rng.choice(frases)} {prep} {apelido}", ["C", "A"],
                    {"productType": tipo, "state": nome}, trocas=trocas, modelo="{tipo} {prep} {estado}")

    def projeto_estado():
        projeto, apelidos = g.rng.choice(PROJETOS)
        nome, apelido, _prep, loc, informal, trocas = g.estado()
        ap = g.rng.choice(apelidos)
        return caso(f"produtos do projeto {ap} {loc} {apelido}",
                    ["C"] + (["A"] if informal or ap != projeto else []),
                    {"project": projeto, "state": nome}, trocas=trocas,
                    modelo="produtos do projeto {projeto} {em} {estado}")

    def cgeo_escala():
        cgeo, apelidos = g.rng.choice(CGEOS)
        escala, aps = g.rng.choice(ESCALAS)
        return caso(f"cartas do {g.rng.choice(apelidos)} {frase_escala(g.rng.choice(aps))}", ["C", "A"],
                    {"supplyArea": cgeo, "scale": escala}, modelo="cartas do {cgeo} {frase de escala}")

    for construtor, n in ((estado_escala, 30), (cidade_escala, 8), (tipo_estado, 6),
                          (projeto_estado, 6), (cgeo_escala, 5)):
        out += [g.tentar(construtor) for _ in range(n)]
    return out


def gen_micodes(g: Gerador) -> list[dict]:
    """G-M: código MI/INOM combinado com outro parâmetro."""
    out = []
    for mi in MI_CODES:
        def mi_estado(mi=mi):
            nome, apelido, prep, _loc, informal, trocas = g.estado()
            return caso(f"folha MI {mi} {prep} {apelido}", ["M", "C"] + (["A"] if informal else []),
                        {"keyword": mi, "state": nome}, trocas=trocas, modelo="folha MI {mi} {prep} {estado}")
        out.append(g.tentar(mi_estado))
    for inom in INOM_CODES:
        def inom_tipo(inom=inom):
            tipo, _frases, rotulos = g.rng.choice(TIPOS)
            return caso(f"INOM {inom} do tipo {g.rng.choice(rotulos)}", ["M", "C", "A"],
                        {"keyword": inom, "productType": tipo}, modelo="INOM {inom} do tipo {tipo}")
        out.append(g.tentar(inom_tipo))
    for mi in g.rng.sample(MI_CODES, 6):
        def mi_cgeo(mi=mi):
            cgeo, apelidos = g.rng.choice(CGEOS)
            return caso(f"MI {mi} produzido pelo {g.rng.choice(apelidos)}", ["M", "C", "A"],
                        {"keyword": mi, "supplyArea": cgeo}, modelo="MI {mi} produzido pelo {cgeo}")
        out.append(g.tentar(mi_cgeo))
    return out


def gen_tempo(g: Gerador) -> list[dict]:
    """G-T: tempo relativo. O verbo decide o campo (publicação × criação)."""
    out = []
    for expr, per in TEMPOS:
        c = caso(f"cartas publicadas {expr}", ["T"], {"publicationPeriod": per},
                 modelo="cartas publicadas {tempo}")
        assert g.registrar(c), c["consulta"]
        out.append(c)

    def verbo(indice: int, genero: str) -> tuple[str, str]:
        if indice % 3 == 2:
            return g.rng.choice(VERBOS_CRI[genero]), "creationPeriod"
        return VERBOS_PUB[genero], "publicationPeriod"

    for i, (expr, per) in enumerate(g.rng.sample(TEMPOS, 10)):
        def t_estado(i=i, expr=expr, per=per):
            nome, apelido, prep, _loc, informal, trocas = g.estado()
            v, campo = verbo(i, "f")
            return caso(f"cartas {prep} {apelido} {v} {expr}", ["T", "C"] + (["A"] if informal else []),
                        {"state": nome, campo: per}, trocas=trocas, modelo="cartas {prep} {estado} {verbo} {tempo}")
        out.append(g.tentar(t_estado))
    for i, (expr, per) in enumerate(g.rng.sample(TEMPOS, 8)):
        def t_cgeo(i=i, expr=expr, per=per):
            cgeo, apelidos = g.rng.choice(CGEOS)
            v, campo = verbo(i, "m")
            return caso(f"produtos do {g.rng.choice(apelidos)} {v} {expr}", ["T", "C", "A"],
                        {"supplyArea": cgeo, campo: per}, modelo="produtos do {cgeo} {verbo} {tempo}")
        out.append(g.tentar(t_cgeo))
    for i, (expr, per) in enumerate(g.rng.sample(TEMPOS, 8)):
        def t_escala(i=i, expr=expr, per=per):
            escala, aps = g.rng.choice(ESCALAS)
            ap = g.rng.choice(aps)
            v, campo = verbo(i, "f")
            return caso(f"cartas {frase_escala(ap)} {v} {expr}", ["T", "C"] + (["A"] if ap != escala else []),
                        {"scale": escala, campo: per}, modelo="cartas {frase de escala} {verbo} {tempo}")
        out.append(g.tentar(t_escala))
    return out


def _ordem(campo, direcao, limite=None, limite_opcional=False) -> dict:
    o = {"sortField": campo, "sortDirection": direcao}
    if limite is not None:
        o["limit"] = {OPCIONAL: limite} if limite_opcional else limite
    return o


def gen_ordenacao(g: Gerador) -> list[dict]:
    """G-O: ordenação e limite, com as convenções do manual (pista, número, singular)."""
    out = []
    modelos_estado = [
        ("a carta mais recente {prep} {x}", _ordem(ORDENACAO_SEM_PISTA, "DESC", 1, True)),
        ("a carta mais antiga {prep} {x}", _ordem(ORDENACAO_SEM_PISTA, "ASC", 1, True)),
        ("as cartas mais recentes {prep} {x}", _ordem(ORDENACAO_SEM_PISTA, "DESC")),
        ("as cartas mais antigas {prep} {x}", _ordem(ORDENACAO_SEM_PISTA, "ASC")),
        ("a primeira carta produzida {prep} {x}", _ordem("creationDate", "ASC", 1, True)),
        ("a última carta publicada {prep} {x}", _ordem("publicationDate", "DESC", 1, True)),
        ("as 3 cartas mais antigas {prep} {x}", _ordem(ORDENACAO_SEM_PISTA, "ASC", 3)),
        ("as 5 publicações mais recentes {prep} {x}", _ordem("publicationDate", "DESC", 5)),
        ("as 10 cartas criadas mais recentemente {prep} {x}", _ordem("creationDate", "DESC", 10)),
        ("cartas {prep} {x} em ordem cronológica de publicação", _ordem("publicationDate", "ASC")),
    ]
    for modelo, ordem in modelos_estado:
        def o_estado(modelo=modelo, ordem=ordem):
            nome, apelido, prep, _loc, informal, trocas = g.estado()
            return caso(modelo.format(prep=prep, x=apelido), ["O", "C"] + (["A"] if informal else []),
                        {"state": nome, **ordem}, trocas=trocas, modelo=modelo.replace("{x}", "{estado}"))
        out.append(g.tentar(o_estado))

    tipos_fem = [("SCN Carta Ortoimagem", "ortoimagens", "ortoimagem"),
                 ("SCN Carta Topográfica Matricial", "cartas topográficas", "carta topográfica"),
                 ("Cartas Temáticas Não SCN", "cartas temáticas", "carta temática"),
                 ("SCN Carta Topográfica Vetorial", "cartas topográficas vetoriais", "carta topográfica vetorial"),
                 ("CIRC", "cartas CIRC", "carta CIRC")]
    modelos_tipo = [
        ("as {pl} mais recentes", _ordem(ORDENACAO_SEM_PISTA, "DESC")),
        ("as 3 {pl} mais antigas", _ordem(ORDENACAO_SEM_PISTA, "ASC", 3)),
        ("a última {sg} publicada", _ordem("publicationDate", "DESC", 1, True)),
        ("a primeira {sg} elaborada", _ordem("creationDate", "ASC", 1, True)),
        ("{pl} da mais nova para a mais antiga", _ordem(ORDENACAO_SEM_PISTA, "DESC")),
    ]
    for (modelo, ordem), (tipo, pl, sg) in zip(modelos_tipo, g.rng.sample(tipos_fem, 5), strict=True):
        c = caso(modelo.format(pl=pl, sg=sg), ["O", "C"], {"productType": tipo, **ordem}, modelo=modelo)
        assert g.registrar(c), c["consulta"]
        out.append(c)

    modelos_tempo = [
        ("as cartas mais recentes publicadas {t}", "publicationPeriod", _ordem(ORDENACAO_SEM_PISTA, "DESC")),
        ("a primeira carta criada {t}", "creationPeriod", _ordem("creationDate", "ASC", 1, True)),
        ("as 5 cartas mais antigas publicadas {t}", "publicationPeriod", _ordem(ORDENACAO_SEM_PISTA, "ASC", 5)),
        ("a última carta publicada {t}", "publicationPeriod", _ordem("publicationDate", "DESC", 1, True)),
    ]
    for (modelo, campo, ordem), (expr, per) in zip(modelos_tempo, g.rng.sample(TEMPOS, 4), strict=True):
        c = caso(modelo.format(t=expr), ["O", "T", "C"], {campo: per, **ordem}, modelo=modelo)
        assert g.registrar(c), c["consulta"]
        out.append(c)
    return out


def gen_ambiguas_extras(g: Gerador) -> list[dict]:
    """G-A: grafias informais — siglas minúsculas, ausência de acento, expressões qualitativas."""
    out = []
    for nome, sigla, prep in [("Pernambuco", "pe", "de"), ("Paraná", "pr", "do"), ("Santa Catarina", "sc", "de"),
                              ("Goiás", "go", "de"), ("Ceará", "ce", "do"), ("Pará", "pa", "do")]:
        out.append(caso(f"mapas {prep} {sigla}", ["S", "A"], {"state": nome}, modelo="mapas {prep} {sigla}"))
    for nome, prep in [("Goiás", "de"), ("Rondônia", "de"), ("Piauí", "do"),
                       ("Amapá", "do"), ("Maranhão", "do"), ("Paraíba", "da")]:
        out.append(caso(f"mapas {prep} {sem_acento(nome).lower()}", ["S", "A"], {"state": nome},
                        modelo="mapas {prep} {estado sem acento}"))
    for cidade in ["Cuiabá", "Goiânia", "Belém", "Brasília"]:
        out.append(caso(f"mapas de {sem_acento(cidade).lower()}", ["S", "A"], {"city": cidade},
                        modelo="mapas de {município sem acento}"))
    out.append(caso("cartas do rio em 50k", ["C", "A"], {"state": "Rio de Janeiro", "scale": "1:50.000"},
                    trocas=[("state", "city")], modelo="(fixo)",
                    notas="'rio' é ambíguo entre o estado e a capital"))
    out.append(caso("mapas detalhados do Amazonas", ["C", "A"], {"scale": "1:25.000", "state": "Amazonas"},
                    modelo="(fixo)", notas="'detalhada' → 1:25.000 é informado na descrição da ferramenta"))
    out.append(caso("cartas em pequena escala do sul", ["S", "A"], {"scale": "1:250.000"},
                    modelo="(fixo)", notas="'sul' é região, não estado: nada a anotar"))
    out.append(caso("produtos em média escala", ["S", "A"], {"scale": {UM_DE: ["1:50.000", "1:100.000"]}},
                    modelo="(fixo)", notas="'média escala' aceita as escalas médias do SCN"))
    for c in out:
        assert g.registrar(c), c["consulta"]
    for k, canonica in [("25k", "1:25.000"), ("50k", "1:50.000"), ("100k", "1:100.000"), ("250k", "1:250.000")]:
        def k_estado(k=k, canonica=canonica):
            nome, _apelido, prep, _loc, _inf, _t = g.estado(excluir_ambiguos=True)
            return caso(f"cartas {prep} {nome} em {k}", ["C", "A"], {"state": nome, "scale": canonica},
                        modelo="cartas {prep} {estado} em {k}")
        out.append(g.tentar(k_estado))
    return out


def gen_multi_produto(g: Gerador) -> list[dict]:
    """G-P: consultas amplas que devolvem muitos produtos."""
    out = []
    for nome, _ap, prep, _loc in g.rng.sample(ESTADOS, 5):
        trocas = [("state", "city")] if nome in ESTADO_OU_CAPITAL else []
        c = caso(f"todas as cartas {prep} {nome}", ["S"], {"state": nome}, trocas=trocas,
                 modelo="todas as cartas {prep} {estado}")
        assert g.registrar(c), c["consulta"]
        out.append(c)
    for cgeo, _ap in CGEOS:
        c = caso(f"todos os produtos do {cgeo}", ["S"], {"supplyArea": cgeo}, modelo="todos os produtos do {cgeo}")
        assert g.registrar(c), c["consulta"]
        out.append(c)
    for escala, _ap in g.rng.sample(ESCALAS, 3):
        def escala_estado(escala=escala):
            nome, _a, prep, _loc, _inf, _t = g.estado(excluir_ambiguos=True)
            return caso(f"cartas na escala {escala} {prep} {nome}", ["C"], {"scale": escala, "state": nome},
                        modelo="cartas na escala {escala} {prep} {estado}")
        out.append(g.tentar(escala_estado))
    return out


def gen_fronteira(g: Gerador) -> list[dict]:
    """G-F: fronteira do domínio (manual, P4 e P6).

    As seis primeiras estão fora do domínio e têm gabarito determinado ("não chamar",
    categoria F, métricas principais); a última tem valor impossível e é observacional.
    """
    fixos = [
        ("me ajuda", "sem intenção de busca", False),
        ("cartas de Marte", "fora da Terra", False),
        ("cartas da Argentina", "fora do território brasileiro", False),
        ("qual a previsão do tempo para amanhã em Manaus?", "outro assunto", False),
        ("quanto custa uma carta topográfica?", "pergunta de preço, não de busca", False),
        ("mapa do tesouro pirata", "ficção", False),
        ("cartas do estado 42", "observacional, P6: valor impossível de representar", True),
    ]
    out = []
    for consulta, motivo, obs in fixos:
        c = caso(consulta, ["S"] if obs else ["F"], {}, modelo="(fixo)", notas=motivo,
                 observacional=obs, espera_tool_call=False)
        assert g.registrar(c), c["consulta"]
        out.append(c)
    return out


# Ordem fixa — NÃO reordenar (a sequência de sorteios define o dataset).
FAMILIAS = [
    ("GS", "gen_simples", "Consultas simples geradas por \\textit{templates} (G-S)"),
    ("GC", "gen_compostas", "Consultas compostas geradas por \\textit{templates} (G-C)"),
    ("GM", "gen_micodes", "Consultas com c\\'odigo MI/INOM geradas por \\textit{templates} (G-M)"),
    ("GT", "gen_tempo", "Consultas com tempo relativo geradas por \\textit{templates} (G-T)"),
    ("GO", "gen_ordenacao", "Consultas com ordena\\c{c}\\~ao geradas por \\textit{templates} (G-O)"),
    ("GA", "gen_ambiguas_extras", "Consultas amb\\'iguas/informais adicionais (G-A)"),
    ("GP", "gen_multi_produto", "Consultas amplas, com muitos produtos (G-P)"),
    ("GF", "gen_fronteira", "Consultas de fronteira do dom\\'inio (G-F)"),
]


def gerar(semente: int = SEMENTE) -> dict[str, list[dict]]:
    """Casos da camada G por família, com IDs atribuídos (GS001, GC001, ...)."""
    g = Gerador(semente)
    saida: dict[str, list[dict]] = {}
    funcoes = globals()
    for prefixo, nome_funcao, _titulo in FAMILIAS:
        casos = funcoes[nome_funcao](g)
        for indice, c in enumerate(casos, start=1):
            c["id"] = f"{prefixo}{indice:03d}"
            c["familia"] = prefixo
            c["funcao"] = nome_funcao
        saida[prefixo] = casos
    return saida


# ─────────────────────────────────────────────────────────────
# Emissão LaTeX (Apêndice A)
# ─────────────────────────────────────────────────────────────
TEXTO_REGRA = {
    "ano_corrente": "ano corrente", "ano_anterior": "ano anterior, inteiro",
    "dois_anos_atras": "ano de dois anos antes", "mes_anterior": "mês anterior, inteiro",
    "mes_corrente": "mês corrente", "semana_passada": "semana passada", "semana_corrente": "semana corrente",
    "hoje": "dia da execução", "ultimos_3_meses": "últimos 3 meses", "ultimos_6_meses": "últimos 6 meses",
    "ultimos_5_anos": "últimos 5 anos", "desde_2020": "desde 2020", "depois_de_2020": "depois de 2020",
    "depois_de_2022": "depois de 2022", "antes_de_2020": "antes de 2020",
    "primeiro_trimestre_corrente": "1º trimestre do ano corrente",
    "segundo_semestre_anterior": "2º semestre do ano anterior",
    "ultimo_trimestre_ano_anterior": "4º trimestre do ano anterior", "trimestre_anterior": "trimestre anterior",
}


def esc(texto: str) -> str:
    return (texto.replace("\\", "\\textbackslash{}").replace("&", r"\&").replace("_", r"\_")
            .replace("%", r"\%").replace("#", r"\#").replace("$", r"\$").replace("°", r"$^\circ$"))


def fmt_valor(v) -> str:
    if isinstance(v, dict) and OPCIONAL in v:
        return f"{fmt_valor(v[OPCIONAL])} (opcional)"
    if isinstance(v, dict) and UM_DE in v:
        return " ou ".join(fmt_valor(x) for x in v[UM_DE])
    if isinstance(v, dict) and "rel" in v:
        return TEXTO_REGRA.get(v["rel"], v["rel"])
    if isinstance(v, dict):
        if "start" in v and "end" in v:
            return f"{v['start']} a {v['end']}"
        return f"a partir de {v['start']}" if "start" in v else f"até {v.get('end', '')}"
    return f'"{v}"' if isinstance(v, str) else str(v)


def linhas_gabarito(c: dict) -> list[str]:
    if not c.get("espera_tool_call", True):
        return [esc("não chamar a ferramenta") + (f" ({esc(c['notas'])})" if c.get("notas") else "")]
    linhas = [esc(f"{campo}: {fmt_valor(v)}") for campo, v in c["esperado"].items()]
    for origem, destino in c.get("trocas", []):
        linhas.append(esc(f"aceita-se também {destino} no lugar de {origem}"))
    if c.get("observacional"):
        linhas.append(esc("caso observacional (P6): executado e reportado, fora das métricas principais"))
    return linhas


SEPARADOR_LINHAS = r"\newline "


def nota_do_caso(c: dict) -> str:
    """Origem (camada P) e justificativa das leituras alternativas, quando houver."""
    partes = []
    m = re.search(r"test-cases\.ts:(\d+)$", c.get("fonte", ""))
    if m:
        partes.append(f"origem: test-cases.ts do protótipo, linha {m.group(1)}")
    if c.get("notas") and c.get("espera_tool_call", True):
        partes.append(c["notas"])
    return "; ".join(partes)


def dtcase(c: dict) -> str:
    cats = " · ".join(c["categorias"])
    corpo = SEPARADOR_LINHAS.join(linhas_gabarito(c))
    nota = nota_do_caso(c)
    if nota:
        return f"\\dtcasenota{{{c['id']}}}{{{cats}}}{{{esc(c['consulta'])}}}{{{corpo}}}{{{esc(nota)}}}"
    return f"\\dtcase{{{c['id']}}}{{{cats}}}{{{esc(c['consulta'])}}}{{{corpo}}}"


def tabela_familia(casos: list[dict]) -> list[str]:
    """Todas as consultas da família, uma por linha (longtable)."""
    out = [r"{\footnotesize", r"\begin{longtable}{|p{1.1cm}|p{1.3cm}|p{5.4cm}|p{6.3cm}|}", r"\hline",
           r"\textbf{ID} & \textbf{Cat.} & \textbf{Consulta} & \textbf{Leituras aceitas} \\ \hline",
           r"\endhead"]
    for c in casos:
        out.append(f"{c['id']} & {' · '.join(c['categorias'])} & {esc(c['consulta'])} & "
                   f"{'; '.join(linhas_gabarito(c))} " + r"\\ \hline")
    out += [r"\end{longtable}", "}"]
    return out


def emit_section(titulo: str, casos: list[dict]) -> str:
    out = [f"\\section{{{titulo}}}", "",
           f"Total desta fam\\'ilia: \\textbf{{{len(casos)} consultas}}, listadas integralmente abaixo "
           "(a fun\\c{c}\\~ao geradora e o modelo de frase de cada consulta constam de \\texttt{dataset.json}).", ""]
    out += tabela_familia(casos)
    return "\n".join(out) + "\n"


def emitir_apendice(familias: dict[str, list[dict]], destino: Path) -> None:
    total = sum(len(v) for v in familias.values())
    partes = [f"% ─── AUTO-GERADO por generate_dataset.py (semente {SEMENTE}): {total} consultas ───", ""]
    for prefixo, _f, titulo in FAMILIAS:
        partes.append(emit_section(titulo, familias[prefixo]))
    destino.write_text("\n".join(partes) + "\n", encoding="utf-8")


def main() -> None:
    familias = gerar()
    destino = Path(__file__).with_name("apendice_dataset_gerado.tex")
    emitir_apendice(familias, destino)
    total = sum(len(v) for v in familias.values())
    print(f"{destino.name}: {total} consultas — " + ", ".join(f"{k}={len(v)}" for k, v in familias.items()))


if __name__ == "__main__":
    main()
