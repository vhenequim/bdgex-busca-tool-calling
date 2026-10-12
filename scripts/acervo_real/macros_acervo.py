"""Macros LaTeX do teste no acervo real do BDGEx.

Lê results/acervo_real/carga.json e results/acervo_real/resultados.json (gravados por carregar_acervo.py e
avaliar_acervo.py) e grava results/acervo_real/numeros_acervo.tex no formato das outras macros do texto:

    \\expandafter\\def\\csname res@acervo@<config>@<medida>\\endcsname{<valor>}

com vírgula decimal, ponto de milhar e \\% nos percentuais. O texto usa \\res{acervo}{<config>}{<medida>}.

Configs gerais: carga (o acervo carregado), gabarito (as buscas do gabarito), ambig (ambiguidade do acervo),
siglas (sigla no filtro de estado), latencia (SQL no acervo real), geral (tamanho do teste).
Configs por rodada, com os nomes de numeros_lote2.tex para o Gemma 4 E4B (tc1, tc2, tc3d, tc3a, tc3, se1, se2,
se3; tc3 é a versão final e se3 o controle) e com prefixo para os outros modelos (e2btc1, e2btc3, e2bse1,
e2bse3, qwentc1, qwentc3, qwense1, qwense3).

Uso:
    python scripts/acervo_real/macros_acervo.py [--copiar DESTINO ...] [--conferir]

--copiar grava cópias idênticas nos caminhos dados; --conferir lista as macros cujo valor (sem o \\ do \\%)
não aparece literalmente em results/acervo_real/relatorio.md, para conferência à mão.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "results" / "acervo_real"
SAIDA = PASTA / "numeros_acervo.tex"
CONJ = "acervo"

# nome da rodada em resultados.json -> config da macro
CONFIGS = {
    "e4b/tc1": "tc1", "e4b/tc2": "tc2", "e4b/tc3d": "tc3d", "e4b/tc3a": "tc3a", "e4b/tc3": "tc3",
    "e4b/se1": "se1", "e4b/se2": "se2", "e4b/se3": "se3",
    "e2b/tc1": "e2btc1", "e2b/tc3": "e2btc3", "e2b/se1": "e2bse1", "e2b/se3": "e2bse3",
    "qwen/tc1": "qwentc1", "qwen/tc3": "qwentc3", "qwen/se1": "qwense1", "qwen/se3": "qwense3",
}

# rótulos gravados por avaliar_acervo.py
ZERO_PROJETO = "projeto (o CSW não traz projeto)"
ZERO_COMB = "combinação de filtros sem carta em comum"
ZERO_TIPO = "tipo de produto ausente do acervo"
ZERO_ESCALA = "escala ausente do acervo"
ZERO_CRIACAO = "um filtro sozinho já zera: creationPeriod"
ZERO_PUBLICACAO = "um filtro sozinho já zera: publicationPeriod"
ZERO_MUNICIPIO = "município sem polígono na malha do IBGE carregada"
INOF = {
    "zero cartas (o gabarito e a busca zeram)": "inofzero",
    "troca de campo de data (só coincide porque o CSW tem uma data só)": "inofdata",
    "limit ou direção (o conjunto é o mesmo, a página mostrada muda)": "inoflimit",
    "de fato inofensivo": "inofreal",
}
ESCALAS = {"1:50.000": "escala50mil", "1:25.000": "escala25mil", "1:100.000": "escala100mil",
           "1:250.000": "escala250mil", "1:2.000": "escala2mil", "1:10.000": "escala10mil"}
TIPOS = {"SCN Carta Topográfica Matricial": "tipotopomatricial",
         "SCN Carta Topográfica Vetorial": "tipotopovetorial",
         "MDS — RAM": "tipomdsram", "SCN Carta Ortoimagem": "tipoortoimagem"}


def mil(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def pct(a: float, b: float | None = None) -> str:
    v = a if b is None else a / b
    return f"{100 * v:.1f}".replace(".", ",") + r"\%"


def dec(v: float, casas: int = 2) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def ms(v: float) -> str:
    return mil(int(round(v)))


def razao(a: int, b: int) -> str:
    return f"{mil(a)}/{mil(b)}"


def gerar(carga: dict, res: dict) -> list[tuple[str, str, str, str]]:
    """Lista de (config, medida, valor, significado)."""
    M: list[tuple[str, str, str, str]] = []

    def add(cfg: str, medida: str, valor: Any, sig: str) -> None:
        if isinstance(valor, int):
            valor = mil(valor)
        M.append((cfg, medida, str(valor), sig))

    # ---------------------------------------------------------------- carga
    dump = carga["dump_csw"]
    mp = carga["mapeamento"]
    cont = carga["contagens"]
    n = cont["datasets"]
    assert n == dump["identificadores_distintos"] == res["tabelas"]["datasets"]
    c = "carga"
    add(c, "declarados", dump["numberOfRecordsMatched"], "registros declarados pelo catálogo (numberOfRecordsMatched do CSW)")
    add(c, "coletados", dump["registros_no_dump"], "registros coletados com repetição (páginas repetidas pelo servidor)")
    add(c, "distintos", n, "registros distintos coletados e carregados")
    add(c, "copias", dump["copias_descartadas"], "cópias idênticas descartadas na coleta")
    add(c, "copiasdiferentes", dump["copias_com_conteudo_diferente"], "cópias com conteúdo diferente")
    add(c, "estados", cont["estados"], "UFs carregadas (malha do IBGE)")
    add(c, "municipios", cont["municipios"], "municípios carregados (malha do IBGE)")
    add(c, "municipioslista", carga["ibge"]["municipios_na_lista_ibge"], "municípios na lista do IBGE")
    add(c, "municipiossempoligono", len(carga["ibge"]["lista_sem_malha"]), "municípios da lista sem polígono na malha")
    add(c, "areas", cont["areas_suprimento"], "áreas de suprimento aproximadas")
    dup = mp["duplicatas_do_catalogo"]
    add(c, "dupgrupos", dup["grupos"], "grupos de duplicatas do catálogo (mesmo INOM, tipo, escala e data, identificadores distintos)")
    add(c, "dupregistros", dup["registros"], "registros nesses grupos de duplicatas")
    add(c, "dupamais", dup["registros_a_mais"], "registros a mais nas duplicatas (registros menos grupos)")
    for k, med in ESCALAS.items():
        v = mp["escala"][k]
        add(c, med, v, f"registros na escala {k}")
        if v / n >= 0.0005:  # abaixo disso o percentual sairia 0,0%
            add(c, med + "pct", pct(v, n), f"percentual dos registros distintos na escala {k}")
    add(c, "semescala", mp["escala"]["?"], "registros sem escala reconhecida")
    add(c, "semescalapct", pct(mp["escala"]["?"], n), "percentual de registros sem escala reconhecida")
    add(c, "escaladoinom", mp["origem_da_escala"]["nível do INOM"], "registros cuja escala veio do nível do INOM (e não do título)")
    for k, med in TIPOS.items():
        v = mp["tipo_produto"][k]
        add(c, med, v, f"registros do tipo {k}")
        add(c, med + "pct", pct(v, n), f"percentual dos registros distintos do tipo {k}")
    semtipo = mp["tipo_produto"]["(tipo não identificado)"]
    add(c, "semtipo", semtipo, "registros sem tipo de produto reconhecido")
    add(c, "semtipopct", pct(semtipo, n), "percentual de registros sem tipo reconhecido")
    add(c, "semescalaetipo", mp["escala_e_tipo_nao_reconhecidos"], "registros sem escala e sem tipo reconhecidos")
    add(c, "tiposausentes", len(mp["tipos_do_schema_ausentes"]), "tipos de produto do esquema ausentes do acervo coletado")
    add(c, "escalasausentes", len(mp["escalas_do_schema_ausentes"]), "escalas do esquema ausentes do acervo coletado")
    mi = mp["mi"]
    add(c, "commi", mi["com_mi"], "registros com MI")
    add(c, "commipct", pct(mi["com_mi"], n), "percentual de registros com MI")
    add(c, "semmi", mi["sem_mi"], "registros sem MI")
    add(c, "midistintos", mi["codigos_mi_normalizados"], "códigos MI distintos (normalizados)")
    add(c, "miduasgrafias", mi["codigos_com_duas_grafias"], "códigos MI escritos com e sem zero à esquerda")
    ino = mp["inom"]
    add(c, "cominom", ino["com_inom"], "registros com INOM")
    add(c, "cominompct", pct(ino["com_inom"], n), "percentual de registros com INOM")
    add(c, "seminom", ino["sem_inom"], "registros sem INOM")
    add(c, "inomdotitulo", ino["dos_quais_recuperados_do_titulo"], "INOM recuperados do título")
    a = res["ambiguidade"]
    add(c, "inomdistintos", a["inom_distintos"], "INOM distintos no acervo")
    add(c, "inomacento", a["inom_com_nomes_que_so_diferem_por_acento_ou_caixa"], "INOM com nomes que só diferem por acento ou caixa")
    add(c, "semdata", mp["datas"]["sem_data"], "registros sem data")
    cx = mp["caixa"]
    add(c, "caixaok", cx["ok"], "registros com caixa envolvente válida")
    add(c, "semcaixa", n - cx["ok"], "registros cuja caixa envolvente não veio válida do CSW (nula, ausente, fora de faixa ou degenerada)")
    cg = mp["cgeo_produtor"]
    add(c, "outroprodutor", cg["(outro produtor)"], "registros de produtor que não é um CGEO")

    # ---------------------------------------------------------------- tamanho do teste
    g = "geral"
    add(g, "n", res["n_consultas"], "consultas do conjunto de teste")
    add(g, "nbusca", res["n_busca"], "consultas cujo correto é buscar")
    add(g, "ndominio", res["n_D"], "consultas do domínio")
    add(g, "nsub", res["n_E"], "consultas subespecificadas (buscar ou pedir esclarecimento)")
    add(g, "nfora", res["n_F"], "consultas fora do domínio (não buscam)")
    add(g, "rodadas", len(res["configuracoes"]), "rodadas (modelo e versão) avaliadas")
    add(g, "buscasdistintas", res["buscas_distintas_executadas"], "buscas distintas executadas no acervo")
    add(g, "duracaomin", dec(res["duracao_s"] / 60, 1), "duração total da avaliação, em minutos")
    add(g, "datareferencia", res["data_referencia"], "data de referência das datas relativas (AAAA-MM-DD)")

    # ---------------------------------------------------------------- gabarito
    z = a["zeros_preferencial"]
    cl = z["classes"]
    cl237 = z["classes_nas_que_zeram_em_todas_as_leituras"]
    g = "gabarito"
    add(g, "buscasconcretas", res["n_buscas_concretas_gabarito"], "buscas concretas do gabarito (leituras aceitas expandidas)")
    add(g, "errosql", res["erros_sql_gabarito"], "buscas do gabarito com erro de SQL")
    add(g, "zeros", z["n"], "buscas preferenciais do gabarito sem carta")
    add(g, "zerospct", pct(z["n"], res["n_busca"]), "percentual das buscas preferenciais sem carta")
    add(g, "todaszeram", a["todas_leituras_zero"], "consultas em que todas as leituras aceitas zeram")
    add(g, "algumaleituracartas", z["dos_quais_alguma_leitura_tem_cartas"], "buscas preferenciais sem carta em que alguma leitura alternativa tem cartas")
    add(g, "leiturascomesem", a["alguma_leitura_zero_outra_nao"], "consultas com leituras com e sem cartas")
    any_cfg = res["configuracoes"]["e4b/tc3"]["contagens"]
    add(g, "comcartas", any_cfg["n_gab_nao_vazio"], "consultas cujo gabarito tem ao menos uma carta")
    add(g, "zeroprojeto", cl[ZERO_PROJETO], "buscas sem carta porque o CSW não traz projeto")
    add(g, "zerocombinacao", cl[ZERO_COMB], "buscas sem carta por combinação de filtros sem carta em comum")
    add(g, "zerotipo", cl[ZERO_TIPO], "buscas sem carta por tipo de produto ausente do acervo")
    add(g, "zeroescala", cl[ZERO_ESCALA], "buscas sem carta por escala ausente do acervo")
    add(g, "zerotipoescala", cl[ZERO_TIPO] + cl[ZERO_ESCALA], "buscas sem carta por tipo ou escala ausente do acervo")
    add(g, "zerofiltrodata", cl[ZERO_CRIACAO] + cl[ZERO_PUBLICACAO], "buscas sem carta em que o filtro de data sozinho já zera")
    add(g, "zeromunicipio", cl[ZERO_MUNICIPIO], "buscas sem carta por município sem polígono na malha")
    outros = z["n"] - cl[ZERO_PROJETO] - cl[ZERO_COMB] - cl[ZERO_TIPO] - cl[ZERO_ESCALA]
    add(g, "zerooutros", outros, "buscas sem carta por outros motivos (filtro de data sozinho ou município sem polígono)")
    add(g, "todasprojeto", cl237[ZERO_PROJETO], "das que zeram em todas as leituras, por projeto")
    add(g, "todascombinacao", cl237[ZERO_COMB], "das que zeram em todas as leituras, por combinação de filtros")
    add(g, "consultasprojeto", a["consultas_com_project"], "consultas com projeto")
    add(g, "consultasarea", a["consultas_com_supplyArea"], "consultas com área de suprimento em alguma leitura")
    dist = a["distribuicao_preferencial"]
    for k, med in [("0", "dist0"), ("1", "dist1"), ("2 a 10", "dist2a10"), ("11 a 100", "dist11a100"),
                   ("101 a 1.000", "dist101a1000"), ("mais de 1.000", "distmaisde1000")]:
        add(g, med, dist[k], f"buscas preferenciais que devolvem {k} cartas")
    add(g, "medianacartas", int(a["total_preferencial"]["mediana"]), "mediana de cartas por busca preferencial")

    # ---------------------------------------------------------------- ambiguidade
    g = "ambig"
    add(g, "buscas", res["n_busca"], "buscas preferenciais (total para o corte da primeira página)")
    add(g, "paginacorta", a["mais_de_10"], "buscas cuja primeira página corta o resultado")
    add(g, "paginacortapct", pct(a["mais_de_10"], res["n_busca"]), "percentual das buscas cuja primeira página corta o resultado")
    add(g, "paginaempate", a["pagina_ambigua_por_empate"], "buscas em que o empate de data cruza a fronteira da página")
    h = a["homonimas"]
    add(g, "nomepedidos", h["n_consultas_por_nome"], "pedidos por nome de folha")
    add(g, "nomehomonimas", h["consultas_com_2_ou_mais_folhas_homonimas"], "pedidos por nome com 2 ou mais INOM/MI com o mesmo nome")
    add(g, "nomelugares", h["lugares_distintos"], "pedidos por nome com folhas homônimas em lugares distintos")
    add(g, "nomelugarespct", pct(h["lugares_distintos"], h["n_consultas_por_nome"]), "percentual dos pedidos por nome com folhas homônimas em lugares distintos")
    add(g, "nomemesmaescala", h["lugares_distintos_com_dois_inom_na_mesma_escala"], "desses, com dois INOM homônimos na mesma escala")
    add(g, "nomemaxlugares", h["max_lugares_distintos"], "máximo de lugares distintos com o mesmo nome")
    add(g, "nomesubdivisoes", h["so_folha_e_subdivisoes"], "pedidos por nome em que só a folha e suas subdivisões têm o nome")
    add(g, "nomeregistros", h["consultas_com_2_ou_mais_registros_nome_exato"], "pedidos por nome com 2 ou mais registros com o nome exato")
    add(g, "nomekeywordmais", h["busca_so_keyword_com_mais_folhas_que_o_nome_exato"], "pedidos em que a busca só por palavra-chave traz mais folhas que o nome exato")
    m = a["municipios"]
    add(g, "municipiopedidos", m["n_consultas_com_city"], "pedidos por município")
    add(g, "municipiomaisdeum", m["casam_mais_de_um_municipio"], "pedidos por município que casam mais de um município")
    add(g, "municipiomaisdeumpct", pct(m["casam_mais_de_um_municipio"], m["n_consultas_com_city"]), "percentual dos pedidos por município que casam mais de um")
    add(g, "municipiooutrauf", m["casam_municipios_de_mais_de_uma_uf"], "pedidos por município que casam municípios de mais de uma UF")
    add(g, "municipiocomestado", m["das_ambiguas_com_estado_no_pedido"], "dos ambíguos, com o estado também no pedido")
    add(g, "municipiomax", m["max_municipios"], "máximo de municípios casados por um pedido do teste")
    add(g, "santamaria", m["exemplos"]["Santa Maria"]["municipios"], "municípios casados por 'Santa Maria'")
    e = a["edicoes"]
    add(g, "codigopedidos", e["n_consultas_por_codigo"], "pedidos por código (MI ou INOM)")
    add(g, "codigoinom", e["por_tipo"]["INOM"], "pedidos por INOM")
    add(g, "codigomi", e["por_tipo"]["MI"], "pedidos por MI")
    add(g, "codigovarios", e["consultas_com_2_ou_mais_registros_do_codigo"], "pedidos por código com 2 ou mais registros")
    add(g, "codigovariospct", pct(e["consultas_com_2_ou_mais_registros_do_codigo"], e["n_consultas_por_codigo"]), "percentual dos pedidos por código com 2 ou mais registros")
    add(g, "codigomax", e["max_registros_por_codigo"], "máximo de registros por código pedido")
    add(g, "codigoprodutos", e["com_mais_de_um_produto"], "pedidos por código com mais de um tipo de produto")
    add(g, "codigodatas", e["com_mais_de_uma_data"], "pedidos por código com mais de uma data")
    add(g, "codigoescalas", e["com_mais_de_uma_escala"], "pedidos por código com mais de uma escala")
    add(g, "codigoduplicatas", e["com_registros_duplicados"], "pedidos por código com registros duplicados no catálogo")
    add(g, "codigosoduplicatas", e["so_duplicatas"], "pedidos por código em que só há a duplicata")
    add(g, "codigokeywordoutros", e["busca_so_keyword_traz_outros_registros"], "pedidos em que a busca só pelo código traz outros registros")
    pm = e["pagina_mostra_o_mais_recente"]
    add(g, "maisrecentesim", pm["True"], "pedidos por código em que a primeira página mostra a edição mais recente")
    add(g, "maisrecentenao", pm["False"], "pedidos por código em que a primeira página não mostra a mais recente")
    add(g, "maisrecentesemregistro", pm["None"], "pedidos por código em que o gabarito não devolve registro do código")
    add(g, "migrafiaalternativa", e["mi_com_registros_na_grafia_alternativa"], "pedidos por MI com registros na outra grafia")

    # ---------------------------------------------------------------- siglas
    s = a["siglas_simulacao"]
    r = a["siglas_execucoes_reais"]
    g = "siglas"
    add(g, "n", s["n"], "siglas simuladas no filtro de estado")
    add(g, "funcionam", s["resultado_igual_ao_do_nome"], "siglas que devolvem o mesmo que o nome da UF")
    add(g, "nenhum", s["nao_casam_nenhuma"], "siglas que não casam estado nenhum")
    add(g, "errado", s["casam_outra_e_nao_a_propria"], "siglas que casam o estado errado e não a própria UF")
    add(g, "propriaeoutras", s["casam_a_propria_e_outras"], "siglas que casam a própria UF e outras")
    ps = s["por_sigla"]
    lista = lambda f: ", ".join(sorted(x["sigla"] for x in ps if f(x)))  # noqa: E731
    add(g, "listafuncionam", lista(lambda x: x["igual"]), "siglas que funcionam")
    add(g, "listanenhum", lista(lambda x: not x["estados_que_casam"]), "siglas que não casam estado nenhum")
    add(g, "listaerrado", lista(lambda x: x["estados_que_casam"] and not x["inclui_a_propria_uf"]), "siglas que casam o estado errado")
    add(g, "execucoes", r["execucoes"], "execuções das rodadas com sigla no filtro de estado")
    add(g, "execucoestc2", r["execucoes_e4b/tc2"], "dessas, na segunda versão com tool calling (Gemma 4 E4B)")
    add(g, "execucoesse2", r["execucoes_e4b/se2"], "dessas, na segunda versão com saída estruturada (Gemma 4 E4B)")
    add(g, "mudam", r["resultado_muda"], "execuções com sigla cujo resultado muda em relação ao nome da UF")
    add(g, "perdetudo", r["perde_tudo"], "execuções com sigla que perdem todas as cartas certas")
    add(g, "amais", r["a_mais_total"], "cartas a mais, somadas, nas execuções com sigla")
    add(g, "amenos", r["a_menos_total"], "cartas a menos, somadas, nas execuções com sigla")

    # ---------------------------------------------------------------- por rodada
    for k, cfg in CONFIGS.items():
        cr = res["configuracoes"][k]
        ct = cr["contagens"]
        nb, nt, ngv = cr["n_busca"], cr["n_total"], ct["n_gab_nao_vazio"]
        rot = cr["rotulo"]
        ap = round(cr["acuracia_param_lote"] * nt)
        ar = round(cr["acuracia_resultado_lote"] * nt)
        buscou = ct.get("buscou", 0) + ct.get("erro_sql", 0)
        certos = ct.get("cruz_certo_igual", 0) + ct.get("cruz_certo_diferente", 0)
        erros = ct.get("cruz_errado_igual", 0) + ct.get("cruz_errado_diferente", 0)
        add(cfg, "accparam", pct(cr["acuracia_param_lote"]), f"{rot}: acerto por parâmetros no conjunto de teste ({nt})")
        add(cfg, "accparamn", razao(ap, nt), f"{rot}: acertos por parâmetros / consultas")
        add(cfg, "accresult", pct(cr["acuracia_resultado_lote"]), f"{rot}: acerto por resultado no conjunto de teste ({nt})")
        add(cfg, "accresultn", razao(ar, nt), f"{rot}: acertos por resultado / consultas")
        add(cfg, "accresultbusca", pct(ct.get("acerto_resultado", 0), nb), f"{rot}: acerto por resultado nas {nb} consultas que buscam")
        add(cfg, "accparamcartas", pct(ct.get("acerto_param_gab_nao_vazio", 0), ngv), f"{rot}: acerto por parâmetros nas consultas cujo gabarito tem cartas")
        add(cfg, "accparamcartasn", razao(ct.get("acerto_param_gab_nao_vazio", 0), ngv), f"{rot}: idem, acertos / n")
        add(cfg, "accresultcartas", pct(ct.get("acerto_resultado_gab_nao_vazio", 0), ngv), f"{rot}: acerto por resultado nas consultas cujo gabarito tem cartas")
        add(cfg, "accresultcartasn", razao(ct.get("acerto_resultado_gab_nao_vazio", 0), ngv), f"{rot}: idem, acertos / n")
        add(cfg, "ncartas", ngv, f"{rot}: n das consultas cujo gabarito tem cartas")
        add(cfg, "buscou", buscou, f"{rot}: execuções que buscaram")
        add(cfg, "certos", certos, f"{rot}: buscas com parâmetros certos")
        add(cfg, "certoigual", ct.get("cruz_certo_igual", 0), f"{rot}: buscas com parâmetros certos que devolvem as mesmas cartas")
        add(cfg, "certodiferente", ct.get("cruz_certo_diferente", 0), f"{rot}: buscas com parâmetros certos e cartas diferentes")
        add(cfg, "erros", erros, f"{rot}: buscas com parâmetros errados")
        add(cfg, "erradoigual", ct.get("cruz_errado_igual", 0), f"{rot}: buscas com parâmetros errados que devolvem as mesmas cartas")
        add(cfg, "erradoigualzero", ct.get("inofensivo_com_resultado_vazio", 0), f"{rot}: dessas, com zero cartas nos dois lados")
        add(cfg, "erradodiferente", ct.get("cruz_errado_diferente", 0), f"{rot}: buscas com parâmetros errados e cartas diferentes")
        add(cfg, "errosql", ct.get("erro_sql", 0), f"{rot}: buscas com erro de SQL")
        add(cfg, "naobuscoudominio", ct.get("nao_buscou_D", 0), f"{rot}: consultas do domínio em que não buscou")
        add(cfg, "naobuscousub", ct.get("nao_buscou_E", 0), f"{rot}: consultas subespecificadas em que não buscou")
        add(cfg, "paginaigual", pct(ct.get("pagina_igual", 0), ct.get("buscou", 0)), f"{rot}: primeira página igual, entre as que buscaram")
        add(cfg, "revocacao", dec(cr["revocacao_media"]), f"{rot}: revocação média")
        add(cfg, "precisao", dec(cr["precisao_media"]), f"{rot}: precisão média")
        inof = {INOF[t]: v["n"] for t, v in cr.get("erro_inofensivo_por_tipo", {}).items()}
        for med in INOF.values():
            add(cfg, med, inof.get(med, 0), f"{rot}: erros com o mesmo resultado, classe {med}")

    # ---------------------------------------------------------------- latência
    lt = res["latencia"]
    rod = lt["por_rodada"]
    g = "latencia"
    add(g, "n", lt["todas"]["n"], "buscas medidas (3 rodadas da leitura preferencial)")
    add(g, "rodadas", len(rod), "rodadas da medida")
    add(g, "mediana", ms(lt["todas"]["mediana"]), "mediana da latência da SQL, em ms")
    add(g, "p95", ms(lt["todas"]["p95"]), "p95 da latência da SQL, em ms")
    add(g, "max", ms(lt["todas"]["max"]), "máximo da latência da SQL, em ms")
    add(g, "espacialmediana", ms(lt["com_filtro_espacial"]["mediana"]), "mediana com filtro espacial (município, estado ou área), em ms")
    add(g, "espacialp95", ms(lt["com_filtro_espacial"]["p95"]), "p95 com filtro espacial, em ms")
    add(g, "espacialn", lt["com_filtro_espacial"]["n"], "buscas medidas com filtro espacial")
    add(g, "semespacialmediana", ms(lt["sem_filtro_espacial"]["mediana"]), "mediana sem filtro espacial, em ms")
    add(g, "semespacialp95", ms(lt["sem_filtro_espacial"]["p95"]), "p95 sem filtro espacial, em ms")
    add(g, "semespacialn", lt["sem_filtro_espacial"]["n"], "buscas medidas sem filtro espacial")
    add(g, "medianamin", ms(min(x["mediana"] for x in rod)), "menor mediana entre as rodadas, em ms")
    add(g, "medianamax", ms(max(x["mediana"] for x in rod)), "maior mediana entre as rodadas, em ms")
    add(g, "p95min", ms(min(x["p95"] for x in rod)), "menor p95 entre as rodadas, em ms")
    add(g, "p95max", ms(max(x["p95"] for x in rod)), "maior p95 entre as rodadas, em ms")
    add(g, "erros", lt["erros"], "buscas com erro na medida")

    chaves = [(c, m_) for c, m_, _, _ in M]
    assert len(chaves) == len(set(chaves)), "macro duplicada"
    return M


def escrever(M: list[tuple[str, str, str, str]]) -> str:
    L = ["% AUTO-GERADO por scripts/acervo_real/macros_acervo.py a partir de results/acervo_real/ — não editar à mão",
         r"\providecommand{\res}[3]{\ifcsname res@#1@#2@#3\endcsname\csname res@#1@#2@#3\endcsname\else\textbf{??}\fi}"]
    for cfg, med, val, _ in sorted(M, key=lambda x: (x[0], x[1])):
        L.append(rf"\expandafter\def\csname res@{CONJ}@{cfg}@{med}\endcsname{{{val}}}")
    return "\n".join(L) + "\n"


def conferir(M: list[tuple[str, str, str, str]]) -> None:
    rel = (PASTA / "relatorio.md").read_text(encoding="utf-8")
    faltam = [(c, m_, v) for c, m_, v, _ in M if v.replace(r"\%", "%") not in rel]
    print(f"conferência: {len(M) - len(faltam)} de {len(M)} valores aparecem literalmente no relatorio.md")
    for c, m_, v in faltam:
        print(f"  não aparece: {c}@{m_} = {v}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--copiar", nargs="*", default=[], help="caminhos para cópias idênticas do .tex")
    ap.add_argument("--conferir", action="store_true", help="lista valores que não aparecem no relatorio.md")
    ap.add_argument("--listar", action="store_true", help="imprime config, medida, valor e significado (TSV)")
    a = ap.parse_args()
    carga = json.loads((PASTA / "carga.json").read_text(encoding="utf-8"))
    res = json.loads((PASTA / "resultados.json").read_text(encoding="utf-8"))
    M = gerar(carga, res)
    txt = escrever(M)
    SAIDA.write_text(txt, encoding="utf-8", newline="\n")
    print(f"{SAIDA}: {len(M)} macros")
    for d in a.copiar:
        Path(d).write_text(txt, encoding="utf-8", newline="\n")
        print(f"copiado para {d}")
    if a.listar:
        sys.stdout.reconfigure(encoding="utf-8")
        for c, m_, v, s in M:
            print(f"{c}\t{m_}\t{v}\t{s}")
    if a.conferir:
        sys.stdout.reconfigure(encoding="utf-8")
        conferir(M)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
