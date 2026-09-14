#!/usr/bin/env python3
# Gerador programático do dataset de avaliação — PFC
# Produz entradas \dtcase{} para LaTeX.

import itertools, random, textwrap

random.seed(42)  # reprodutibilidade

# ─────────────────────────────────────────────────────────────
# CATÁLOGOS (extraídos de constants.ts do protótipo do 1º CGEO)
# ─────────────────────────────────────────────────────────────
STATES = [
    ("Acre", ["AC", "acre"]),
    ("Alagoas", ["AL", "alagoas"]),
    ("Amapá", ["AP", "amapa", "Amapa"]),
    ("Amazonas", ["AM", "amazonas"]),
    ("Bahia", ["BA", "bahia"]),
    ("Ceará", ["CE", "ceara", "Ceara"]),
    ("Distrito Federal", ["DF", "df", "distrito federal"]),
    ("Espírito Santo", ["ES", "espirito santo"]),
    ("Goiás", ["GO", "goias", "Goias"]),
    ("Maranhão", ["MA", "maranhao", "Maranhao"]),
    ("Mato Grosso", ["MT", "mato grosso"]),
    ("Mato Grosso do Sul", ["MS", "mato grosso do sul", "MTdoSul"]),
    ("Minas Gerais", ["MG", "minas gerais", "minas"]),
    ("Pará", ["PA", "para", "Para"]),
    ("Paraíba", ["PB", "paraiba"]),
    ("Paraná", ["PR", "parana"]),
    ("Pernambuco", ["PE", "pernambuco"]),
    ("Piauí", ["PI", "piaui"]),
    ("Rio de Janeiro", ["RJ", "rio de janeiro", "rio"]),
    ("Rio Grande do Norte", ["RN", "rio grande do norte"]),
    ("Rio Grande do Sul", ["RS", "rio grande do sul", "gauchos"]),
    ("Rondônia", ["RO", "rondonia"]),
    ("Roraima", ["RR", "roraima"]),
    ("Santa Catarina", ["SC", "santa catarina"]),
    ("São Paulo", ["SP", "sao paulo", "sampa"]),
    ("Sergipe", ["SE", "sergipe"]),
    ("Tocantins", ["TO", "tocantins"]),
]

CITIES = [
    ("Rio de Janeiro", "Rio de Janeiro"),
    ("São Paulo", "São Paulo"),
    ("Brasília", "Distrito Federal"),
    ("Manaus", "Amazonas"),
    ("Porto Velho", "Rondônia"),
    ("Cuiabá", "Mato Grosso"),
    ("Fortaleza", "Ceará"),
    ("Salvador", "Bahia"),
    ("Belo Horizonte", "Minas Gerais"),
    ("Curitiba", "Paraná"),
    ("Porto Alegre", "Rio Grande do Sul"),
    ("Recife", "Pernambuco"),
    ("Goiânia", "Goiás"),
    ("Belém", "Pará"),
]

SCALES = [
    ("1:1.000",     ["1k", "1:1000", "1 mil"]),
    ("1:2.000",     ["2k", "1:2000"]),
    ("1:5.000",     ["5k", "1:5000"]),
    ("1:10.000",    ["10k", "1:10000"]),
    ("1:25.000",    ["25k", "1:25000", "detalhada"]),
    ("1:50.000",    ["50k", "1:50000"]),
    ("1:100.000",   ["100k", "1:100000", "cem k"]),
    ("1:250.000",   ["250k", "1:250000", "pequena escala"]),
]

PRODUCT_TYPES = [
    ("SCN Carta Topográfica Matricial",           ["topo", "topográfica", "topografica"]),
    ("SCN Carta Topográfica Vetorial",            ["vetorial", "topográfica vetorial"]),
    ("SCN Carta Ortoimagem",                      ["ortoimagem", "ortoimg", "orto"]),
    ("SCN Carta Ortoimagem Banda P Pol HH",       ["banda P HH", "orto banda P"]),
    ("SCN Carta Ortoimagem Banda X Pol HH",       ["banda X HH", "orto banda X"]),
    ("MDT — RAM",                                 ["MDT", "mdt", "modelo digital de terreno"]),
    ("MDS — RAM",                                 ["MDS", "mds", "modelo digital de superficie"]),
    ("CIRC",                                      ["CIRC", "circ"]),
    ("Cartas Temáticas Não SCN",                  ["carta temática", "temática", "tematica"]),
]

