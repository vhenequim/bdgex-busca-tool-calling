"""Carrega o acervo real do BDGEx (metadados do CSW) num PostGIS com o esquema do protótipo.

Análise EXPLORATÓRIA, feita depois da entrega do texto, para responder à pergunta da banca
"por que não testaram a busca com o acervo real?". Não roda modelo nenhum e não altera
nenhum resultado do texto. A SQL de busca continua a de `pfc_busca.tools.montar_sql`.

    python scripts/acervo_real/carregar_acervo.py \
        [--dsn postgresql://pfc@localhost:5433/acervo_real] \
        [--malhas DIR_COM_AS_MALHAS_DO_IBGE] [--sem-conferencia]

O script é idempotente: apaga e recria as tabelas do esquema do protótipo
(`db/init_schema_prototipo.sql`, sem as linhas CREATE EXTENSION, que já existem no banco) e
uma tabela auxiliar `csw_origem` (rastreabilidade de cada linha de `datasets` até o registro
CSW), carrega tudo e, ao fim, confere 20 registros sorteados contra o JSON do CSW e roda
algumas buscas de sanidade com `tools.montar_sql`. As contagens e o mapeamento vão para
`results/acervo_real/carga.json` (só agregados; o dump bruto continua fora do git).

Mapeamento CSW -> esquema do protótipo (decisões, todas documentadas em `carga.json`)
--------------------------------------------------------------------------------------
- Registros: um por `dc:identifier` distinto. A coleta de 28/09/2026 devolveu 31.190
  registros em 4 páginas, mas só 21.229 identificadores distintos: a página 3, a partir da
  posição 1.230, e a página 4 inteira repetem, byte a byte, registros da página 2 (paginação
  instável do servidor CSW). Carregar as cópias criaria "edições" que não existem, então
  elas são descartadas. O servidor declara 31.190 registros; se esse número conta registros
  distintos (não verificado), cerca de 9.961 registros do catálogo NÃO estão no dump.
  Além das cópias da paginação, o próprio catálogo tem registros duplicados (UUIDs distintos
  com o mesmo INOM, tipo, escala e data); eles ficam, e são contados em `carga.json`.
- `id` = `dc:identifier` (todos são UUID válidos), o que liga cada linha ao JSON do CSW.
- `nome`, `mi`, `inom`, `escala`, `tipo_produto`: extraídos por
  `scripts/lote_validacao/catalogo.py` (`carregar_bdgex`), o MESMO leitor que sorteou os
  valores do gabarito, no vocabulário de `pfc_busca.schema` (ESCALAS, TIPOS_PRODUTO).
  `nome` = nome da folha quando houver, senão o título do registro. Títulos fora do padrão
  "NOME - INOM - ESCALA" (ex.: "PAJEÚ-SD-23-X-B-V-3-50.000", INOM com travessão "–") que o
  leitor não decompõe têm o INOM e o nome recuperados por `inom_do_titulo`/`nome_do_titulo`
  (contados à parte; nenhum alvo do gabarito vem desses registros). O código MI fica como o
  catálogo o escreve (o BDGEx mistura "0757-4" e "757-4" para a mesma folha; não se
  normaliza, porque essa é uma ambiguidade real do acervo).
- Escala: a do título (`escala_canonica`, ou um "1:NN.000" explícito em qualquer ponto do
  título); se o título não traz escala, a do nível do
  código INOM (articulação sistemática: 4 partes = 1:250.000, 5 = 1:100.000,
  6 = 1:50.000, 7 = 1:25.000). Sem nenhuma das duas: ESCALA_DESCONHECIDA.
- Tipo de produto: `tipo_do_registro` (heurística sobre título e formato). O CSW não traz
  um campo de tipo; registros que a heurística não reconhece (em geral `dc:format` = "Array")
  ficam com TIPO_DESCONHECIDO. Os valores sentinela não pertencem ao vocabulário, logo
  nenhum filtro `scale`/`productType` os casa por acidente.
- `projeto` = '' (o CSW não traz projeto). Toda busca com `project` devolve zero.
- `data_publicacao` = `data_criacao` = `dc:date` (o CSW não distingue as duas; `dct:modified`
  é igual a `dc:date` em todos os registros). Registro sem data: DATA_DESCONHECIDA.
- `geom` = `ows:BoundingBox` (EPSG 4326, ordem lat/lon no CSW). Caixas ausentes, nulas
  (0 0 / 0 0), com coordenadas fora de faixa (pixels) recebem GEOM_SENTINELA, um quadrado
  minúsculo no Golfo da Guiné que não intersecta nenhum estado, município ou área.
  Caixas degeneradas (largura ou altura zero) são expandidas em 1e-6 grau.
- `estados` e `municipios`: malhas oficiais do IBGE (API de malhas v3, qualidade
  intermediária, SIRGAS 2000 tratado como 4326), com nomes e siglas de
  `data/lote_validacao/ibge_municipios.json` pelo código IBGE.
- `areas_suprimento`: NÃO há polígonos oficiais das áreas de suprimento no repositório. A
  aproximação é a área coberta pelos registros produzidos por cada CGEO (`dc:creator`):
  união das bounding boxes válidas (as sem caixa válida ficam de fora; o teto de
  AREA_MAX_CAIXA grau² por caixa é só uma salvaguarda e não exclui nenhuma) com buffer
  negativo de BUFFER_NEGATIVO grau, para que folhas vizinhas que só encostam na borda não
  contem como interseção. É uma aproximação, não a divisão oficial: o filtro `supplyArea`
  passa a significar "a região onde aquele CGEO tem produtos no catálogo", que se afasta
  muito da área de suprimento real (o 1º CGEO cobre boa parte de RR e do AM, por exemplo;
  a fração de cada UF coberta por cada área vai para `carga.json`). Contagens absolutas
  com `supplyArea` não representam a área real.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from collections import Counter
from datetime import date
from pathlib import Path

import psycopg

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts" / "lote_validacao"))

import catalogo  # noqa: E402
from catalogo import _texto  # noqa: E402

from pfc_busca import schema, tools  # noqa: E402

DSN_PADRAO = "postgresql://pfc@localhost:5433/acervo_real"
MALHAS_PADRAO = Path(
    r"C:\Users\vhene\AppData\Local\Temp\claude\C--Users-vhene-pfc"
    r"\3eb8d7a1-493a-4998-8b27-66c44e89980d\scratchpad\acervo_real"
)
ARQ_SCHEMA = RAIZ / "db" / "init_schema_prototipo.sql"
ARQ_IBGE = RAIZ / "data" / "lote_validacao" / "ibge_municipios.json"
SAIDA = RAIZ / "results" / "acervo_real" / "carga.json"

ESCALA_DESCONHECIDA = "?"                     # cabe em VARCHAR(10); fora de schema.ESCALAS
TIPO_DESCONHECIDO = "(tipo não identificado)"  # fora de schema.TIPOS_PRODUTO
NOME_DESCONHECIDO = "(sem título)"
DATA_DESCONHECIDA = date(1, 1, 1)
GEOM_SENTINELA = "SRID=4326;POLYGON((0 0,0.000001 0,0.000001 0.000001,0 0.000001,0 0))"
BUFFER_NEGATIVO = 0.001     # grau (~110 m); as caixas do CSW vêm arredondadas em 1e-5 grau
AREA_MAX_CAIXA = 4.0        # grau²; uma folha 1:250.000 tem 1,5 grau²
ESCALA_POR_NIVEL_INOM = {4: "1:250.000", 5: "1:100.000", 6: "1:50.000", 7: "1:25.000"}

assert ESCALA_DESCONHECIDA not in schema.ESCALAS and TIPO_DESCONHECIDO not in schema.TIPOS_PRODUTO


# ---------------------------------------------------------------------------
# Leitura do CSW
# ---------------------------------------------------------------------------


def ler_csw() -> tuple[list[dict], dict]:
    """Registros brutos distintos (na ordem da coleta) e estatística da duplicação."""
    brutos: list[dict] = []
    casados = None
    for arquivo in sorted(catalogo.DIR_CSW.glob("pagina_*.json")):
        corpo = json.loads(arquivo.read_text(encoding="utf-8"))["csw:GetRecordsResponse"]["csw:SearchResults"]
        casados = casados or int(corpo["@numberOfRecordsMatched"])
        itens = corpo.get("csw:Record") or []
        brutos += itens if isinstance(itens, list) else [itens]
    copias = Counter(r.get("dc:identifier") for r in brutos)
    distintos: dict[str, dict] = {}
    divergentes = 0
    for r in brutos:
        i = r.get("dc:identifier")
        if i in distintos:
            if json.dumps(r, sort_keys=True) != json.dumps(distintos[i], sort_keys=True):
                divergentes += 1
            continue
        distintos[i] = r
    estat = {
        "registros_no_dump": len(brutos),
        "numberOfRecordsMatched": casados,
        "identificadores_distintos": len(distintos),
        "copias_descartadas": len(brutos) - len(distintos),
        "identificadores_com_2_copias": sum(1 for n in copias.values() if n == 2),
        "identificadores_com_3_copias": sum(1 for n in copias.values() if n == 3),
        "copias_com_conteudo_diferente": divergentes,
    }
    return list(distintos.values()), estat


TRACOS = str.maketrans({"–": "-", "—": "-", "−": "-"})   # en dash, em dash, sinal de menos
RE_INOM_NO_TITULO = re.compile(
    r"(?<![A-Z0-9])([NS][A-Z]-\d{2}-[VXYZ](?:-[A-D](?:-(?:VI|IV|V|I{1,3})(?:-[1-4](?:-(?:NO|NE|SO|SE))?)?)?)?)"
    r"(?=-\d{1,3}\.?000(?!\d)|\s|$|_)")   # depois do INOM vem a escala ("-50.000"), espaço ou fim
RE_ESCALA_EXPLICITA = re.compile(r"1\s?:\s?(\d{1,3})\.?000(?!\d)")
RE_NOME_COLADO = re.compile(r"^([^\d-][^\d]*?)\s*-\s*[NS][A-Z]-\d{2}-")


def inom_do_titulo(titulo: str) -> str | None:
    """INOM dentro de um título fora do padrão "NOME - INOM - ESCALA" (ex.: "PAJEÚ-SD-23-X-B-V-3-50.000",
    "2354-3-NE-SE-24-V-D-I-3-NE-25.000", "CÓRREGO BOREVI - SF−21−Z−B−V−3−SO - 25.000"), validado pela
    mesma expressão de `catalogo`."""
    t = titulo.upper().translate(TRACOS)
    for m in RE_INOM_NO_TITULO.finditer(t):
        if catalogo.RE_INOM.match(m.group(1)):
            return m.group(1)
    return None


def nome_do_titulo(titulo: str) -> str | None:
    """Nome da folha em títulos colados ao INOM ("PAJEÚ-SD-23-X-B-V-3-50.000" -> "Pajeú")."""
    m = RE_NOME_COLADO.match(titulo.translate(TRACOS))
    if not m or not re.search(r"[A-Za-zÀ-ú]{3}", m.group(1)):
        return None
    nome = m.group(1).strip()
    # mesmas exclusões do leitor: descrição de produto não é nome de folha
    if catalogo.tipo_do_registro(nome, "") is not None or catalogo.sem_acento(nome).upper().startswith(
            ("VAZIO", "CARTA ", "MOSAICO", "ORTOIMAGEM", "MODELO")):
        return None
    return catalogo.nome_proprio(nome)


def escala_do_inom(inom: str | None) -> str | None:
    if not inom:
        return None
    return ESCALA_POR_NIVEL_INOM.get(len(inom.split("-")))


def caixa(registro: dict) -> tuple[str, str]:
    """(EWKT da geometria, situação da caixa)."""
    b = registro.get("ows:BoundingBox")
    if not isinstance(b, dict):
        return GEOM_SENTINELA, "sem caixa"
    try:
        la0, lo0 = map(float, b["ows:LowerCorner"].split())
        la1, lo1 = map(float, b["ows:UpperCorner"].split())
    except (KeyError, ValueError):
        return GEOM_SENTINELA, "caixa ilegível"
    if la0 == la1 == lo0 == lo1 == 0:
        return GEOM_SENTINELA, "caixa nula (0 0)"
    if not (-90 <= la0 <= 90 and -90 <= la1 <= 90 and -180 <= lo0 <= 180 and -180 <= lo1 <= 180):
        return GEOM_SENTINELA, "coordenadas fora de faixa"
    situacao = "ok"
    if la1 < la0 or lo1 < lo0:
        la0, la1, lo0, lo1 = min(la0, la1), max(la0, la1), min(lo0, lo1), max(lo0, lo1)
        situacao = "cantos invertidos"
    if la0 == la1 or lo0 == lo1:
        la0, la1, lo0, lo1 = la0 - 1e-6, la1 + 1e-6, lo0 - 1e-6, lo1 + 1e-6
        situacao = "degenerada (expandida)"
    wkt = f"POLYGON(({lo0} {la0},{lo1} {la0},{lo1} {la1},{lo0} {la1},{lo0} {la0}))"
    return f"SRID=4326;{wkt}", situacao


def mapear(brutos: list[dict]) -> list[dict]:
    """Uma linha de `datasets` (+ dados de origem) por registro CSW distinto."""
    extraidos = {r["id"]: r for r in catalogo.carregar_bdgex()}  # mesmo leitor do gabarito
    linhas = []
    for bruto in brutos:
        e = dict(extraidos[bruto["dc:identifier"]])
        inom_recuperado = nome_recuperado = False
        if e["inom"] is None and (achado := inom_do_titulo(e["titulo"])):
            e["inom"], inom_recuperado = achado, True
        if e["nome_folha"] and re.search(r"[NS][A-Z]-\d{2}-", e["nome_folha"].upper()):
            # o leitor às vezes devolve o INOM dentro do nome ("Acaraú- Sb-24-y-b", "- Na-22-y-b-iii-2-so")
            e["nome_folha"], nome_recuperado = nome_do_titulo(e["titulo"]), True
        if e["nome_folha"] is None and (achado := nome_do_titulo(e["titulo"])):
            e["nome_folha"], nome_recuperado = achado, True
        escala, origem_escala = e["escala"], "título"
        if escala is None and (m := RE_ESCALA_EXPLICITA.search(e["titulo"])):
            # "ORTOIMAGEM 1:50.000 ÁREA SA-20-X-B-IV": `escala_canonica` exige fronteira de palavra após "000"
            escala = f"1:{m.group(1)}.000" if f"1:{m.group(1)}.000" in schema.ESCALAS else None
        if escala is None:
            escala, origem_escala = escala_do_inom(e["inom"]), "nível do INOM"
        if escala is None:
            escala, origem_escala = ESCALA_DESCONHECIDA, None
        data_txt = _texto(bruto.get("dc:date")).strip()
        try:
            data = date.fromisoformat(data_txt[:10])
        except ValueError:
            data = DATA_DESCONHECIDA
        geom, situacao = caixa(bruto)
        linhas.append({
            "id": e["id"],
            "nome": (e["nome_folha"] or e["titulo"] or NOME_DESCONHECIDO)[:200],
            "mi": e["mi"], "inom": e["inom"],
            "escala": escala, "tipo_produto": e["tipo"] or TIPO_DESCONHECIDO,
            "projeto": "", "data": data, "geom": geom,
            # origem (tabela csw_origem)
            "titulo": e["titulo"], "formato": _texto(bruto.get("dc:format")),
            "criador": _texto(bruto.get("dc:creator")), "cgeo": e["cgeo"],
            "origem_escala": origem_escala, "tipo_reconhecido": e["tipo"] is not None,
            "nome_da_folha": e["nome_folha"] is not None,
            "inom_recuperado": inom_recuperado, "nome_recuperado": nome_recuperado,
            "data_original": data_txt or None, "situacao_caixa": situacao,
        })
    return linhas


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

DDL_ORIGEM = """
CREATE TABLE csw_origem (
    id uuid PRIMARY KEY REFERENCES datasets(id) ON DELETE CASCADE,
    titulo TEXT, formato TEXT, criador TEXT, cgeo TEXT,
    origem_escala TEXT, tipo_reconhecido BOOLEAN, nome_da_folha BOOLEAN,
    inom_recuperado BOOLEAN, nome_recuperado BOOLEAN,
    data_original TEXT, situacao_caixa TEXT
);
"""


def recriar_esquema(cur: psycopg.Cursor) -> None:
    cur.execute("DROP TABLE IF EXISTS csw_origem, datasets, areas_suprimento, municipios, estados CASCADE")
    sql = "\n".join(linha for linha in ARQ_SCHEMA.read_text(encoding="utf-8").splitlines()
                    if not linha.strip().upper().startswith("CREATE EXTENSION"))
    cur.execute(sql)
    cur.execute(DDL_ORIGEM)


def carregar_datasets(cur: psycopg.Cursor, linhas: list[dict]) -> None:
    colunas = ("id", "nome", "mi", "inom", "escala", "tipo_produto", "projeto",
               "data_publicacao", "data_criacao", "geom")
    with cur.copy(f"COPY datasets ({', '.join(colunas)}) FROM STDIN") as copia:
        for x in linhas:
            copia.write_row((x["id"], x["nome"], x["mi"], x["inom"], x["escala"], x["tipo_produto"],
                             x["projeto"], x["data"], x["data"], x["geom"]))
    colunas_o = ("id", "titulo", "formato", "criador", "cgeo", "origem_escala", "tipo_reconhecido",
                 "nome_da_folha", "inom_recuperado", "nome_recuperado", "data_original", "situacao_caixa")
    with cur.copy(f"COPY csw_origem ({', '.join(colunas_o)}) FROM STDIN") as copia:
        for x in linhas:
            copia.write_row(tuple(x[c] for c in colunas_o))


def _geom_sql(param: str = "%s") -> str:
    # GeoJSON -> MultiPolygon válido, SRID 4326
    return (f"ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_SetSRID(ST_GeomFromGeoJSON({param}), 4326)), 3))")


def carregar_ibge(cur: psycopg.Cursor, malhas: Path) -> dict:
    municipios = json.loads(ARQ_IBGE.read_text(encoding="utf-8"))
    nome_mun, uf_por_cod = {}, {}
    for m in municipios:
        uf = ((m.get("microrregiao") or {}).get("mesorregiao") or {}).get("UF") or \
             ((m.get("regiao-imediata") or {}).get("regiao-intermediaria") or {}).get("UF") or {}
        nome_mun[str(m["id"])] = (m["nome"], uf.get("sigla"))
        if uf.get("id"):
            uf_por_cod[str(uf["id"])] = (uf["nome"], uf["sigla"])

    ufs = json.loads((malhas / "ibge_uf_intermediaria.geojson").read_text(encoding="utf-8"))["features"]
    for f in ufs:
        nome, sigla = uf_por_cod[f["properties"]["codarea"]]
        cur.execute(f"INSERT INTO estados (nome, sigla, geom) VALUES (%s, %s, {_geom_sql()})",
                    (nome, sigla, json.dumps(f["geometry"])))

    muns = json.loads((malhas / "ibge_mun_intermediaria.geojson").read_text(encoding="utf-8"))["features"]
    sem_nome = []
    linhas = []
    for f in muns:
        cod = f["properties"]["codarea"]
        if cod not in nome_mun:
            sem_nome.append(cod)
            continue
        nome, sigla = nome_mun[cod]
        linhas.append((nome, sigla, json.dumps(f["geometry"])))
    cur.executemany(f"INSERT INTO municipios (nome, sigla_estado, geom) VALUES (%s, %s, {_geom_sql()})", linhas)
    codigos_malha = {f["properties"]["codarea"] for f in muns}
    return {
        "estados": len(ufs), "municipios_na_malha": len(muns),
        "municipios_na_lista_ibge": len(municipios),
        "malhas_sem_nome_na_lista": sem_nome,
        "lista_sem_malha": sorted(f"{c} {nome_mun[c][0]}/{nome_mun[c][1]}"
                                  for c in set(nome_mun) - codigos_malha),
    }


def carregar_areas(cur: psycopg.Cursor) -> list[dict]:
    estat = []
    for n in range(1, 6):
        nome = f"{n}° Centro de Geoinformação"
        assert nome in schema.CENTROS_GEOINFORMACAO
        cur.execute(
            """SELECT count(*) FILTER (WHERE o.situacao_caixa NOT IN ('ok','cantos invertidos')),
                      count(*) FILTER (WHERE o.situacao_caixa IN ('ok','cantos invertidos')
                                         AND ST_Area(d.geom) > %s),
                      count(*)
                 FROM datasets d JOIN csw_origem o USING (id) WHERE o.cgeo = %s""",
            (AREA_MAX_CAIXA, nome))
        sem_caixa, acima_do_teto, total = cur.fetchone()
        excluidos = sem_caixa + acima_do_teto
        cur.execute(
            f"""INSERT INTO areas_suprimento (nome, sigla, geom)
                SELECT %s, %s, ST_Multi(ST_CollectionExtract(ST_MakeValid(
                           ST_Buffer(ST_Union(d.geom), -{BUFFER_NEGATIVO})), 3))
                  FROM datasets d JOIN csw_origem o USING (id)
                 WHERE o.cgeo = %s AND o.situacao_caixa IN ('ok', 'cantos invertidos')
                   AND ST_Area(d.geom) <= %s
             RETURNING ST_Area(geom), ST_NumGeometries(geom)""",
            (nome, f"{n}° CGEO", nome, AREA_MAX_CAIXA))
        area, partes = cur.fetchone()
        estat.append({"nome": nome, "registros_do_cgeo": total, "caixas_usadas": total - excluidos,
                      "registros_sem_caixa_valida": sem_caixa, "caixas_acima_do_teto_de_area": acima_do_teto,
                      "area_grau2": round(area, 2), "poligonos": partes})
    # sobreposição entre as áreas aproximadas (a divisão oficial não se sobrepõe)
    cur.execute("""SELECT a.sigla, b.sigla, round(ST_Area(ST_Intersection(a.geom, b.geom))::numeric, 2)
                     FROM areas_suprimento a JOIN areas_suprimento b ON a.id < b.id
                    WHERE ST_Intersects(a.geom, b.geom)""")
    sobre = [{"areas": f"{x} x {y}", "area_grau2": float(z)} for x, y, z in cur.fetchall()]
    # fração de cada UF coberta por cada área aproximada (>= 5%): mostra o quanto ela se afasta da divisão real
    cur.execute("""SELECT a.sigla, e.sigla,
                          round((ST_Area(ST_Intersection(a.geom, e.geom)) / ST_Area(e.geom))::numeric, 2)
                     FROM areas_suprimento a JOIN estados e ON ST_Intersects(a.geom, e.geom)
                    ORDER BY a.sigla, 3 DESC""")
    cobertura: dict[str, dict[str, float]] = {}
    for area_sigla, uf, frac in cur.fetchall():
        if frac >= 0.05:
            cobertura.setdefault(area_sigla, {})[uf] = float(frac)
    return estat + [{"sobreposicoes": sobre}, {"fracao_de_cada_uf_coberta": cobertura}]


def grafias_do_mi(linhas: list[dict]) -> dict:
    """Códigos MI escritos com e sem zero à esquerda no catálogo ("0757-4" e "757-4")."""
    grafias: dict[str, set[str]] = {}
    for x in linhas:
        if x["mi"]:
            numero, sep, resto = x["mi"].partition("-")
            grafias.setdefault((numero.lstrip("0") or "0") + sep + resto, set()).add(x["mi"])
    duplas = {k: v for k, v in grafias.items() if len(v) > 1}
    curtos = Counter(x["escala"] for x in linhas if x["mi"] and len(x["mi"].split("-")[0]) < 4)
    return {"codigos_mi_normalizados": len(grafias),
            "codigos_com_duas_grafias": len(duplas),
            "grafias_distintas_nesses_codigos": sum(len(v) for v in duplas.values()),
            "mi_com_menos_de_4_digitos_por_escala": dict(curtos.most_common()),
            "nota": "MI com menos de 4 dígitos é a numeração normal da 1:250.000; a ambiguidade é o mesmo "
                    "código escrito com e sem zero à esquerda"}


def duplicatas_do_catalogo(linhas: list[dict]) -> dict:
    """Registros com UUIDs distintos e o mesmo INOM, tipo, escala e data (duplicação do próprio catálogo)."""
    grupos = Counter((x["inom"], x["tipo_produto"], x["escala"], x["data"]) for x in linhas if x["inom"])
    rep = {k: n for k, n in grupos.items() if n > 1}
    return {"criterio": "mesmo INOM, tipo de produto, escala e data, com dc:identifier distintos",
            "grupos": len(rep), "registros": sum(rep.values()),
            "registros_a_mais": sum(n - 1 for n in rep.values())}


# ---------------------------------------------------------------------------
# Conferência
# ---------------------------------------------------------------------------


def conferir_amostra(cur: psycopg.Cursor, brutos: list[dict], n: int = 20, semente: int = 2026) -> list[dict]:
    """Confere n registros sorteados: o que está no banco contra o JSON do CSW."""
    amostra = random.Random(semente).sample(brutos, n)
    saida = []
    for b in amostra:
        cur.execute("""SELECT d.nome, d.mi, d.inom, d.escala, d.tipo_produto, d.data_publicacao,
                              d.data_criacao, ST_XMin(d.geom), ST_YMin(d.geom), ST_XMax(d.geom),
                              ST_YMax(d.geom), o.titulo, o.situacao_caixa
                         FROM datasets d JOIN csw_origem o USING (id) WHERE d.id = %s""",
                    (b["dc:identifier"],))
        (nome, mi, inom, escala, tipo, dpub, dcri, x0, y0, x1, y1, titulo, situacao) = cur.fetchone()
        titulo_csw = _texto(b.get("dc:title")).strip()
        problemas = []
        if titulo != titulo_csw:
            problemas.append("título")
        if dpub.isoformat() != _texto(b.get("dc:date"))[:10] or dpub != dcri:
            problemas.append("data")
        caixa_csw = b.get("ows:BoundingBox")
        if situacao == "ok":
            la0, lo0 = map(float, caixa_csw["ows:LowerCorner"].split())
            la1, lo1 = map(float, caixa_csw["ows:UpperCorner"].split())
            if max(abs(x0 - lo0), abs(y0 - la0), abs(x1 - lo1), abs(y1 - la1)) > 1e-9:
                problemas.append("caixa")
        if nome not in titulo_csw.title() and nome.upper() not in titulo_csw.upper() and nome != titulo_csw:
            problemas.append("nome")
        if mi and mi not in titulo_csw and mi != _texto(b.get("dct:alternative")).strip():
            problemas.append("mi")
        if inom and inom not in titulo_csw.upper():
            problemas.append("inom")
        if escala in schema.ESCALAS:
            num = escala.split(":")[1].replace(".", "")
            if num.lstrip("0") not in titulo_csw.replace(".", "").replace(" ", "") and not inom:
                problemas.append("escala")
        elif escala != ESCALA_DESCONHECIDA:
            problemas.append("escala fora do vocabulário")
        if tipo not in schema.TIPOS_PRODUTO and tipo != TIPO_DESCONHECIDO:
            problemas.append("tipo fora do vocabulário")
        saida.append({
            "id": b["dc:identifier"], "titulo_csw": titulo_csw, "formato_csw": _texto(b.get("dc:format")),
            "data_csw": _texto(b.get("dc:date")), "caixa_csw": caixa_csw and
            f'{caixa_csw.get("ows:LowerCorner")} / {caixa_csw.get("ows:UpperCorner")}',
            "banco": {"nome": nome, "mi": mi, "inom": inom, "escala": escala, "tipo_produto": tipo,
                      "data": dpub.isoformat(), "caixa_lonlat": [x0, y0, x1, y1], "situacao_caixa": situacao},
            "problemas": problemas,
        })
    return saida


BUSCAS_SANIDADE = [
    ("folha por MI (4 dígitos)", {"keyword": "1950-3-NO"}),
    ("folha por MI (sem zero à esquerda, como no título)", {"keyword": "757-4"}),
    ("mesma folha por MI com zero à esquerda", {"keyword": "0757-4"}),
    ("folha por INOM", {"keyword": "SD-23-X-B-V-3-NO"}),
    ("folha pelo nome", {"keyword": "Calumbi"}),
    ("município", {"city": "Santa Maria"}),
    ("município + escala", {"city": "Porto Alegre", "scale": "1:25.000"}),
    ("estado", {"state": "Rondônia"}),
    ("estado por sigla (ILIKE '%AM%')", {"state": "AM"}),
    ("estado + tipo", {"state": "Bahia", "productType": "SCN Carta Topográfica Vetorial"}),
    ("área de suprimento", {"supplyArea": "4° Centro de Geoinformação"}),
    ("projeto (ausente no CSW)", {"project": "Mapeamento Sistemático"}),
    ("período", {"keyword": "Santa Maria", "publicationPeriod": {"start": "2015-01-01", "end": "2020-12-31"}}),
]


def buscas_sanidade(cur: psycopg.Cursor) -> list[dict]:
    saida = []
    for rotulo, params in BUSCAS_SANIDADE:
        sql_contagem, sql_principal, args = tools.montar_sql(params)
        inicio = time.perf_counter()
        cur.execute(sql_contagem, args)
        total = cur.fetchone()[0]
        cur.execute(sql_principal, args)
        itens = cur.fetchall()
        ms = (time.perf_counter() - inicio) * 1000
        saida.append({
            "busca": rotulo, "params": params, "total": total, "latencia_ms": round(ms, 1),
            "primeiros": [f"{r[0]} | MI {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[6]}" for r in itens[:5]],
        })
    return saida


# ---------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--dsn", default=DSN_PADRAO)
    p.add_argument("--malhas", type=Path, default=MALHAS_PADRAO,
                   help="pasta com ibge_uf_intermediaria.geojson e ibge_mun_intermediaria.geojson")
    p.add_argument("--sem-conferencia", action="store_true")
    args = p.parse_args()

    t0 = time.perf_counter()
    brutos, estat_dump = ler_csw()
    linhas = mapear(brutos)

    with psycopg.connect(args.dsn) as conexao:
        with conexao.cursor() as cur:
            recriar_esquema(cur)
            carregar_datasets(cur, linhas)
            estat_ibge = carregar_ibge(cur, args.malhas)
            estat_areas = carregar_areas(cur)
            cur.execute("ANALYZE")
        conexao.commit()

        with conexao.cursor() as cur:
            contagens = {}
            for tabela in ("datasets", "estados", "municipios", "areas_suprimento", "csw_origem"):
                cur.execute(f"SELECT count(*) FROM {tabela}")
                contagens[tabela] = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM estados WHERE NOT ST_IsValid(geom)")
            invalidos = {"estados": cur.fetchone()[0]}
            cur.execute("SELECT count(*) FROM municipios WHERE NOT ST_IsValid(geom)")
            invalidos["municipios"] = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM areas_suprimento WHERE NOT ST_IsValid(geom)")
            invalidos["areas_suprimento"] = cur.fetchone()[0]
            amostra = [] if args.sem_conferencia else conferir_amostra(cur, brutos)
            sanidade = [] if args.sem_conferencia else buscas_sanidade(cur)

    c = Counter
    relatorio = {
        "rotulo": "análise exploratória feita depois da entrega; não altera nenhum resultado do texto",
        "dsn": args.dsn, "esquema": "db/init_schema_prototipo.sql (sem CREATE EXTENSION) + csw_origem",
        "dump_csw": estat_dump,
        "contagens": contagens,
        "geometrias_invalidas_apos_carga": invalidos,
        "mapeamento": {
            "nome": {"nome_da_folha": sum(x["nome_da_folha"] for x in linhas),
                     "corrigidos_ou_recuperados_de_titulo_fora_do_padrao": sum(x["nome_recuperado"] for x in linhas),
                     "titulo_do_registro": sum(not x["nome_da_folha"] for x in linhas)},
            "mi": {"com_mi": sum(1 for x in linhas if x["mi"]), "sem_mi": sum(1 for x in linhas if not x["mi"]),
                   **grafias_do_mi(linhas)},
            "duplicatas_do_catalogo": duplicatas_do_catalogo(linhas),
            "inom": {"com_inom": sum(1 for x in linhas if x["inom"]),
                     "dos_quais_recuperados_do_titulo": sum(x["inom_recuperado"] for x in linhas),
                     "sem_inom": sum(1 for x in linhas if not x["inom"])},
            "escala_do_titulo_x_nivel_do_inom": {
                "ambos": sum(1 for x in linhas if x["origem_escala"] == "título" and escala_do_inom(x["inom"])),
                "divergem": sum(1 for x in linhas if x["origem_escala"] == "título" and escala_do_inom(x["inom"])
                                and escala_do_inom(x["inom"]) != x["escala"])},
            "escala": dict(c(x["escala"] for x in linhas).most_common()),
            "origem_da_escala": dict(c(x["origem_escala"] or "não reconhecida" for x in linhas).most_common()),
            "tipo_produto": dict(c(x["tipo_produto"] for x in linhas).most_common()),
            "tipo_nao_reconhecido_por_formato": dict(c(x["formato"] or "(sem formato)" for x in linhas
                                                       if not x["tipo_reconhecido"]).most_common()),
            "escala_e_tipo_nao_reconhecidos": sum(1 for x in linhas if x["escala"] == ESCALA_DESCONHECIDA
                                                  and not x["tipo_reconhecido"]),
            "tipos_do_schema_ausentes": [t for t in schema.TIPOS_PRODUTO if t not in {x["tipo_produto"] for x in linhas}],
            "escalas_do_schema_ausentes": [e for e in schema.ESCALAS if e not in {x["escala"] for x in linhas}],
            "projeto": "'' em todos (o CSW não traz projeto)",
            "datas": {"regra": "data_publicacao = data_criacao = dc:date (dct:modified é igual)",
                      "sem_data": sum(1 for x in linhas if x["data"] == DATA_DESCONHECIDA),
                      "minima": min(x["data"] for x in linhas if x["data"] != DATA_DESCONHECIDA).isoformat(),
                      "maxima": max(x["data"] for x in linhas).isoformat(),
                      "fora_de_1900_2026": sorted(x["data"].isoformat() for x in linhas
                                                  if x["data"] != DATA_DESCONHECIDA
                                                  and not 1900 <= x["data"].year <= 2026)},
            "caixa": dict(c(x["situacao_caixa"] for x in linhas).most_common()),
            "cgeo_produtor": dict(c(x["cgeo"] or "(outro produtor)" for x in linhas).most_common()),
        },
        "sentinelas": {"escala": ESCALA_DESCONHECIDA, "tipo_produto": TIPO_DESCONHECIDO,
                       "nome": NOME_DESCONHECIDO, "data": DATA_DESCONHECIDA.isoformat(),
                       "geom": GEOM_SENTINELA},
        "ibge": estat_ibge,
        "areas_suprimento": {"metodo": f"união das caixas válidas dos registros de cada CGEO (os registros sem "
                                       f"caixa válida ficam de fora; o teto de {AREA_MAX_CAIXA} grau² por caixa "
                                       f"não exclui nenhuma), buffer de -{BUFFER_NEGATIVO} grau; aproximação, "
                                       "não a divisão oficial: a área é a região onde o CGEO tem produtos no "
                                       "catálogo, e contagens absolutas com supplyArea não representam a área real",
                             "por_area": estat_areas},
        "conferencia_amostra": {"n": len(amostra), "com_problema": sum(1 for a in amostra if a["problemas"]),
                                "registros": amostra},
        "buscas_sanidade": sanidade,
        "duracao_s": round(time.perf_counter() - t0, 1),
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: relatorio[k] for k in ("dump_csw", "contagens", "duracao_s")}, ensure_ascii=False))
    print(f"relatório: {SAIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
