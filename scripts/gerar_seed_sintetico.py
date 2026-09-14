"""Gera `db/seed_sintetico.sql` — dados SINTÉTICOS e rotulados para o PostGIS.

Servem a um único propósito: provar que a arquitetura fecha ponta a ponta
(consulta → tool call → SQL → GeoJSON). NÃO representam o acervo da DSG, as
geometrias NÃO são as reais (cada UF é um retângulo numa grade) e NENHUMA
métrica do PFC depende deles (Cap. 3, §Exclusões).

Determinístico (seed 7). Reexecute e faça o commit do .sql junto.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "db" / "seed_sintetico.sql"
random.seed(7)

ESTADOS = [  # (nome, sigla) — grade 6 colunas × 5 linhas, oeste→leste, norte→sul
    ("Roraima", "RR"), ("Amapá", "AP"), ("Amazonas", "AM"), ("Pará", "PA"), ("Maranhão", "MA"), ("Ceará", "CE"),
    ("Acre", "AC"), ("Rondônia", "RO"), ("Tocantins", "TO"), ("Piauí", "PI"), ("Rio Grande do Norte", "RN"), ("Paraíba", "PB"),
    ("Mato Grosso", "MT"), ("Goiás", "GO"), ("Distrito Federal", "DF"), ("Bahia", "BA"), ("Pernambuco", "PE"), ("Alagoas", "AL"),
    ("Mato Grosso do Sul", "MS"), ("Minas Gerais", "MG"), ("Espírito Santo", "ES"), ("Sergipe", "SE"), ("São Paulo", "SP"), ("Rio de Janeiro", "RJ"),
    ("Paraná", "PR"), ("Santa Catarina", "SC"), ("Rio Grande do Sul", "RS"),
]
CIDADES = [("Rio de Janeiro", "RJ"), ("São Paulo", "SP"), ("Brasília", "DF"), ("Manaus", "AM"),
           ("Porto Velho", "RO"), ("Cuiabá", "MT"), ("Fortaleza", "CE"), ("Salvador", "BA"),
           ("Belo Horizonte", "MG"), ("Curitiba", "PR"), ("Porto Alegre", "RS"), ("Recife", "PE"),
           ("Goiânia", "GO"), ("Belém", "PA")]
ESCALAS = ["1:1.000", "1:2.000", "1:5.000", "1:10.000", "1:25.000", "1:50.000", "1:100.000", "1:250.000"]
TIPOS = ["SCN Carta Topográfica Matricial", "SCN Carta Topográfica Vetorial", "SCN Carta Ortoimagem",
         "SCN Carta Ortoimagem Banda P Pol HH", "SCN Carta Ortoimagem Banda X Pol HH", "MDT — RAM",
         "MDS — RAM", "CIRC", "Cartas Temáticas Não SCN"]
PROJETOS = ["Mapeamento Sistemático", "Olimpíadas Rio 2016", "Copa do Mundo 2014", "Copa das Confederações",
            "Base Cartográfica Digital da Bahia", "Base Cartográfica Digital de Rondônia",
            "Base Cartográfica Digital do Amapá", "NGA-BECA", "AMAN"]
MI = ["2965-2-NE", "2866-3", "2901", "530", "3010", "2965", "2866-2-SO", "2901-4-NE", "531-1-NE", "2965-3", "2866-3-NO", "3010-2-SE"]
INOM = ["SF-22-Y-D", "SF-22-Y-D-II", "SF-22-Y-D-II-4", "SF-22-Y-D-II-4-SE", "SG-22-X-A", "SF-23-V-C", "SG-21-Z-B",
        "SH-22-W-A-III-1-NE", "SG-22-Z-D-II-3", "SF-24-Y-A"]
NOMES = ["Passo da Seringueira", "Vale do Guaporé", "Porto Velho", "Serra do Cachimbo", "Rio Verde", "Boa Vista",
         "Chapada dos Guimarães", "Lagoa Mirim", "Ilha do Bananal", "Pico da Neblina", "Foz do Iguaçu", "Baía de Todos os Santos"]

# Grade: 6 colunas de 6° de longitude (-74..-38) × 5 linhas de 7,5° de latitude (5..-32,5)
LARGURA, ALTURA, X0, Y0 = 6.0, 7.5, -74.0, 5.0


def celula(indice: int) -> tuple[float, float, float, float]:
    col, lin = indice % 6, indice // 6
    xmin, ymax = X0 + col * LARGURA, Y0 - lin * ALTURA
    return xmin, ymax - ALTURA, xmin + LARGURA, ymax


def sql_str(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def envelope(b, multi=False) -> str:
    base = f"ST_MakeEnvelope({b[0]:.4f}, {b[1]:.4f}, {b[2]:.4f}, {b[3]:.4f}, 4326)"
    return f"ST_Multi({base})" if multi else base


def caixa_dentro(b, fracao: float, rng: random.Random) -> tuple[float, float, float, float]:
    w, h = (b[2] - b[0]) * fracao, (b[3] - b[1]) * fracao
    x = rng.uniform(b[0], b[2] - w)
    y = rng.uniform(b[1], b[3] - h)
    return x, y, x + w, y + h


def main() -> None:
    caixas = {sigla: celula(i) for i, (_, sigla) in enumerate(ESTADOS)}
    linhas = [
        "-- =====================================================================",
        "-- SEMENTE SINTÉTICA — gerada por scripts/gerar_seed_sintetico.py (seed 7)",
        "-- Não representa o acervo da DSG. Geometrias são retângulos numa grade.",
        "-- Uso exclusivo: demonstrar o pipeline ponta a ponta. Fora de métrica.",
        "-- =====================================================================",
        "COMMENT ON TABLE datasets IS 'SEMENTE SINTÉTICA (scripts/gerar_seed_sintetico.py) — não é o acervo real da DSG';",
        "COMMENT ON TABLE estados IS 'SINTÉTICO — retângulos em grade, não a malha do IBGE';",
        "COMMENT ON TABLE municipios IS 'SINTÉTICO — retângulos dentro do estado, não a malha do IBGE';",
        "COMMENT ON TABLE areas_suprimento IS 'SINTÉTICO — faixas verticais da grade';",
        "",
        "-- estados",
    ]
    for nome, sigla in ESTADOS:
        linhas.append(f"INSERT INTO estados (nome, sigla, geom) VALUES ({sql_str(nome)}, '{sigla}', "
                      f"{envelope(caixas[sigla], multi=True)});")
    linhas += ["", "-- municípios (14 cidades-referência do dataset)"]
    rng = random.Random(7)
    caixas_cidade = {}
    for nome, uf in CIDADES:
        caixa = caixa_dentro(caixas[uf], 0.25, rng)
        caixas_cidade[nome] = caixa
        linhas.append(f"INSERT INTO municipios (nome, sigla_estado, geom) VALUES ({sql_str(nome)}, '{uf}', "
                      f"{envelope(caixa, multi=True)});")
    linhas += ["", "-- áreas de suprimento: 5 faixas verticais (colunas 0, 1, 2, 3, 4-5 da grade)"]
    faixas = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6)]
    for n, (c0, c1) in enumerate(faixas, start=1):
        b = (X0 + c0 * LARGURA, Y0 - 5 * ALTURA, X0 + c1 * LARGURA, Y0)
        linhas.append(f"INSERT INTO areas_suprimento (nome, sigla, geom) VALUES "
                      f"('{n}° Centro de Geoinformação', '{n}° CGEO', {envelope(b, multi=True)});")

    linhas += ["", "-- datasets (produtos)"]
    produtos: list[tuple] = []

    def produto(nome, mi, inom, escala, tipo, projeto, pub, cri, caixa):
        produtos.append((nome, mi, inom, escala, tipo, projeto, pub, cri, caixa))

    def data_aleatoria(a0=2015, a1=2026) -> date:
        inicio = date(a0, 1, 1)
        return inicio + timedelta(days=rng.randint(0, (date(a1, 9, 1) - inicio).days))

    # 1) casos "âncora": garantem resultado não vazio nas consultas P/N mais citadas
    ancoras = [
        ("Passo da Seringueira", "2965-2-NE", "SF-22-Y-D-II-4-SE", "1:25.000", TIPOS[0], "Mapeamento Sistemático", date(2023, 5, 10), date(2022, 11, 3), "RS"),
        ("Porto Velho", "2866-3", "SF-22-Y-D-II", "1:50.000", TIPOS[0], "Base Cartográfica Digital de Rondônia", date(2024, 3, 15), date(2023, 8, 20), "RO"),
        ("Vale do Guaporé", "2901", "SF-22-Y-D", "1:100.000", TIPOS[2], "Base Cartográfica Digital de Rondônia", date(2021, 7, 1), date(2020, 2, 14), "RO"),
        ("Maracanã", "2901-4-NE", "SF-23-V-C", "1:25.000", TIPOS[2], "Olimpíadas Rio 2016", date(2016, 6, 1), date(2015, 12, 1), "RJ"),
        ("Castelão", "530", "SG-22-X-A", "1:250.000", TIPOS[0], "Copa das Confederações", date(2013, 5, 20), date(2012, 10, 1), "CE"),
        ("Chapada dos Guimarães", "3010", "SG-21-Z-B", "1:50.000", TIPOS[5], "Mapeamento Sistemático", date(2019, 4, 2), date(2018, 1, 9), "MT"),
        ("Recife Antigo", "531-1-NE", "SF-24-Y-A", "1:25.000", TIPOS[2], "Mapeamento Sistemático", date(2022, 9, 9), date(2021, 6, 30), "PE"),
        ("Lagoa Mirim", "2965-3", "SH-22-W-A-III-1-NE", "1:25.000", TIPOS[1], "Mapeamento Sistemático", date(2026, 3, 3), date(2025, 11, 11), "RS"),
    ]
    for nome, mi, inom, esc, tipo, proj, pub, cri, uf in ancoras:
        produto(nome, mi, inom, esc, tipo, proj, pub, cri, caixa_dentro(caixas[uf], 0.12, rng))
    # produtos dentro de cada cidade-referência (para `city` devolver algo)
    for nome_cidade, _uf in CIDADES:
        for _ in range(2):
            pub = data_aleatoria()
            produto(f"{nome_cidade} {rng.choice(['Norte', 'Sul', 'Leste', 'Oeste', 'Centro'])}",
                    rng.choice(MI), rng.choice(INOM), rng.choice(ESCALAS), rng.choice(TIPOS),
                    rng.choice(PROJETOS), pub, pub - timedelta(days=rng.randint(30, 700)),
                    caixa_dentro(caixas_cidade[nome_cidade], 0.5, rng))
    # 2) cobertura: 3 produtos por UF
    for _nome_uf, uf in ESTADOS:
        for _ in range(3):
            pub = data_aleatoria()
            produto(f"{rng.choice(NOMES)} ({uf})", rng.choice(MI), rng.choice(INOM), rng.choice(ESCALAS),
                    rng.choice(TIPOS), rng.choice(PROJETOS), pub, pub - timedelta(days=rng.randint(30, 900)),
                    caixa_dentro(caixas[uf], 0.15, rng))

    for nome, mi, inom, esc, tipo, proj, pub, cri, caixa in produtos:
        linhas.append(
            "INSERT INTO datasets (nome, mi, inom, escala, tipo_produto, projeto, data_publicacao, data_criacao, geom) "
            f"VALUES ({sql_str(nome)}, {sql_str(mi)}, {sql_str(inom)}, {sql_str(esc)}, {sql_str(tipo)}, "
            f"{sql_str(proj)}, '{pub.isoformat()}', '{cri.isoformat()}', {envelope(caixa)});"
        )
    linhas.append(f"-- total: {len(produtos)} produtos sintéticos")
    DESTINO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"{DESTINO.relative_to(RAIZ)}: {len(ESTADOS)} estados, {len(CIDADES)} municípios, 5 CGEOs, {len(produtos)} produtos")


if __name__ == "__main__":
    main()