SUPPLY_AREAS = [
    ("1° Centro de Geoinformação", ["1o CGEO", "primeiro cgeo", "1 CGEO", "1º cgeo"]),
    ("2° Centro de Geoinformação", ["2o CGEO", "segundo cgeo", "2 CGEO"]),
    ("3° Centro de Geoinformação", ["3o CGEO", "terceiro cgeo", "3 CGEO"]),
    ("4° Centro de Geoinformação", ["4o CGEO", "quarto cgeo", "4 CGEO"]),
    ("5° Centro de Geoinformação", ["5o CGEO", "quinto cgeo", "5 CGEO"]),
]

PROJECTS = [
    ("Mapeamento Sistemático",            ["mapeamento sistematico", "sistemático"]),
    ("Olimpíadas Rio 2016",               ["olimpiadas", "rio 2016", "jogos olimpicos"]),
    ("Copa do Mundo 2014",                ["copa 2014", "copa do mundo"]),
    ("Copa das Confederações",            ["copa das confederacoes", "confederações"]),
    ("Base Cartográfica Digital da Bahia",["BCD da Bahia", "bcd bahia"]),
    ("Base Cartográfica Digital de Rondônia", ["BCD Rondônia", "bcd rondonia"]),
    ("Base Cartográfica Digital do Amapá",["BCD Amapá", "bcd amapa"]),
    ("NGA-BECA",                          ["NGA-BECA", "BECA", "beca"]),
    ("AMAN",                              ["AMAN", "aman"]),
]

# Códigos MI e INOM plausíveis
MI_CODES = ["2965-2-NE", "2866-3", "2901", "530", "3010", "2965", "2866-2-SO",
            "2901-4-NE", "531-1-NE", "2965-3", "2866-3-NO", "3010-2-SE"]
INOM_CODES = ["SF-22-Y-D", "SF-22-Y-D-II", "SF-22-Y-D-II-4", "SF-22-Y-D-II-4-SE",
              "SG-22-X-A", "SF-23-V-C", "SG-21-Z-B", "SH-22-W-A-III-1-NE",
              "SG-22-Z-D-II-3", "SF-24-Y-A"]

TIME_RELATIVE_TEMPLATES = [
    ("esse ano",                 "ano corrente da execução, integral"),
    ("ano passado",              "ano anterior à execução, integral"),
    ("mês passado",              "mês anterior à execução, integral"),
    ("semana passada",           "7 dias corridos anteriores à execução"),
    ("últimos 3 meses",          "90 dias corridos anteriores à execução"),
    ("últimos 6 meses",          "180 dias corridos anteriores à execução"),
    ("últimos 5 anos",           "5 anos anteriores à execução"),
    ("desde 2020",               "2020-01-01 a data da execução"),
    ("depois de 2022",           "2022-01-01 a data da execução"),
    ("antes de 2020",            "sem limite inferior a 2019-12-31"),
    ("entre 2022 e 2023",        "2022-01-01 a 2023-12-31"),
    ("no primeiro trimestre",    "1º trimestre do ano da execução"),
    ("segundo semestre passado", "jul--dez do ano anterior"),
    ("desta semana",             "semana corrente"),
    ("de hoje",                  "dia da execução"),
]

ORDERINGS = [
    ("mais recente",   ("publicationDate", "DESC", None)),
    ("mais antiga",    ("publicationDate", "ASC",  None)),
    ("mais recentes",  ("publicationDate", "DESC", None)),
    ("mais antigas",   ("publicationDate", "ASC",  None)),
    ("primeira",       ("creationDate",    "ASC",  1)),
    ("última",         ("creationDate",    "DESC", 1)),
    ("3 mais antigas", ("creationDate",    "ASC",  3)),
    ("5 mais antigas", ("creationDate",    "ASC",  5)),
    ("10 mais recentes",("creationDate",   "DESC", 10)),
]

# ─────────────────────────────────────────────────────────────
# GERADORES POR CATEGORIA
# ─────────────────────────────────────────────────────────────
def esc(text):
    """Escape LaTeX special characters minimally."""
    return (text.replace("&", r"\&")
                .replace("_", r"\_")
                .replace("%", r"\%")
                .replace("#", r"\#"))

def dtcase(id_, cats, query, params):
    r"""Emit a \dtcase{...}{...}{...}{...} line."""
    params_str = r"\newline ".join(params) if isinstance(params, list) else params
    return f"\\dtcase{{{id_}}}{{{cats}}}{{{esc(query)}}}{{{params_str}}}"

def gen_simples():
    """S: consultas de UM parâmetro só."""
    out = []
    # UFs — samples
    for state, aliases in STATES[:15]:  # 15 UFs
        alias = random.choice(aliases + [state.lower(), state])
        cats = "S" + (" · A" if alias != state and alias.lower() != state.lower() else "")
        out.append((f"cartas de {alias}", cats, [f'state: "{state}"']))
    # Escalas
    for scale, aliases in SCALES:
        alias = random.choice(aliases + [scale])
        cats = "S" + (" · A" if alias != scale else "")
        out.append((f"produtos em escala {alias}", cats, [f'scale: "{scale}"']))
    # Tipos de produto
    for pt, aliases in PRODUCT_TYPES:
        alias = random.choice(aliases + [pt])
        cats = "S" + (" · A" if alias.lower() != pt.lower() else "")
        out.append((f"{alias}", cats, [f'productType: "{pt}"']))
    # CGEOs
    for sa, aliases in SUPPLY_AREAS:
        alias = random.choice(aliases)
        out.append((f"produtos do {alias}", "S · A", [f'supplyArea: "{sa}"']))
    # Cidades
    for city, uf in CITIES[:10]:
        out.append((f"cartas de {city}", "S", [f'city: "{city}"']))
    # MIs/INOMs isolados
    for mi in MI_CODES[:8]:
        out.append((f"MI {mi}", "S · M", [f'keyword: "{mi}"']))
    for inom in INOM_CODES[:6]:
        out.append((f"INOM {inom}", "S · M", [f'keyword: "{inom}"']))
    return out

def gen_compostas():
    """C: dois ou mais parâmetros."""
    out = []
    # UF + Escala (sample 30 combinações)
    pairs = [(random.choice(STATES), random.choice(SCALES)) for _ in range(30)]
    for (state, salias), (scale, kalias) in pairs:
        sa = random.choice(salias + [state])
        sk = random.choice(kalias + [scale])
        cats = "C" + (" · A" if (sa != state or sk != scale) else "")
        out.append((f"cartas de {sa} em {sk}", cats, [f'state: "{state}"', f'scale: "{scale}"']))
    # Cidade + Escala
    for city, uf in random.sample(CITIES, 8):
        scale, kalias = random.choice(SCALES)
        sk = random.choice(kalias + [scale])
        cats = "C" + (" · A" if sk != scale else "")
        out.append((f"mapas de {city} em {sk}", cats, [f'city: "{city}"', f'scale: "{scale}"']))
    # Tipo + UF
    for pt, palias in random.sample(PRODUCT_TYPES, 6):
        state, salias = random.choice(STATES)
        sp = random.choice(palias + [pt])
        sa = random.choice(salias + [state])
        cats = "C" + (" · A" if (sa != state or sp.lower() != pt.lower()) else "")
        out.append((f"{sp} de {sa}", cats, [f'productType: "{pt}"', f'state: "{state}"']))
    # Projeto + UF
    for proj, palias in random.sample(PROJECTS, 6):
        state, salias = random.choice(STATES)
        sp = random.choice(palias + [proj])
        sa = random.choice(salias + [state])
        cats = "C" + (" · A" if (sp != proj or sa != state) else "")
        out.append((f"produtos do projeto {sp} em {sa}", cats, [f'project: "{proj}"', f'state: "{state}"']))
    # CGEO + Escala
    for sa_, sa_al in SUPPLY_AREAS:
        scale, kalias = random.choice(SCALES)
        salias_ = random.choice(sa_al)
        sk = random.choice(kalias + [scale])
        out.append((f"cartas do {salias_} em {sk}", "C · A", [f'supplyArea: "{sa_}"', f'scale: "{scale}"']))
    return out

def gen_micodes():
    """M: com MI/INOM."""
    out = []
    for mi in MI_CODES:
        state, salias = random.choice(STATES)
        sa = random.choice(salias + [state])
        cats = "M · C" + (" · A" if sa != state else "")
        out.append((f"folha MI {mi} de {sa}", cats, [f'keyword: "{mi}"', f'state: "{state}"']))
    for inom in INOM_CODES:
        pt, palias = random.choice(PRODUCT_TYPES)
        sp = random.choice(palias + [pt])
        cats = "M · C" + (" · A" if sp.lower() != pt.lower() else "")
        out.append((f"INOM {inom} do tipo {sp}", cats, [f'keyword: "{inom}"', f'productType: "{pt}"']))
    # Combinados com CGEO
    for mi in random.sample(MI_CODES, 6):
        sa, sa_al = random.choice(SUPPLY_AREAS)
        salias_ = random.choice(sa_al)
        out.append((f"MI {mi} produzido pelo {salias_}", "M · C · A", [f'keyword: "{mi}"', f'supplyArea: "{sa}"']))
    return out

def gen_tempo():
    """T: tempo relativo."""
    out = []
    for expr, semantica in TIME_RELATIVE_TEMPLATES:
        # simples: só tempo
        out.append((f"produtos publicados {expr}", "T", [f"publicationPeriod: {semantica}"]))
    # tempo + UF
    for expr, semantica in random.sample(TIME_RELATIVE_TEMPLATES, 10):
        state, salias = random.choice(STATES)
        sa = random.choice(salias + [state])
        cats = "T · C" + (" · A" if sa != state else "")
        out.append((f"cartas de {sa} {expr}", cats, [f'state: "{state}"', f"publicationPeriod: {semantica}"]))
    # tempo + CGEO
    for expr, semantica in random.sample(TIME_RELATIVE_TEMPLATES, 8):
        sa_, sa_al = random.choice(SUPPLY_AREAS)
        salias_ = random.choice(sa_al)
        out.append((f"produtos do {salias_} {expr}", "T · C · A", [f'supplyArea: "{sa_}"', f"publicationPeriod: {semantica}"]))
    # tempo + escala
    for expr, semantica in random.sample(TIME_RELATIVE_TEMPLATES, 8):
        scale, kalias = random.choice(SCALES)
        sk = random.choice(kalias + [scale])
        cats = "T · C" + (" · A" if sk != scale else "")
        out.append((f"cartas em {sk} {expr}", cats, [f'scale: "{scale}"', f"publicationPeriod: {semantica}"]))
    return out

def gen_ordenacao():
    """O: ordenação e limite."""
    out = []
    for expr, (field, direction, limit) in ORDERINGS:
        # simples: só ordenação (raro puro; combino com UF/tipo)
        state, salias = random.choice(STATES)
        sa = random.choice(salias + [state])
        params = [f'state: "{state}"',
                  f'sortField: "{field}"',
                  f'sortDirection: "{direction}"']
        if limit: params.append(f"limit: {limit}")
        cats = "O · C" + (" · A" if sa != state else "")
        out.append((f"{expr.capitalize()} carta de {sa}", cats, params))
    # ordenação + tipo
    for expr, (field, direction, limit) in random.sample(ORDERINGS, 5):
        pt, palias = random.choice(PRODUCT_TYPES)
        sp = random.choice(palias + [pt])
        params = [f'productType: "{pt}"',
                  f'sortField: "{field}"',
                  f'sortDirection: "{direction}"']
        if limit: params.append(f"limit: {limit}")
        cats = "O · C" + (" · A" if sp.lower() != pt.lower() else "")
        out.append((f"{sp} {expr}", cats, params))
    # ordenação + tempo
    for expr, (field, direction, limit) in random.sample(ORDERINGS, 5):
        tempo_expr, semantica = random.choice(TIME_RELATIVE_TEMPLATES)
        params = [f"publicationPeriod: {semantica}",
                  f'sortField: "{field}"',
                  f'sortDirection: "{direction}"']
        if limit: params.append(f"limit: {limit}")
        out.append((f"{expr.capitalize()} carta publicada {tempo_expr}", "O · T · A", params))
    return out

def gen_ambiguas_extras():
    """A: variações informais adicionais (abreviações, sem acento, misturas)."""
    out = []
    # Abreviações estados
    templates = [
        ("mapas do {alias}",               [("Rio de Janeiro", "rj"), ("São Paulo", "sp"),
                                             ("Minas Gerais", "mg"), ("Bahia", "ba"),
                                             ("Rio Grande do Sul", "rs"), ("Distrito Federal", "df")],
                                            lambda st: [f'state: "{st}"']),
    ]
    for tmpl, pairs, params_fn in templates:
        for canon, alias in pairs:
            out.append((tmpl.format(alias=alias), "A · S", params_fn(canon)))
    # Sem acento
    unacc = [("Sao Paulo", "São Paulo", "state"), ("Goias", "Goiás", "state"),
             ("Para", "Pará", "state"), ("Rondonia", "Rondônia", "state"),
             ("Piaui", "Piauí", "state"), ("Ceara", "Ceará", "state"),
             ("Amapa", "Amapá", "state"), ("Maranhao", "Maranhão", "state"),
             ("Cuiaba", "Cuiabá", "city"), ("Goiania", "Goiânia", "city"),
             ("Belem", "Belém", "city")]
    for informal, canonical, field in unacc:
        out.append((f"cartas de {informal}", "A · S",
                    [f'{field}: "{canonical}"']))
    # "Detalhada" / "pequena escala" / "média"
    out.append(("mapas detalhados do Amazonas", "A · C",
                ['scale: "1:25.000"', 'state: "Amazonas"']))
    out.append(("cartas em pequena escala do sul", "A · C",
                ['scale: "1:250.000"']))
    out.append(("produtos em média escala", "A · S",
                ['scale: "1:50.000"']))
    # 25k, 50k, 100k
    for k, canonical in [("25k", "1:25.000"), ("50k", "1:50.000"),
                          ("100k", "1:100.000"), ("250k", "1:250.000")]:
        state, _ = random.choice(STATES)
        out.append((f"cartas do {state} em {k}", "A · C",
                    [f'state: "{state}"', f'scale: "{canonical}"']))
    return out

def gen_multi_produto():
    """Consultas que retornam vários produtos (relevantes para expected_mi_ids)."""
    out = []
    templates = [
        ("todas as cartas de {state}", "C",
         lambda st: [f'state: "{st}"',
                     "expected: retorna todas as cartas cuja bbox intersecta a UF"]),
        ("todos os produtos do {sa}", "C · A",
         lambda sa: [f'supplyArea: "{sa}"',
                     "expected: retorna todos os produtos cadastrados sob esse CGEO"]),
        ("cartas em {scale} do {state}", "C",
         lambda scale, st: [f'scale: "{scale}"', f'state: "{st}"',
                             "expected: retorna todas as folhas naquela escala e UF"]),
    ]
    # Todas de X UF
    for state, _ in random.sample(STATES, 5):
        out.append((f"todas as cartas de {state}", "C",
                    [f'state: "{state}"',
                     "expected: retorna todas as cartas cuja bbox intersecta a UF (contagem esperada varia com o dump)"]))
    for sa, _ in SUPPLY_AREAS:
        out.append((f"todos os produtos do {sa}", "C",
                    [f'supplyArea: "{sa}"',
                     "expected: retorna todos os produtos daquele CGEO"]))
    for scale, _ in random.sample(SCALES, 3):
        state, _ = random.choice(STATES)
        out.append((f"cartas em {scale} do {state}", "C",
                    [f'scale: "{scale}"', f'state: "{state}"',
                     "expected: retorna todas as folhas naquela escala e UF"]))
    return out

def gen_fronteira():
    """Casos de fronteira/erro esperado."""
    return [
        ("cartas fora do brasil", "S",
         ['expected: nenhum parâmetro extraível (fora do domínio)']),
        ("me ajuda", "S",
         ['expected: nenhum parâmetro extraível (sem intenção clara)']),
        ("quero um mapa bonito", "A",
         ['expected: nenhum parâmetro extraível (subespecífico)']),
        ("escala 1:10.000.000", "S · A",
         ['expected: escala fora do enum (erro esperado)']),
        ("cartas do futuro (ano 2050)", "C · T",
         ['publicationPeriod: 2050-01-01 a 2050-12-31',
          'expected: SQL válida com resultado esperado zero registros']),
        ("cartas de Marte", "S",
         ['expected: nenhum estado brasileiro; deve devolver zero ou pedir esclarecimento']),
        ("cartas do estado 42", "S",
         ['expected: state inválido; erro de normalização detectável']),
    ]

# ─────────────────────────────────────────────────────────────
# EMISSÃO LaTeX
# ─────────────────────────────────────────────────────────────
SAMPLE_PER_FAMILY = 6  # exibe apenas as N primeiras de cada família no PDF

def emit_section(name, cases, prefix, start_idx=1):
    out = [f"\\section{{{name}}}", ""]
    total = len(cases)
    sample = cases[:SAMPLE_PER_FAMILY]
    remaining = total - len(sample)
    if remaining > 0:
        restantes = ("a demais 1 \\'e gerada" if remaining == 1
                     else f"as demais {remaining} s\\~ao geradas")
        out.append(f"Total desta fam\\'ilia: \\textbf{{{total} consultas}}. "
                   f"Reproduzem-se abaixo as {len(sample)} primeiras como amostra representativa; "
                   f"{restantes} pelo \\textit{{script}} "
                   f"\\texttt{{generate\\_dataset.py}}, dispon\\'ivel no reposit\\'orio do projeto.")
    else:
        out.append(f"Total desta fam\\'ilia: \\textbf{{{total} consultas}}.")
    out.append("")
    for i, (q, cats, params) in enumerate(sample, start=start_idx):
        out.append(dtcase(f"{prefix}{i:03d}", cats, q, params))
    return "\n".join(out) + "\n"

def main():
    parts = []
    families = [
        ("Consultas simples geradas por \\textit{templates} (G-S)",       gen_simples(),      "GS"),
        ("Consultas compostas geradas por \\textit{templates} (G-C)",     gen_compostas(),    "GC"),
        ("Consultas com c\\'odigo MI/INOM geradas por \\textit{templates} (G-M)", gen_micodes(), "GM"),
        ("Consultas com tempo relativo geradas por \\textit{templates} (G-T)", gen_tempo(),  "GT"),
        ("Consultas com ordena\\c{c}\\~ao geradas por \\textit{templates} (G-O)", gen_ordenacao(), "GO"),
        ("Consultas amb\\'iguas/informais adicionais (G-A)",              gen_ambiguas_extras(), "GA"),
        ("Consultas multi-produto (G-P)",                                 gen_multi_produto(), "GP"),
        ("Consultas de fronteira / erro esperado (G-F)",                  gen_fronteira(),    "GF"),
    ]

    # Contagem total
    total = sum(len(cases) for _, cases, _ in families)
    parts.append(f"% ─── AUTO-GERADO: {total} consultas por templates ───")
    parts.append("")

    for section_name, cases, prefix in families:
        parts.append(emit_section(section_name, cases, prefix))

    # Sumário
    parts.append(f"% Total gerado: {total}")
    parts.append(f"% Detalhamento:")
    for section_name, cases, prefix in families:
        parts.append(f"%   {prefix}: {len(cases)} consultas")

    with open("/tmp/apendice_gerado.tex", "w") as f:
        f.write("\n".join(parts))

    print(f"WROTE /tmp/apendice_gerado.tex")
    print(f"Total generated: {total}")
    print("Detalhamento:")
    for section_name, cases, prefix in families:
        print(f"  {prefix}: {len(cases)} consultas")

if __name__ == "__main__":
    main()
