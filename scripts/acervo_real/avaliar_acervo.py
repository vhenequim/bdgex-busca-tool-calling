"""Executa no acervo real do BDGEx as buscas do lote 2 (gabarito e cada configuração) e mede o resultado.

Análise EXPLORATÓRIA, feita depois da entrega do texto, para responder à pergunta da banca "por que não
testaram a busca com o acervo real?". Não roda modelo nenhum e não altera nenhum resultado do texto: os
parâmetros vêm do gabarito do lote 2 e dos registros das rodadas já feitas (`results/lote2/`), e a SQL é a
de `pfc_busca.tools.montar_sql`, sem mudança. O banco é o carregado por `carregar_acervo.py`.

    python scripts/acervo_real/avaliar_acervo.py [--dsn postgresql://pfc@localhost:5433/acervo_real]
    python scripts/acervo_real/avaliar_acervo.py --so-relatorio     # refaz os .md a partir do resultados.json

Método
------
Para cada consulta do lote 2 cujo correto é buscar (espera_tool_call; 717 do domínio e 65 subespecificadas
da categoria E, em que pedir esclarecimento também é aceito):

1. Gabarito. As leituras aceitas são as da pontuação existente: `lote._leituras` (preferencial + alternativas,
   já com as datas relativas resolvidas para a data da execução por `gabarito.resolver_leituras`, via
   `lote.carregar_pasta` -> `repontuar`), e cada leitura é expandida em buscas concretas por `lote._concretas`
   (todas as combinações de `$um_de`; `$opcional` presente ou ausente). Cada busca concreta é executada.
2. Configuração. Os parâmetros que ela emitiu: `predito` do registro da execução, a mesma busca que a
   pontuação por parâmetros avalia (a última busca aceita). Sem `predito`: "não buscou".
3. Cada busca guarda o conjunto completo de ids (a cláusula WHERE de `montar_sql`, sem LIMIT, conferida com a
   contagem) e a primeira página (a ordem e o LIMIT de `montar_sql`; 10 por padrão, ou o `limit` pedido).
4. Medidas por configuração:
   - resultado igual: o conjunto devolvido é igual ao de alguma busca concreta aceita;
   - primeira página igual: as cartas da primeira página são as mesmas de alguma busca aceita. Como muitas
     cartas têm a mesma data (a ordenação da SQL é só pela data), a página não é única quando há empate na
     fronteira; contamos a página como igual quando existe uma ordem compatível com a SQL em que as duas
     páginas coincidem (e também, à parte, a igualdade da página como o PostgreSQL a devolveu);
   - revocação e precisão em relação à busca aceita mais próxima (maior Jaccard);
   - tabela cruzada com a pontuação existente (`metrics.avaliar_linha`): parâmetro certo x resultado igual.
   - acerto por resultado: busca com resultado igual, ou (só na categoria E) não buscar. No lote inteiro,
     somam-se as 163 consultas fora do domínio com a pontuação existente (nelas não há busca).
5. Ambiguidade do acervo nas buscas do gabarito (leitura preferencial, com os opcionais presentes):
   distribuição do número de resultados, zeros (classificados), cortes da primeira página, folhas homônimas,
   várias edições por código, o código MI escrito com e sem zero à esquerda e as siglas no filtro de estado
   (execuções reais e simulação das 27 siglas).
6. Latência: `tools.buscar_catalogo` (contagem + primeira página, com conexão nova a cada busca, como no
   sistema) para a busca preferencial de cada consulta.

O lote 2 é o conjunto de teste: nada aqui grava o texto de uma consulta nem os parâmetros por consulta.
Saídas: results/acervo_real/resultados.json, relatorio.md e resumo_slide.md.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import psycopg

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

from pfc_busca import ferramentas, tools  # noqa: E402
from pfc_busca.evaluation import gabarito, lote, lote2, metrics  # noqa: E402

DSN_PADRAO = "postgresql://pfc@localhost:5433/acervo_real"
DATASET = RAIZ / "data" / "lote_validacao_2.json"
DIR_LOTE2 = RAIZ / "results" / "lote2"
SAIDA = RAIZ / "results" / "acervo_real"
ARQ_CARGA = SAIDA / "carga.json"

# (chave, rótulo, pasta). Gemma 4 E4B: as oito configurações do lote 2; extensão: E2B e Qwen com v1 e v3.
MODELOS = (("e4b", "Gemma 4 E4B", "gemma4-e4b-it-qat", ("tc1", "tc2", "tc3d", "tc3a", "tc3", "se1", "se2", "se3")),
           ("e2b", "Gemma 4 E2B", "gemma4-e2b-it-qat", ("tc1", "tc3", "se1", "se3")),
           ("qwen", "Qwen 3 4B", "qwen3-4b-instruct-2507-q4_K_M", ("tc1", "tc3", "se1", "se3")))
PREFIXO = {"tc1": "", "se1": "se-", "tc2": "tc2-", "se2": "se2-", "tc3d": "tc3d-", "tc3a": "tc3a-",
           "tc3": "tc3-", "se3": "se3-"}
assert all(PREFIXO[k] == lote2.CONFIGS[k][0] for k in PREFIXO)

_PREFIXO_CONTAGEM = "SELECT COUNT(*)::integer AS total FROM datasets"
_RE_ORDEM = re.compile(r"ORDER BY (data_publicacao|data_criacao) (ASC|DESC) LIMIT (\d+)$")
_RE_MI = re.compile(tools._REGEX_MI)
_RE_INOM = re.compile(tools._REGEX_INOM)


# ---------------------------------------------------------------------------
# Execução das buscas (com cache por SQL + argumentos)
# ---------------------------------------------------------------------------

class Executor:
    def __init__(self, dsn: str):
        self.con = psycopg.connect(dsn, autocommit=True)
        with self.con.cursor() as cur:
            cur.execute("SET statement_timeout = '120s'")
        self.cache: dict[tuple, dict] = {}

    def busca(self, params: dict) -> dict:
        """{total, ids: {id: (pub, cri)}, pagina: [ids], ordem: (coluna, direcao, limite), erro}."""
        try:
            sql_contagem, sql_principal, args = tools.montar_sql(params)
        except Exception as e:  # noqa: BLE001 — parâmetros que nem montam a SQL
            return {"erro": f"montar_sql: {type(e).__name__}", "total": None, "ids": {}, "pagina": [], "ordem": None}
        chave = (sql_principal, repr(args))
        if chave in self.cache:
            return self.cache[chave]
        assert sql_contagem.startswith(_PREFIXO_CONTAGEM)
        where = sql_contagem[len(_PREFIXO_CONTAGEM):]
        cauda = sql_principal.split("FROM datasets", 1)[1]
        m = _RE_ORDEM.search(sql_principal.strip())
        assert m, sql_principal[-120:]
        ordem = (m.group(1), m.group(2), int(m.group(3)))
        r: dict[str, Any] = {"erro": None, "ordem": ordem}
        try:
            with self.con.cursor() as cur:
                cur.execute(sql_contagem, args)
                r["total"] = cur.fetchone()[0]
                cur.execute("SELECT id::text, data_publicacao, data_criacao FROM datasets" + where, args)
                r["ids"] = {i: (p, c) for i, p, c in cur.fetchall()}
                cur.execute("SELECT id::text FROM datasets" + cauda, args)
                r["pagina"] = [x[0] for x in cur.fetchall()]
            assert r["total"] == len(r["ids"]), "contagem diferente do conjunto"
        except psycopg.Error as e:
            r.update(erro=f"{type(e).__name__}: {str(e).strip().splitlines()[0][:120]}", total=None, ids={}, pagina=[])
        self.cache[chave] = r
        return r

    def escalar(self, sql: str, args: list | tuple = ()) -> Any:
        with self.con.cursor() as cur:
            cur.execute(sql, args)
            return cur.fetchall()


def pagina_tolerante(r: dict) -> tuple:
    """(G, b, T, k): G = ids certamente na página (data estritamente melhor que a da fronteira), b = data da
    fronteira, T = ids empatados na fronteira, k = quantos de T entram. Sem corte: (todos, None, ∅, 0)."""
    coluna, direcao, limite = r["ordem"]
    pos = 0 if coluna == "data_publicacao" else 1
    ids = r["ids"]
    if len(ids) <= limite:
        return frozenset(ids), None, frozenset(), 0
    datas = sorted((v[pos] for v in ids.values()), reverse=(direcao == "DESC"))
    b = datas[limite - 1]
    melhor = (lambda d: d > b) if direcao == "DESC" else (lambda d: d < b)
    G = frozenset(i for i, v in ids.items() if melhor(v[pos]))
    T = frozenset(i for i, v in ids.items() if v[pos] == b)
    return G, b, T, limite - len(G)


def paginas_compativeis(a: dict, b: dict) -> bool:
    Ga, ba, Ta, ka = pagina_tolerante(a)
    Gb, bb, Tb, kb = pagina_tolerante(b)
    if Ga != Gb or ka != kb:
        return False
    return ka == 0 or (ba == bb and len(Ta & Tb) >= ka)


def pagina_ambigua(r: dict) -> bool:
    G, b, T, k = pagina_tolerante(r)
    return k > 0 and len(T) > k


# ---------------------------------------------------------------------------
# Carregamento
# ---------------------------------------------------------------------------

def carregar_configs() -> tuple[dict[str, dict], list[str]]:
    """'<modelo>/<config>' -> {"rotulo", "linhas": {id: linha}}."""
    out, avisos = {}, []
    for chave_m, rot_m, pasta_m, cfgs in MODELOS:
        for k in cfgs:
            p = DIR_LOTE2 / (PREFIXO[k] + pasta_m)
            r = lote.carregar_pasta(p, DATASET)
            if r is None:
                avisos.append(f"{chave_m}/{k}: sem rodada em {p}")
                continue
            linhas, _casos = r
            unicas = lote._uma_por_id(linhas)
            out[f"{chave_m}/{k}"] = {"rotulo": f"{rot_m} {lote2.CONFIGS[k][2]}", "modelo": rot_m,
                                    "config": lote2.CONFIGS[k][2], "linhas": unicas}
    return out, avisos


def ultima_busca_tc(linha: dict) -> Any:
    """Argumentos da última chamada a buscar_catalogo registrada (só para conferir `predito`)."""
    tcs = [t for t in (linha.get("tool_calls") or []) if isinstance(t, dict) and t.get("name") == "buscar_catalogo"]
    return tcs[-1].get("args") if tcs else None


def busca_recusada(linha: dict) -> bool:
    """A última chamada a buscar_catalogo do traço foi recusada pelo validador ("BUSCA NÃO EXECUTADA")."""
    traco = (linha.get("extras") or {}).get("traco") or []
    buscas = [t for t in traco if isinstance(t, dict) and t.get("ferramenta") == "buscar_catalogo"]
    return bool(buscas) and str(buscas[-1].get("resultado", "")).startswith("BUSCA NÃO EXECUTADA")


def sem_acento_nem_caixa(t: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", t) if not unicodedata.combining(ch)).casefold()


_CAMPOS_DATA = {"publicationPeriod", "creationPeriod", "sortField"}


def _assinatura_data(p: dict) -> tuple:
    return (frozenset(k for k in ("publicationPeriod", "creationPeriod") if p.get(k)),
            "creationDate" if p.get("sortField") == "creationDate" else "publicationDate")


def tipo_inofensivo(pred: dict, concretas: list[dict], campos: set[str], vazio: bool) -> str:
    """Por que um parâmetro errado devolve o mesmo conjunto de cartas."""
    if vazio:
        return "zero cartas (o gabarito e a busca zeram)"
    if campos & _CAMPOS_DATA and all(_assinatura_data(c) != _assinatura_data(pred) for c in concretas):
        return "troca de campo de data (só coincide porque o CSW tem uma data só)"
    if campos and campos <= {"limit", "sortDirection"}:
        return "limit ou direção (o conjunto é o mesmo, a página mostrada muda)"
    return "de fato inofensivo"


def preferencial(leitura: dict) -> dict:
    """Leitura preferencial concreta: cada campo no valor preferencial, com os opcionais presentes."""
    return {c: gabarito.valor_preferencial(v) for c, v in leitura.items()}


def eh_codigo(kw: Any) -> str | None:
    if not isinstance(kw, str):
        return None
    if _RE_MI.match(kw):
        return "MI"
    if _RE_INOM.match(kw):
        return "INOM"
    return None


def quantis(v: list[float]) -> dict[str, float | None]:
    if not v:
        return {"n": 0, "mediana": None, "p95": None, "max": None}
    s = sorted(v)
    return {"n": len(s), "mediana": round(statistics.median(s), 1),
            "p95": round(s[min(len(s) - 1, int(round(0.95 * (len(s) - 1))))], 1), "max": round(s[-1], 1)}


def faixa(n: int | None) -> str:
    if n is None:
        return "erro"
    for lim, rot in ((0, "0"), (1, "1"), (10, "2 a 10"), (100, "11 a 100"), (1000, "101 a 1.000")):
        if n <= lim:
            return rot
    return "mais de 1.000"


FAIXAS = ["0", "1", "2 a 10", "11 a 100", "101 a 1.000", "mais de 1.000", "erro"]


# ---------------------------------------------------------------------------
# Avaliação
# ---------------------------------------------------------------------------

def avaliar(dsn: str) -> dict[str, Any]:
    t0 = time.perf_counter()
    cfgs, avisos = carregar_configs()
    ex = Executor(dsn)
    tabelas = {t: ex.escalar(f"SELECT count(*) FROM {t}")[0][0]
               for t in ("datasets", "estados", "municipios", "areas_suprimento")}

    # --- gabarito: as mesmas leituras em todas as configurações (mesmo dataset e mesma data)
    base = next(iter(cfgs.values()))["linhas"]
    for nome_c, c in cfgs.items():
        for i, x in c["linhas"].items():
            if lote._leituras(x) != lote._leituras(base[i]) or x["hoje"] != base[i]["hoje"]:
                avisos.append(f"{nome_c}: gabarito resolvido de {i} difere do de referência")
    ids_busca = sorted(i for i, x in base.items() if x["espera_tool_call"])
    ids_f = sorted(i for i, x in base.items() if not x["espera_tool_call"])
    grupo = {i: ("E" if base[i].get("aceita_nao_chamar") else "D") for i in ids_busca}

    gab: dict[str, dict] = {}
    n_concretas = 0
    for i in ids_busca:
        x = base[i]
        concretas = []
        for le in lote._leituras(x):
            for c in lote._concretas(le):
                if c not in concretas:
                    concretas.append(c)
        n_concretas += len(concretas)
        res = [ex.busca(c) for c in concretas]
        pref = preferencial(x["esperado_resolvido"])
        gab[i] = {"concretas": concretas, "res": res, "pref": pref, "res_pref": ex.busca(pref)}
    erros_gab = sum(1 for g in gab.values() for r in g["res"] + [g["res_pref"]] if r["erro"])
    print(f"gabarito: {len(ids_busca)} consultas, {n_concretas} buscas concretas, erros {erros_gab}, "
          f"{time.perf_counter() - t0:.0f}s", flush=True)

    # --- configurações
    por_config: dict[str, dict] = {}
    detalhe: dict[str, dict] = {}
    for nome_c, c in cfgs.items():
        linhas = c["linhas"]
        cont = Counter()
        rec, prec, rec_dif, prec_dif = [], [], [], []
        divergencia_predito = 0
        campos_inofensivo, campos_muda = Counter(), Counter()
        tipos_inof: dict[str, list[str]] = {}
        certo_dif: dict[str, list[str]] = {}
        det = {}
        for i in ids_busca:
            x = linhas.get(i)
            if x is None:
                cont["ausente"] += 1
                continue
            g = gab[i]
            aval = metrics.avaliar_linha(x)
            certo = aval.correto
            campos_erro = "+".join(sorted(aval.fp | aval.fn | aval.fora_do_schema)) or "(nenhum)"
            pred = x["predito"]
            if nome_c.split("/")[1].startswith("tc") and pred is not None:
                ult = ultima_busca_tc(x)
                if ult is not None and ult != pred:
                    divergencia_predito += 1
            gr = grupo[i]
            gab_vazio = all(r["total"] == 0 for r in g["res"])
            if pred == {} and busca_recusada(x):
                # a pontuação registrou `{}` para uma chamada que o validador recusou; o sistema não buscou
                cont["predito_vazio_busca_recusada"] += 1
                pred = None
            if pred is None:
                st = "nao_buscou"
                cont[f"nao_buscou_{gr}"] += 1
                acerto_res = gr == "E"
                det[i] = [st, int(certo), None, None, None, None]
            else:
                r = ex.busca(pred)
                if r["erro"]:
                    st = "erro_sql"
                    cont["erro_sql"] += 1
                    cont[f"cruz_{'certo' if certo else 'errado'}_erro"] += 1
                    acerto_res = False
                    det[i] = [st, int(certo), 0, 0, None, None]
                else:
                    st = "buscou"
                    S = set(r["ids"])
                    iguais = [set(a["ids"]) == S for a in g["res"]]
                    igual = any(iguais)
                    pag = any(paginas_compativeis(r, a) for a in g["res"])
                    pag_exec = any(set(r["pagina"]) == set(a["pagina"]) for a in g["res"])
                    # busca aceita mais próxima (maior Jaccard; ambos vazios = 1)
                    melhor, mj = None, -1.0
                    for a in g["res"]:
                        A = set(a["ids"])
                        j = 1.0 if not A and not S else len(A & S) / len(A | S)
                        if j > mj:
                            melhor, mj = A, j
                    rc = len(melhor & S) / len(melhor) if melhor else None
                    pc = len(melhor & S) / len(S) if S else None
                    if rc is not None:
                        rec.append(rc)
                        if not igual:
                            rec_dif.append(rc)
                    if pc is not None:
                        prec.append(pc)
                        if not igual:
                            prec_dif.append(pc)
                    cont["buscou"] += 1
                    cont["igual"] += igual
                    cont["igual_nao_vazio"] += igual and not gab_vazio
                    cont["pagina_igual"] += pag
                    cont["pagina_igual_executada"] += pag_exec
                    cont["pagina_igual_resultado_diferente"] += pag and not igual
                    cont[f"cruz_{'certo' if certo else 'errado'}_{'igual' if igual else 'diferente'}"] += 1
                    if not certo and igual:
                        cont["inofensivo_com_resultado_vazio"] += len(S) == 0
                        campos_inofensivo[campos_erro] += 1
                        ti = tipo_inofensivo(pred, g["concretas"], aval.fp | aval.fn | aval.fora_do_schema, not S)
                        tipos_inof.setdefault(ti, []).append(i)
                    if not certo and not igual:
                        campos_muda[campos_erro] += 1
                    if certo and not igual:
                        cont["certo_diferente"] += 1
                        kw = pred.get("keyword")
                        aceitas = {v for le in lote._leituras(x) for v in gabarito.valores_aceitos(le.get("keyword"))
                                   if isinstance(v, str)}
                        if not isinstance(kw, str) or kw in aceitas:
                            motivo = "outro"
                        elif sem_acento_nem_caixa(kw) in {sem_acento_nem_caixa(v) for v in aceitas}:
                            motivo = "keyword difere só por acento ou caixa"
                            cont["certo_diferente_keyword_acento_ou_caixa"] += 1
                            cont["certo_diferente_keyword_maiuscula_acentuada"] += any(
                                ch.isupper() and ord(ch) > 127 for ch in kw)
                        else:
                            motivo = "keyword difere por pontuação ou caractere"
                            cont["certo_diferente_keyword_pontuacao"] += 1
                        certo_dif.setdefault(motivo, []).append(i)
                    acerto_res = igual
                    det[i] = [st, int(certo), int(igual), int(pag), None if rc is None else round(rc, 4),
                              None if pc is None else round(pc, 4)]
            cont["acerto_param"] += certo
            cont["acerto_resultado"] += acerto_res
            cont[f"acerto_param_{gr}"] += certo
            cont[f"acerto_resultado_{gr}"] += acerto_res
            if not gab_vazio:
                cont["n_gab_nao_vazio"] += 1
                cont["acerto_resultado_gab_nao_vazio"] += acerto_res
                cont["acerto_param_gab_nao_vazio"] += certo
        f_certas = sum(metrics.avaliar_linha(linhas[i]).correto for i in ids_f if i in linhas)
        n_total = sum(1 for i in ids_busca + ids_f if i in linhas)
        por_config[nome_c] = {
            "rotulo": c["rotulo"], "modelo": c["modelo"], "config": c["config"],
            "n_busca": len(ids_busca), "n_D": sum(1 for g in grupo.values() if g == "D"),
            "n_E": sum(1 for g in grupo.values() if g == "E"), "contagens": dict(cont),
            "revocacao_media": round(statistics.fmean(rec), 4) if rec else None,
            "precisao_media": round(statistics.fmean(prec), 4) if prec else None,
            "revocacao_media_quando_diferente": round(statistics.fmean(rec_dif), 4) if rec_dif else None,
            "precisao_media_quando_diferente": round(statistics.fmean(prec_dif), 4) if prec_dif else None,
            "n_revocacao": len(rec), "n_precisao": len(prec),
            "f_certas": f_certas, "n_f": len(ids_f), "n_total": n_total,
            "acuracia_param_lote": (cont["acerto_param"] + f_certas) / n_total,
            "acuracia_resultado_lote": (cont["acerto_resultado"] + f_certas) / n_total,
            "predito_difere_da_ultima_chamada_registrada": divergencia_predito,
            "campos_do_erro_inofensivo": dict(campos_inofensivo.most_common()),
            "campos_do_erro_que_muda_o_resultado": dict(campos_muda.most_common()),
            "erro_inofensivo_por_tipo": {k: {"n": len(v), "ids": v} for k, v in
                                         sorted(tipos_inof.items(), key=lambda kv: -len(kv[1]))},
            "certo_e_diferente_por_motivo": {k: {"n": len(v), "ids": v} for k, v in certo_dif.items()},
        }
        detalhe[nome_c] = det
        print(f"{nome_c}: param {por_config[nome_c]['acuracia_param_lote']:.3f} resultado "
              f"{por_config[nome_c]['acuracia_resultado_lote']:.3f} ({time.perf_counter() - t0:.0f}s)", flush=True)

    amb = ambiguidade(ex, gab, ids_busca, base, cfgs)
    lat = latencias(dsn, gab, ids_busca)
    carga = json.loads(ARQ_CARGA.read_text(encoding="utf-8")) if ARQ_CARGA.exists() else {}
    return {
        "rotulo": "análise exploratória feita depois da entrega, sem rodar modelos; não altera nenhum resultado do texto",
        "dsn": dsn, "tabelas": tabelas, "dataset": DATASET.relative_to(RAIZ).as_posix(),
        "data_referencia": base[ids_busca[0]]["hoje"],
        "n_consultas": len(base), "n_busca": len(ids_busca), "n_D": por_config[next(iter(por_config))]["n_D"],
        "n_E": por_config[next(iter(por_config))]["n_E"], "n_F": len(ids_f),
        "n_buscas_concretas_gabarito": n_concretas, "erros_sql_gabarito": erros_gab,
        "buscas_distintas_executadas": len(ex.cache),
        "configuracoes": por_config, "ambiguidade": amb, "latencia": lat, "avisos": avisos,
        "carga": {k: carga.get(k) for k in ("dump_csw", "contagens", "mapeamento", "areas_suprimento", "ibge")},
        "detalhe_por_consulta": {
            "colunas": ["situacao", "param_certo", "resultado_igual", "pagina_igual", "revocacao", "precisao"],
            "configuracoes": detalhe},
        "gabarito_por_consulta": {i: {"grupo": grupo[i], "n_buscas": len(gab[i]["concretas"]),
                                      "totais": [r["total"] for r in gab[i]["res"]],
                                      "total_preferencial": gab[i]["res_pref"]["total"]} for i in ids_busca},
        "duracao_s": round(time.perf_counter() - t0, 1),
    }


# ---------------------------------------------------------------------------
# Ambiguidade do acervo real
# ---------------------------------------------------------------------------

def dist(v: list[int]) -> dict[str, int]:
    """Distribuição em faixas fixas: 0, 1, 2, 3, 4 a 5, 6 a 10, mais de 10."""
    faixas = ((0, "0"), (1, "1"), (2, "2"), (3, "3"), (5, "4 a 5"), (10, "6 a 10"))
    d = {rot: 0 for _, rot in faixas} | {"mais de 10": 0}
    for x in v:
        d[next((rot for lim, rot in faixas if x <= lim), "mais de 10")] += 1
    return d


CAMPOS_FILTRO = ("keyword", "scale", "productType", "project", "publicationPeriod", "creationPeriod", "city",
                 "state", "supplyArea")


def culpados_zero(ex: Executor, p: dict) -> str:
    """Campos cuja retirada, um de cada vez, já devolve alguma carta (para os zeros por combinação)."""
    filtros = [c for c in CAMPOS_FILTRO if p.get(c)]
    cs = [c for c in filtros if ex.busca({k: v for k, v in p.items() if k != c})["total"]]
    return "+".join(cs) if cs else "nenhum campo sozinho (mais de um filtro sem carta em comum)"


def classificar_zero(ex: Executor, p: dict) -> str:
    if p.get("project"):
        return "projeto (o CSW não traz projeto)"
    if p.get("productType") and ex.busca({"productType": p["productType"]})["total"] == 0:
        return "tipo de produto ausente do acervo"
    if p.get("scale") and ex.busca({"scale": p["scale"]})["total"] == 0:
        return "escala ausente do acervo"
    if p.get("city") and not municipios_que_casam(ex, p["city"]):
        return "município sem polígono na malha do IBGE carregada"
    filtros = [c for c in CAMPOS_FILTRO if p.get(c)]
    sozinhos = [c for c in filtros if ex.busca({c: p[c]})["total"] == 0]
    if sozinhos:
        return "um filtro sozinho já zera: " + "+".join(sozinhos)
    return "combinação de filtros sem carta em comum"


def municipios_que_casam(ex: Executor, valor: str) -> list[tuple[str, str]]:
    """Municípios que o filtro `city` de `montar_sql` casa (mesma condição: ILIKE '%valor%' sem acento)."""
    return [tuple(r) for r in ex.escalar(
        "SELECT nome, sigla_estado FROM municipios WHERE unaccent(lower(nome)) ILIKE unaccent(lower(%s)) "
        "ORDER BY nome, sigla_estado", (f"%{valor}%",))]


def familias_inom(inoms: set[str]) -> list[str]:
    """INOM que não estão contidos em outro do conjunto (a folha-mãe absorve as subdivisões com o mesmo nome)."""
    return sorted(c for c in inoms if not any(c != o and c.startswith(o + "-") for o in inoms))


def ambiguidade(ex: Executor, gab: dict, ids_busca: list[str], base: dict, cfgs: dict) -> dict[str, Any]:
    out: dict[str, Any] = {}
    totais = {i: gab[i]["res_pref"]["total"] for i in ids_busca}
    out["distribuicao_preferencial"] = {f: sum(1 for t in totais.values() if faixa(t) == f) for f in FAIXAS}
    vals = [t for t in totais.values() if t is not None]
    out["total_preferencial"] = {"mediana": statistics.median(vals), "max": max(vals),
                                 "media": round(statistics.fmean(vals), 1)}
    out["mais_de_10"] = sum(1 for i in ids_busca if (totais[i] or 0) > gab[i]["res_pref"]["ordem"][2])
    out["mais_de_10_literal"] = sum(1 for t in vals if t > 10)
    out["pagina_ambigua_por_empate"] = sum(1 for i in ids_busca if pagina_ambigua(gab[i]["res_pref"]))
    out["todas_leituras_zero"] = sum(1 for i in ids_busca if all(r["total"] == 0 for r in gab[i]["res"]))
    out["alguma_leitura_zero_outra_nao"] = sum(1 for i in ids_busca if any(r["total"] == 0 for r in gab[i]["res"])
                                               and any(r["total"] for r in gab[i]["res"]))
    zeros = [i for i in ids_busca if totais[i] == 0]
    classe_de = {i: classificar_zero(ex, gab[i]["pref"]) for i in zeros}
    classes = Counter(classe_de.values())
    todas_zero = {i for i in ids_busca if all(r["total"] == 0 for r in gab[i]["res"])}
    out["zeros_preferencial"] = {
        "n": len(zeros), "classes": dict(classes.most_common()),
        "dos_quais_todas_as_leituras_zeram": sum(1 for i in zeros if i in todas_zero),
        "dos_quais_alguma_leitura_tem_cartas": sum(1 for i in zeros if i not in todas_zero),
        "classes_nas_que_zeram_em_todas_as_leituras": dict(Counter(classe_de[i] for i in zeros
                                                                   if i in todas_zero).most_common()),
        "nota": "classificação das buscas preferenciais que zeram (o primeiro critério que se aplica); "
                "todas_leituras_zero conta as consultas em que todas as leituras aceitas zeram"}
    out["zeros_combinacao_culpados"] = dict(Counter(
        culpados_zero(ex, gab[i]["pref"]) for i in zeros
        if classificar_zero(ex, gab[i]["pref"]) == "combinação de filtros sem carta em comum").most_common())
    out["zeros_por_campo_presente"] = dict(Counter(c for i in zeros for c in CAMPOS_FILTRO if gab[i]["pref"].get(c))
                                           .most_common())
    out["zeros_ids"] = zeros

    # municípios: o filtro city casa substrings e homônimos de outras UFs
    cid = []
    for i in ids_busca:
        leituras_city = [c for c in gab[i]["concretas"] if isinstance(c.get("city"), str) and c["city"]]
        if leituras_city:
            casas = [municipios_que_casam(ex, c["city"]) for c in leituras_city]
            pior = max(casas, key=len)
            cid.append({"id": i, "municipios": len(pior), "ufs": len({u for _, u in pior}),
                        "com_estado_no_pedido": any(c.get("state") for c in leituras_city)})
    exemplos_cidade = {}
    for v in ("Baliza", "Arujá", "Passagem", "Colorado", "Santa Maria"):
        casa = municipios_que_casam(ex, v)
        exemplos_cidade[v] = {"municipios": len(casa), "lista": [f"{n}/{u}" for n, u in casa][:8]}
    out["municipios"] = {
        "n_consultas_com_city": len(cid),
        "nota": "consultas com city em alguma leitura aceita; conta o valor de city que casa mais municípios",
        "casam_mais_de_um_municipio": sum(1 for c in cid if c["municipios"] > 1),
        "casam_municipios_de_mais_de_uma_uf": sum(1 for c in cid if c["ufs"] > 1),
        "das_ambiguas_com_estado_no_pedido": sum(1 for c in cid if c["municipios"] > 1 and c["com_estado_no_pedido"]),
        "nenhum_municipio": sum(1 for c in cid if c["municipios"] == 0),
        "max_municipios": max((c["municipios"] for c in cid), default=0),
        "distribuicao": dist([c["municipios"] for c in cid]),
        "exemplos": exemplos_cidade,
        "por_consulta": cid,
    }

    # folhas homônimas e várias edições (keyword da leitura preferencial)
    nomes, codigos = [], []
    for i in ids_busca:
        kw = gab[i]["pref"].get("keyword")
        if isinstance(kw, str) and kw:
            (codigos if eh_codigo(kw) else nomes).append((i, kw))
    homo = []
    for i, kw in nomes:
        exatos = ex.escalar(
            "SELECT count(*), count(DISTINCT coalesce(inom, mi, id::text)), count(DISTINCT escala), "
            "count(DISTINCT tipo_produto) FROM datasets WHERE unaccent(lower(nome)) = unaccent(lower(%s))", (kw,))[0]
        folhas = ex.escalar("SELECT DISTINCT inom, mi, escala FROM datasets "
                            "WHERE unaccent(lower(nome)) = unaccent(lower(%s))", (kw,))
        inoms = {f[0] for f in folhas if f[0]}
        familias = familias_inom(inoms) + sorted({f[1] or "?" for f in folhas if not f[0]})
        por_escala = Counter(e for inom, e in {(f[0], f[2]) for f in folhas if f[0]})
        r_kw = ex.busca({"keyword": kw})
        folhas_kw = ex.escalar("SELECT count(DISTINCT coalesce(inom, mi, id::text)) FROM datasets WHERE id = ANY(%s::uuid[])",
                               (list(r_kw["ids"]),))[0][0]
        homo.append({"id": i, "registros_nome_exato": exatos[0], "folhas_nome_exato": exatos[1],
                     "familias": len(familias), "inom_das_familias": familias if len(familias) > 1 else [],
                     "dois_inom_na_mesma_escala": any(n > 1 for n in por_escala.values()),
                     "escalas_nome_exato": exatos[2], "tipos_nome_exato": exatos[3],
                     "registros_busca_keyword": r_kw["total"], "folhas_busca_keyword": folhas_kw,
                     "total_busca_gabarito": gab[i]["res_pref"]["total"]})
    out["homonimas"] = {
        "n_consultas_por_nome": len(homo),
        "folhas_distintas_com_o_nome_exato": dist([h["folhas_nome_exato"] for h in homo]),
        "consultas_com_2_ou_mais_folhas_homonimas": sum(1 for h in homo if h["folhas_nome_exato"] >= 2),
        "max_folhas_homonimas": max((h["folhas_nome_exato"] for h in homo), default=0),
        "consultas_com_2_ou_mais_registros_nome_exato": sum(1 for h in homo if h["registros_nome_exato"] >= 2),
        "folhas_distintas_na_busca_so_keyword": dist([h["folhas_busca_keyword"] for h in homo]),
        "mediana_registros_busca_so_keyword": statistics.median([h["registros_busca_keyword"] for h in homo]) if homo else None,
        "mediana_folhas_busca_so_keyword": statistics.median([h["folhas_busca_keyword"] for h in homo]) if homo else None,
        "busca_so_keyword_com_mais_folhas_que_o_nome_exato": sum(1 for h in homo
                                                                 if h["folhas_busca_keyword"] > h["folhas_nome_exato"]),
        "consultas_nome_exato_ausente": sum(1 for h in homo if h["registros_nome_exato"] == 0),
        "lugares_distintos": sum(1 for h in homo if h["familias"] >= 2),
        "lugares_distintos_com_dois_inom_na_mesma_escala": sum(1 for h in homo if h["familias"] >= 2
                                                              and h["dois_inom_na_mesma_escala"]),
        "so_folha_e_subdivisoes": sum(1 for h in homo if h["folhas_nome_exato"] >= 2 and h["familias"] < 2),
        "max_lugares_distintos": max((h["familias"] for h in homo), default=0),
        "exemplo_lugares_distintos": (ex_h := max((h["inom_das_familias"] for h in homo), key=len, default=[])),
        "exemplo_nome": ex.escalar(
            "SELECT min(nome) FROM datasets WHERE inom = ANY(%s) GROUP BY unaccent(lower(nome)) "
            "HAVING count(DISTINCT inom) = %s ORDER BY count(*) DESC LIMIT 1", (ex_h, len(ex_h)))[0][0] if ex_h else None,
        "nota": "lugares distintos = INOM com o mesmo nome em que um não contém o outro; a folha-mãe e suas "
                "subdivisões com o mesmo nome contam como um lugar só",
        "por_consulta": homo,
    }

    edic = []
    for i, kw in codigos:
        tipo = eh_codigo(kw)
        col = "mi" if tipo == "MI" else "inom"
        linhas_ex = ex.escalar(f"SELECT id::text, escala, tipo_produto, data_publicacao FROM datasets WHERE {col} = %s", (kw,))
        chaves = Counter((lin[1], lin[2], lin[3]) for lin in linhas_ex)
        r_kw = ex.busca({"keyword": kw})
        rg = gab[i]["res_pref"]
        exatos_no_res = {lin[0]: lin[3] for lin in linhas_ex if lin[0] in rg["ids"]}
        mostra_recente = None
        if exatos_no_res:
            dmax = max(exatos_no_res.values())
            mostra_recente = any(j in rg["pagina"] and d == dmax for j, d in exatos_no_res.items())
        variante = None
        if tipo == "MI":
            num, _, resto = kw.partition("-")
            alt = (num.lstrip("0") or "0") if num.startswith("0") else num.zfill(4)
            if alt != num:
                alt_kw = alt + ("-" + resto if resto else "")
                variante = ex.escalar("SELECT count(*) FROM datasets WHERE mi = %s", (alt_kw,))[0][0]
        edic.append({"id": i, "tipo": tipo, "registros_codigo_exato": len(linhas_ex),
                     "escalas": len({lin[1] for lin in linhas_ex}), "produtos": len({lin[2] for lin in linhas_ex}),
                     "datas": len({lin[3] for lin in linhas_ex}), "registros_busca_keyword": r_kw["total"],
                     "registros_repetidos": sum(n - 1 for n in chaves.values()),
                     "so_repeticao": len(linhas_ex) >= 2 and len(chaves) == 1,
                     "registros_busca_gabarito": rg["total"], "exatos_no_resultado": len(exatos_no_res),
                     "pagina_mostra_o_mais_recente": mostra_recente,
                     "ordem_gabarito": rg["ordem"][1],
                     "registros_na_grafia_alternativa_do_mi": variante})
    out["edicoes"] = {
        "n_consultas_por_codigo": len(edic), "por_tipo": dict(Counter(e["tipo"] for e in edic)),
        "registros_por_codigo": dist([e["registros_codigo_exato"] for e in edic]),
        "consultas_com_2_ou_mais_registros_do_codigo": sum(1 for e in edic if e["registros_codigo_exato"] >= 2),
        "max_registros_por_codigo": max((e["registros_codigo_exato"] for e in edic), default=0),
        "com_mais_de_uma_escala": sum(1 for e in edic if e["escalas"] > 1),
        "com_mais_de_um_produto": sum(1 for e in edic if e["produtos"] > 1),
        "com_mais_de_uma_data": sum(1 for e in edic if e["datas"] > 1),
        "com_registros_duplicados": sum(1 for e in edic if e["registros_repetidos"]),
        "so_duplicatas": sum(1 for e in edic if e["so_repeticao"]),
        "com_produtos_ou_edicoes_distintos": sum(1 for e in edic if e["registros_codigo_exato"] >= 2
                                                 and not e["so_repeticao"]),
        "busca_so_keyword_traz_outros_registros": sum(1 for e in edic
                                                      if e["registros_busca_keyword"] > e["registros_codigo_exato"]),
        "mediana_registros_busca_so_keyword": statistics.median([e["registros_busca_keyword"] for e in edic]) if edic else None,
        "pagina_mostra_o_mais_recente": dict(Counter(str(e["pagina_mostra_o_mais_recente"]) for e in edic)),
        "nao_mostra_por_ordem_ascendente": sum(1 for e in edic if e["pagina_mostra_o_mais_recente"] is False
                                               and e["ordem_gabarito"] == "ASC"),
        "mi_com_registros_na_grafia_alternativa": sum(1 for e in edic if e["registros_na_grafia_alternativa_do_mi"]),
        "mi_consultas": sum(1 for e in edic if e["tipo"] == "MI"),
        "por_consulta": edic,
    }

    # siglas no filtro de estado
    estados = [n for (n,) in ex.escalar("SELECT nome FROM estados ORDER BY nome")]
    sim = []
    for sigla, nome_uf in sorted(ferramentas.UFS.items()):
        casam = [n for (n,) in ex.escalar(
            "SELECT nome FROM estados WHERE unaccent(lower(nome)) ILIKE unaccent(lower(%s)) ORDER BY nome", (f"%{sigla}%",))]
        r_s, r_n = ex.busca({"state": sigla}), ex.busca({"state": nome_uf})
        S, N = set(r_s["ids"]), set(r_n["ids"])
        sim.append({"sigla": sigla, "uf": nome_uf, "estados_que_casam": casam, "inclui_a_propria_uf": nome_uf in casam,
                    "registros_sigla": len(S), "registros_nome": len(N), "a_mais": len(S - N), "a_menos": len(N - S),
                    "igual": S == N})
    out["siglas_simulacao"] = {
        "n": len(sim), "casam_so_a_propria_uf": sum(1 for s in sim if s["estados_que_casam"] == [s["uf"]]),
        "nao_casam_nenhuma": sum(1 for s in sim if not s["estados_que_casam"]),
        "casam_outra_e_nao_a_propria": sum(1 for s in sim if s["estados_que_casam"] and not s["inclui_a_propria_uf"]),
        "casam_a_propria_e_outras": sum(1 for s in sim if s["inclui_a_propria_uf"] and len(s["estados_que_casam"]) > 1),
        "resultado_igual_ao_do_nome": sum(1 for s in sim if s["igual"]),
        "por_sigla": sim, "n_estados": len(estados),
    }
    reais = Counter()
    exemplos_siglas = Counter()
    for nome_c, c in cfgs.items():
        for i in ids_busca:
            x = c["linhas"].get(i)
            p = x and x["predito"]
            st = p.get("state") if isinstance(p, dict) else None
            if isinstance(st, str) and st.strip().upper() in ferramentas.UFS and len(st.strip()) == 2:
                sig = st.strip().upper()
                q = dict(p, state=ferramentas.UFS[sig])
                S, N = set(ex.busca(p)["ids"]), set(ex.busca(q)["ids"])
                reais["execucoes"] += 1
                reais[f"execucoes_{nome_c}"] += 1
                reais["resultado_muda"] += S != N
                reais["a_mais_total"] += len(S - N)
                reais["a_menos_total"] += len(N - S)
                reais["perde_tudo"] += bool(N) and not (S & N)
                exemplos_siglas[sig] += 1
    out["siglas_execucoes_reais"] = {**dict(reais), "siglas_usadas": dict(exemplos_siglas.most_common())}

    # supplyArea (aproximada) e project nas buscas do gabarito
    out["consultas_com_supplyArea"] = sum(1 for i in ids_busca if any("supplyArea" in c for c in gab[i]["concretas"]))
    out["consultas_com_project"] = sum(1 for i in ids_busca if any("project" in c for c in gab[i]["concretas"]))

    # grafias: o mesmo INOM escrito com e sem acento (ou em outra caixa) no próprio catálogo
    out["inom_com_nomes_que_so_diferem_por_acento_ou_caixa"] = ex.escalar(
        "SELECT count(*) FROM (SELECT inom FROM datasets WHERE inom IS NOT NULL GROUP BY inom "
        "HAVING count(DISTINCT nome) > 1 AND count(DISTINCT unaccent(lower(nome))) = 1) t")[0][0]
    out["inom_distintos"] = ex.escalar("SELECT count(DISTINCT inom) FROM datasets")[0][0]
    collate, ctype = ex.escalar("SELECT datcollate, datctype FROM pg_database WHERE datname = current_database()")[0]
    out["locale_do_banco"] = {"collate": collate, "ctype": ctype}
    return out


RODADAS_LATENCIA = 3


def latencias(dsn: str, gab: dict, ids_busca: list[str]) -> dict[str, Any]:
    """`tools.buscar_catalogo` (conexão nova, contagem + primeira página) na busca preferencial de cada consulta,
    em RODADAS_LATENCIA rodadas; a máquina é de uso geral, então a medida varia entre rodadas."""
    vals, espaciais, sem_espacial, erros, rodadas = [], [], [], 0, []
    for _ in range(RODADAS_LATENCIA):
        v_rodada = []
        for i in ids_busca:
            p = gab[i]["pref"]
            r = tools.buscar_catalogo(p, dsn)
            if not r.executado:
                erros += 1
                continue
            v_rodada.append(r.latencia_ms)
            (espaciais if any(p.get(c) for c in ("city", "state", "supplyArea")) else sem_espacial).append(r.latencia_ms)
        vals += v_rodada
        rodadas.append(quantis(v_rodada))
    return {"metodo": f"tools.buscar_catalogo na leitura preferencial (conexão nova a cada busca, contagem + "
                      f"primeira página), {RODADAS_LATENCIA} rodadas seguidas depois de todas as buscas já terem "
                      "rodado uma vez (cache aquecido), num notebook de uso geral; os quantis juntam as rodadas",
            "todas": quantis(vals), "com_filtro_espacial": quantis(espaciais), "sem_filtro_espacial": quantis(sem_espacial),
            "por_rodada": rodadas, "erros": erros,
            "banco_sintetico": "não há medida comparável: nas rodadas do lote 2 a busca não foi executada "
                               "(latencia_tool_ms vazio em todos os registros)"}


# ---------------------------------------------------------------------------
# Relatórios
# ---------------------------------------------------------------------------

def pct(a: float, b: float | None = None) -> str:
    v = a if b is None else (a / b if b else float("nan"))
    return f"{100 * v:.1f}%".replace(".", ",")


def mil(n: Any) -> str:
    return f"{n:,}".replace(",", ".") if isinstance(n, int) else str(n)


def num(v: float | None, casas: int = 2) -> str:
    return "—" if v is None else f"{v:.{casas}f}".replace(".", ",")


# Conferência manual (feita uma vez, à mão, antes de escrever o relatório; os ids são do lote 2 e o texto das
# consultas não é gravado). Para cada consulta: a leitura do gabarito e os parâmetros do TC v3 (Gemma 4 E4B), a
# SQL montada por `montar_sql`, a contagem refeita com SQL escrita à mão (sem `montar_sql`) e a classificação.
CONFERENCIA_MANUAL = {
    "configuracao": "e4b/tc3",
    "ids": ["BVC0135", "BVA0013", "BVS0070", "BVA0044", "BVC0079", "BVC0171", "BVA0004", "BVA0018", "BVC0153",
            "BVS0068", "BVT0070", "BVC0116", "BVC0069", "BVE0012", "BVE0071"],
    "achados": [
        "parâmetros, SQL e argumentos conferem com o registro da execução e com o gabarito resolvido em todas as 15",
        "as contagens foram refeitas com SQL escrita à mão (filtro pela sigla da UF ou da área, igualdade de nome, "
        "de escala e de tipo) em 11 das 15 e deram o mesmo número em todas; as outras 4 são as 3 com project, que "
        "zeram por construção, e a subespecificada sem busca",
        "a classificação 'resultado igual' está certa nas 15: 6 iguais com parâmetro certo (4 delas com zero "
        "cartas: projeto, tipo MDT ausente do acervo, nome + tipo sem registro, nome + tipo + escala + área sem "
        "registro), 3 iguais com parâmetro errado (data inicial 1900 acrescentada; UF omitida numa busca com "
        "projeto; keyword a mais numa busca com projeto, as duas com zero cartas), 5 diferentes (keyword encurtada "
        "que casa outras folhas; keyword sem acento; nome encurtado que acha outra folha; busca vazia que devolve "
        "o acervo inteiro; keyword genérica numa subespecificada) e 1 'não buscou' numa subespecificada",
        "dois achados do acervo real apareceram na amostra: a mesma folha está escrita 'Vila Propício' num "
        "registro e 'Vila Propicio' no outro, e a busca por palavra-chave é sensível a acento, então a keyword "
        "sem acento devolve o outro registro; e uma folha pedida 'do 1º CGEO', que no acervo é do 2º CGEO, dá zero no "
        "gabarito, enquanto o modelo, que encurtou o nome, achou outra folha de nome parecido",
    ],
}


def _cfgs_ordem(res: dict) -> list[str]:
    return list(res["configuracoes"])


def tabela_configs(res: dict) -> list[str]:
    L = ["| Configuração | Acerto por parâmetros (945) | Acerto por resultado (945) | Acerto por resultado (782 que "
         "buscam) | Idem, só gabarito com cartas (545) | Primeira página igual | Revocação média | Precisão média |",
         "|---|---|---|---|---|---|---|---|"]
    for k in _cfgs_ordem(res):
        c = res["configuracoes"][k]
        n = c["contagens"]
        ngv = n["n_gab_nao_vazio"]
        L.append(f"| {c['rotulo']} | {pct(c['acuracia_param_lote'])} | {pct(c['acuracia_resultado_lote'])} | "
                 f"{pct(n.get('acerto_resultado', 0), c['n_busca'])} | "
                 f"{pct(n.get('acerto_resultado_gab_nao_vazio', 0), ngv)} (param. {pct(n.get('acerto_param_gab_nao_vazio', 0), ngv)}) | "
                 f"{pct(n.get('pagina_igual', 0), n.get('buscou', 0))} das que buscaram | "
                 f"{num(c['revocacao_media'])} | {num(c['precisao_media'])} |")
    return L


def tabela_cruzada(res: dict) -> list[str]:
    L = ["| Configuração | Buscou | Certo e igual | Certo e diferente | Errado e igual (com zero cartas) | "
         "Errado e diferente | Erro de SQL | Não buscou (D / E) |", "|---|---|---|---|---|---|---|---|"]
    for k in _cfgs_ordem(res):
        c = res["configuracoes"][k]
        n = c["contagens"]
        L.append(f"| {c['rotulo']} | {n.get('buscou', 0) + n.get('erro_sql', 0)} | {n.get('cruz_certo_igual', 0)} | "
                 f"{n.get('cruz_certo_diferente', 0)} | {n.get('cruz_errado_igual', 0)} "
                 f"({n.get('inofensivo_com_resultado_vazio', 0)}) | {n.get('cruz_errado_diferente', 0)} | "
                 f"{n.get('erro_sql', 0)} | {n.get('nao_buscou_D', 0)} / {n.get('nao_buscou_E', 0)} |")
    return L


ZERO_PROJETO = "projeto (o CSW não traz projeto)"
ZERO_TIPO = "tipo de produto ausente do acervo"
ZERO_ESCALA = "escala ausente do acervo"
ZERO_COMB = "combinação de filtros sem carta em comum"
INOF_ZERO = "zero cartas (o gabarito e a busca zeram)"
INOF_DATA = "troca de campo de data (só coincide porque o CSW tem uma data só)"
INOF_LIMIT = "limit ou direção (o conjunto é o mesmo, a página mostrada muda)"
INOF_REAL = "de fato inofensivo"


def derivados(res: dict) -> dict[str, Any]:
    """Números compostos usados no relatório e no resumo (todos saem de resultados.json)."""
    cfg = res["configuracoes"]
    a = res["ambiguidade"]
    z = a["zeros_preferencial"]
    cl = z["classes"]
    n3 = cfg["e4b/tc3"]["contagens"]
    inof3 = {k: v["n"] for k, v in cfg["e4b/tc3"].get("erro_inofensivo_por_tipo", {}).items()}
    lat = res["latencia"]
    rod = lat.get("por_rodada") or [lat["todas"]]
    carga = res.get("carga") or {}
    mapa = carga.get("mapeamento") or {}
    d = {
        "zeros_projeto": cl.get(ZERO_PROJETO, 0),
        "zeros_tipo_escala": cl.get(ZERO_TIPO, 0) + cl.get(ZERO_ESCALA, 0),
        "zeros_combinacao": cl.get(ZERO_COMB, 0),
        "certos3": n3.get("cruz_certo_igual", 0) + n3.get("cruz_certo_diferente", 0),
        "erros3": n3.get("cruz_errado_igual", 0) + n3.get("cruz_errado_diferente", 0),
        "inof3": inof3,
        "lat_med": (min(r["mediana"] for r in rod), max(r["mediana"] for r in rod)),
        "lat_p95": (min(r["p95"] for r in rod), max(r["p95"] for r in rod)),
        "n_rodadas": len(rod),
        "mi": mapa.get("mi") or {},
        "duplicatas": mapa.get("duplicatas_do_catalogo") or {},
        "recusadas": {k: c["contagens"].get("predito_vazio_busca_recusada", 0) for k, c in cfg.items()
                      if c["contagens"].get("predito_vazio_busca_recusada")},
        "v1_primeira_chamada": sum(c.get("predito_difere_da_ultima_chamada_registrada", 0)
                                   for k, c in cfg.items() if k.endswith("/tc1")),
    }
    d["zeros_outros"] = z["n"] - d["zeros_projeto"] - d["zeros_tipo_escala"] - d["zeros_combinacao"]
    return d


def _faixa_ms(par: tuple) -> str:
    a, b = (round(x) for x in par)
    return f"{a} ms" if a == b else f"{a} a {b} ms"


def relatorio(res: dict) -> str:
    cfg = res["configuracoes"]
    a = res["ambiguidade"]
    lat = res["latencia"]
    carga = res.get("carga") or {}
    dump = carga.get("dump_csw") or {}
    mapa = carga.get("mapeamento") or {}
    t3 = cfg["e4b/tc3"]
    n3 = t3["contagens"]
    s3 = cfg["e4b/se3"]
    ss = a["siglas_simulacao"]
    sr = a["siglas_execucoes_reais"]
    ho = a["homonimas"]
    ed = a["edicoes"]
    mu = a["municipios"]
    z = a["zeros_preferencial"]
    d = derivados(res)
    L: list[str] = []
    w = L.append
    w("# Busca no acervo real do BDGEx: o lote 2 executado nos metadados do CSW")
    w("")
    w(f"**Rótulo:** {res['rotulo']}. Gerado por `scripts/acervo_real/avaliar_acervo.py` a partir de "
      "`results/acervo_real/resultados.json`; todos os números saem do script.")
    w("")
    w("## Por que esta análise")
    w("")
    w("A avaliação do texto mede se a frase vira os parâmetros certos. A busca em si só tinha sido demonstrada "
      "no banco sintético (14 municípios, 117 produtos), o que esconde a ambiguidade do acervo real: folhas "
      "homônimas, sigla que casa com mais de um estado, várias edições da mesma folha. Aqui as buscas que o "
      "sistema faria no lote 2 (o gabarito e o que cada configuração emitiu) rodam no acervo real carregado num "
      "PostGIS com o esquema do protótipo, com a SQL de `tools.montar_sql` sem mudança. Nenhum modelo foi rodado.")
    w("")
    w("## Método")
    w("")
    w(f"- **Banco:** {mil(res['tabelas']['datasets'])} registros do CSW do BDGEx em `datasets`, "
      f"{res['tabelas']['estados']} UFs e {mil(res['tabelas']['municipios'])} municípios das malhas do IBGE, "
      f"{res['tabelas']['areas_suprimento']} áreas de suprimento aproximadas (detalhes da carga em `carga.json`).")
    w(f"- **Consultas:** as {res['n_busca']} do lote 2 cujo correto é buscar ({res['n_D']} do domínio e "
      f"{res['n_E']} subespecificadas, em que pedir esclarecimento também vale). As {res['n_F']} fora do domínio "
      "não buscam e entram no acerto do lote inteiro com a pontuação existente.")
    w(f"- **Gabarito:** cada leitura aceita (a preferencial e as alternativas, com as datas relativas resolvidas "
      f"para {res['data_referencia']}, como na pontuação) é expandida em buscas concretas (`$um_de`: cada valor; "
      f"`$opcional`: com e sem o campo), {mil(res['n_buscas_concretas_gabarito'])} ao todo, "
      f"{res['erros_sql_gabarito']} com erro.")
    rec = ", ".join(f"{cfg[k]['rotulo']} {v}" for k, v in d["recusadas"].items()) or "nenhuma"
    w("- **Configurações:** as 16 rodadas do lote 2 (Gemma 4 E4B com TC v1, v2, v3d, v3a, v3 e SE v1, v2, v3; "
      "Gemma 4 E2B e Qwen 3 4B com TC e SE v1 e v3). A busca de cada execução é o `predito` do registro, a mesma "
      "que a pontuação por parâmetros avalia, e não necessariamente a última chamada registrada: no TC v1, quando "
      "a resposta trouxe duas chamadas, vale a primeira, como na pontuação "
      f"({d['v1_primeira_chamada']} execuções nas três rodadas TC v1). Quando o `predito` é `{{}}` e o traço mostra "
      "que o validador recusou a chamada (\"BUSCA NÃO EXECUTADA\"), a execução conta como \"não buscou\", "
      f"porque o sistema não buscou ({rec}); o acerto não muda, porque `{{}}` já contava como erro.")
    w("- **Resultado igual:** o conjunto completo de cartas devolvido (sem LIMIT) é igual ao de alguma busca "
      "concreta aceita. **Acerto por resultado:** resultado igual, ou não buscar numa subespecificada.")
    w("- **Primeira página igual:** as cartas da primeira página (LIMIT de `montar_sql`, 10 por padrão) são as "
      "mesmas de alguma busca aceita. A SQL ordena só pela data, e muitas cartas têm a mesma data "
      f"(em {a['pagina_ambigua_por_empate']} das {res['n_busca']} buscas preferenciais o empate cruza a fronteira "
      "da página), então a página conta como igual quando existe uma ordem compatível com a SQL em que as duas "
      "coincidem. A igualdade da página como o PostgreSQL a devolveu também está em `resultados.json`.")
    w("- **Revocação e precisão:** do conjunto devolvido contra o da busca aceita mais próxima (maior Jaccard). "
      "A revocação só é definida quando a busca aceita tem cartas; a precisão, quando a devolvida tem.")
    w(f"- **Buscas distintas executadas:** {mil(res['buscas_distintas_executadas'])} (com cache por SQL e "
      f"argumentos). Duração total: {num(res['duracao_s'] / 60, 1)} min.")
    w("")
    w("## Resultados por configuração")
    w("")
    w("O acerto por parâmetros é o do texto (repontuado aqui e conferido com `results/lote2/consolidado`). "
      "O acerto por resultado troca o critério: em vez de exigir os parâmetros do gabarito, exige o mesmo "
      "conjunto de cartas.")
    w("")
    L += tabela_configs(res)
    w("")
    w(f"Atenção ao denominador: em {a['todas_leituras_zero']} das {res['n_busca']} consultas que buscam, todas as "
      "leituras do gabarito devolvem zero cartas no acervo real (seção seguinte). Nelas, qualquer busca que também "
      "devolva zero conta como resultado igual. Por isso a coluna restrita às "
      f"{n3['n_gab_nao_vazio']} consultas cujo gabarito tem ao menos uma carta é a comparação mais justa.")
    w("")
    w("### Parâmetro certo × resultado igual")
    w("")
    L += tabela_cruzada(res)
    w("")
    i3 = d["inof3"]
    w(f"- **A pontuação por parâmetros não infla o acerto.** No TC v3 (E4B), {n3.get('cruz_certo_igual', 0)} das "
      f"{d['certos3']} buscas com parâmetros certos devolvem as mesmas cartas do gabarito.")
    w(f"- **Erros de parâmetro com o mesmo resultado:** no TC v3 (E4B), {n3.get('cruz_errado_igual', 0)} das "
      f"{d['erros3']} execuções que buscaram com parâmetro errado devolvem o mesmo conjunto, mas quase todos por "
      f"limitação do acervo, não porque o erro seja irrelevante: {i3.get(INOF_ZERO, 0)} zeram nos dois lados; "
      f"{i3.get(INOF_DATA, 0)} trocam o campo de data (publicação por criação, ou acrescentam o outro) e só "
      f"coincidem porque o CSW grava uma data só; {i3.get(INOF_LIMIT, 0)} mudam só o `limit` (o conjunto é o "
      f"mesmo, a página mostrada não); e {i3.get(INOF_REAL, 0)} são de fato inofensivos (nos três, conferidos à "
      "mão, a data inicial 1900 acrescentada). Por isso não chamamos a métrica por parâmetros de conservadora.")
    i_s3 = {k: v["n"] for k, v in s3.get("erro_inofensivo_por_tipo", {}).items()}
    w(f"- No SE v3 (E4B): {s3['contagens'].get('cruz_errado_igual', 0)} erros com o mesmo resultado, dos quais "
      f"{i_s3.get(INOF_ZERO, 0)} com zero cartas, {i_s3.get(INOF_DATA, 0)} por troca de campo de data, "
      f"{i_s3.get(INOF_LIMIT, 0)} de `limit` e {i_s3.get(INOF_REAL, 0)} de fato inofensivos. Campos dos erros que "
      f"mudam o resultado: {_campos(s3['campos_do_erro_que_muda_o_resultado'])}; no TC v3: "
      f"{_campos(t3['campos_do_erro_que_muda_o_resultado'])}.")
    tot_cd = sum(c["contagens"].get("certo_diferente", 0) for c in cfg.values())
    tot_ac = sum(c["contagens"].get("certo_diferente_keyword_acento_ou_caixa", 0) for c in cfg.values())
    tot_pt = sum(c["contagens"].get("certo_diferente_keyword_pontuacao", 0) for c in cfg.values())
    tot_mai = sum(c["contagens"].get("certo_diferente_keyword_maiuscula_acentuada", 0) for c in cfg.values())
    w(f"- **Parâmetro certo, resultado diferente:** {tot_cd} execuções nas 16 configurações "
      f"({n3.get('cruz_certo_diferente', 0)} no TC v3 E4B). Em {tot_ac} delas a keyword difere do gabarito só por "
      f"acento ou caixa, e em {tot_pt} por pontuação ou caractere (o nome do catálogo tem um caractere de controle "
      "e o sinal de menos U+2212, que a normalização da pontuação apaga). A pontuação compara texto normalizado, "
      "mas a busca por palavra-chave do protótipo (full-text `portuguese` e `LIKE`) é sensível a acento. "
      f"{tot_mai} delas têm letra maiúscula acentuada, que o `lower()` deste banco não converte porque ele foi "
      f"criado com locale `{a['locale_do_banco']['ctype']}`; num banco com locale UTF-8 essas {tot_mai} "
      "provavelmente coincidiriam.")
    w("")
    w("## Ambiguidade do acervo real (buscas do gabarito)")
    w("")
    w("Leitura preferencial de cada consulta, com os campos opcionais presentes.")
    w("")
    w("| Cartas devolvidas | Consultas |")
    w("|---|---|")
    for f, n in a["distribuicao_preferencial"].items():
        if f != "erro" or n:
            w(f"| {f} | {n} |")
    w("")
    w(f"- Mediana de {num(a['total_preferencial']['mediana'], 0)} cartas por busca; "
      f"**{a['mais_de_10']} das {res['n_busca']} buscas passam do tamanho da primeira página** (o usuário vê só "
      "as 10 mais recentes, ou o `limit` pedido).")
    w(f"- **Zeros:** {z['n']} buscas preferenciais devolvem zero cartas; em "
      f"{z['dos_quais_todas_as_leituras_zeram']} delas todas as leituras aceitas zeram e em "
      f"{z['dos_quais_alguma_leitura_tem_cartas']} alguma leitura alternativa tem cartas (entre as "
      f"{res['n_busca']} consultas, {a['alguma_leitura_zero_outra_nao']} têm leituras com e sem cartas). "
      f"Classificação das {z['n']} (o primeiro critério que se aplica):")
    for k, v in z["classes"].items():
        w(f"  - {k}: {v}")
    w(f"  - nas {z['dos_quais_todas_as_leituras_zeram']} que zeram em todas as leituras: "
      + _campos(z["classes_nas_que_zeram_em_todas_as_leituras"], 8) + ".")
    w("  - nas buscas que zeram pela combinação, o campo cuja retirada sozinha já devolve cartas: "
      + _campos(a["zeros_combinacao_culpados"]) + ".")
    w(f"  - Leitura: {d['zeros_projeto']} zeram pelo mapeamento (o CSW não traz projeto); "
      f"{d['zeros_tipo_escala']} pedem um tipo ou uma escala que o acervo coletado não tem (o gabarito cobre o "
      f"enumerado inteiro para testar a extração); {d['zeros_combinacao']} combinam filtros sem carta em comum; "
      f"{d['zeros_outros']} têm um filtro que sozinho já zera. No gerador do gabarito, as consultas por código (VM) "
      "e metade das consultas combinadas (VC) partem de um registro real, de onde vêm código, escala, tipo, CGEO "
      "e nome da folha; estado, município e projeto, e o CGEO ou o tipo quando o registro não os tem, são "
      "sorteados à parte. Os zeros por combinação aparecem nesses campos sorteados à parte.")
    w(f"- **Municípios homônimos e por substring:** o filtro `city` é `unaccent(lower(nome)) ILIKE '%valor%'`. "
      f"Das {mu['n_consultas_com_city']} consultas com município, **{mu['casam_mais_de_um_municipio']} casam mais "
      f"de um município** ({mu['casam_municipios_de_mais_de_uma_uf']} em mais de uma UF; até "
      f"{mu['max_municipios']}), por substring ou por homônimo em outra UF; em "
      f"{mu['das_ambiguas_com_estado_no_pedido']} delas o pedido também traz o estado, que restringe o resultado. "
      + "Exemplos: " + "; ".join(f"\"{k}\" casa {v['municipios']} ({', '.join(v['lista'][:4])}"
                                 f"{', ...' if v['municipios'] > 4 else ''})" for k, v in mu["exemplos"].items())
      + f". {mu['nenhum_municipio']} pede um município sem polígono na malha carregada.")
    ex_h = ", ".join(ho.get("exemplo_lugares_distintos", []))
    w(f"- **Folhas homônimas:** das {ho['n_consultas_por_nome']} consultas que pedem uma folha pelo nome, "
      f"{ho['consultas_com_2_ou_mais_folhas_homonimas']} têm 2 ou mais INOM/MI distintos com exatamente aquele "
      f"nome. Separando: **{ho['lugares_distintos']} têm folhas de mesmo nome em lugares distintos** "
      f"({ho['lugares_distintos_com_dois_inom_na_mesma_escala']} com dois INOM na mesma escala; até "
      f"{ho['max_lugares_distintos']} lugares, por exemplo {ho.get('exemplo_nome')} em {ex_h}), e {ho['so_folha_e_subdivisoes']} têm só a "
      "folha e suas subdivisões com o mesmo nome (a folha-mãe e uma folha contida nela, em outra escala). "
      f"{ho['consultas_com_2_ou_mais_registros_nome_exato']} têm 2 ou mais registros com o nome (a mesma folha em "
      "mais de um produto). A busca só por keyword, que também casa nomes que contêm o termo, traz mais folhas "
      f"que o nome exato em {ho['busca_so_keyword_com_mais_folhas_que_o_nome_exato']} consultas.")
    dup = d["duplicatas"]
    w(f"- **Produtos, edições e duplicatas por código:** das {ed['n_consultas_por_codigo']} consultas por MI ou "
      f"INOM ({_dist(ed['por_tipo'])}), **{ed['consultas_com_2_ou_mais_registros_do_codigo']} têm 2 ou mais "
      f"registros com o código** (até {ed['max_registros_por_codigo']}); {ed['com_mais_de_um_produto']} em mais "
      f"de um tipo de produto, {ed['com_mais_de_uma_data']} com mais de uma data, {ed['com_mais_de_uma_escala']} "
      f"em mais de uma escala, e {ed['com_registros_duplicados']} com registros duplicados no próprio catálogo "
      f"(mesma escala, tipo e data, UUIDs distintos; em {ed['so_duplicatas']} só há a duplicata). No catálogo "
      f"inteiro, {mil(dup.get('grupos'))} grupos ({mil(dup.get('registros'))} registros) têm o mesmo INOM, tipo, "
      "escala e data. A busca só pelo código traz outros registros além dos do código em "
      f"{ed['busca_so_keyword_traz_outros_registros']} consultas (o full-text casa a folha-mãe e vizinhas).")
    pm = ed["pagina_mostra_o_mais_recente"]
    w(f"- **A primeira página mostra a edição mais recente?** Sim em {pm.get('True', 0)}, não em "
      f"{pm.get('False', 0)} ({ed['nao_mostra_por_ordem_ascendente']} por ordem ascendente pedida), e em "
      f"{pm.get('None', 0)} o gabarito não devolve nenhum registro do código (outros filtros zeram). A ordem padrão "
      "é a data decrescente, então a mais recente vem primeiro.")
    mi = d["mi"]
    w(f"- **Grafia do MI:** {mil(mi.get('codigos_com_duas_grafias'))} códigos MI aparecem escritos com e sem zero "
      "à esquerda no BDGEx (\"0757-4\" e \"757-4\"). Em "
      f"{ed['mi_com_registros_na_grafia_alternativa']} das {ed['mi_consultas']} consultas por MI há registros na "
      "outra grafia, que a busca por igualdade não devolve. (MI com menos de 4 dígitos, por si, não é ambiguidade: "
      "é a numeração normal da 1:250.000.)")
    w(f"- **Grafia do nome:** {mil(a['inom_com_nomes_que_so_diferem_por_acento_ou_caixa'])} dos "
      f"{mil(a['inom_distintos'])} INOM do acervo têm registros com nomes que só diferem por acento ou caixa "
      "(ex.: \"Vila Propício\" e \"Vila Propicio\"). Como a busca por keyword é sensível a acento, a mesma folha "
      "aparece ou não conforme a grafia.")
    w("")
    w("### Siglas no filtro de estado")
    w("")
    w("O filtro de estado é `unaccent(lower(nome)) ILIKE '%valor%'`. Com a sigla no lugar do nome:")
    w("")
    w(f"- **Simulação das 27 siglas:** só {ss['resultado_igual_ao_do_nome']} devolvem o mesmo que o nome da UF; "
      f"{ss['nao_casam_nenhuma']} não casam estado nenhum (zero cartas); {ss['casam_a_propria_e_outras']} "
      f"casam a própria UF e outras; {ss['casam_outra_e_nao_a_propria']} casam o estado errado e não a própria ("
      + "; ".join(f"\"{s['sigla']}\" casa {', '.join(s['estados_que_casam'])}" for s in ss["por_sigla"]
                  if s["estados_que_casam"] and not s["inclui_a_propria_uf"]) + ").")
    w("")
    w("| Sigla | Estados que casam | Cartas com a sigla | Cartas com o nome | A mais | A menos |")
    w("|---|---|---|---|---|---|")
    for s in ss["por_sigla"]:
        if not s["igual"]:
            w(f"| {s['sigla']} | {', '.join(s['estados_que_casam']) or '(nenhum)'} | {mil(s['registros_sigla'])} | "
              f"{mil(s['registros_nome'])} | {mil(s['a_mais'])} | {mil(s['a_menos'])} |")
    iguais = [s["sigla"] for s in ss["por_sigla"] if s["igual"]]
    w(f"| {', '.join(iguais)} | só a própria | = | = | 0 | 0 |")
    w("")
    cfg_sig = {k.removeprefix("execucoes_"): v for k, v in sr.items() if k.startswith("execucoes_")}
    w(f"- **Execuções reais:** {sr.get('execucoes', 0)} execuções (de todas as configurações) puseram uma sigla em "
      f"`state`: {', '.join(cfg[k]['rotulo'] + ' ' + str(v) for k, v in cfg_sig.items())}. Nenhuma das configurações v1 "
      f"e v3 emitiu sigla. Em {sr.get('resultado_muda', 0)} delas o resultado muda em relação ao nome da UF "
      f"({mil(sr.get('a_mais_total', 0))} cartas a mais e {mil(sr.get('a_menos_total', 0))} a menos no total; "
      f"{sr.get('perde_tudo', 0)} perdem todas as cartas certas). Esse é o efeito que a v3 corrige no validador "
      "(sigla vira nome da UF) e que a métrica por parâmetros já contava como erro.")
    w("")
    w("## Latência da SQL no acervo real")
    w("")
    w(f"{lat['metodo']}.")
    w("")
    w("| Buscas | n | Mediana (ms) | p95 (ms) | Máximo (ms) |")
    w("|---|---|---|---|---|")
    for rot, k in (("Todas", "todas"), ("Com filtro espacial (city, state, supplyArea)", "com_filtro_espacial"),
                   ("Sem filtro espacial", "sem_filtro_espacial")):
        q = lat[k]
        w(f"| {rot} | {q['n']} | {num(q['mediana'], 0)} | {num(q['p95'], 0)} | {num(q['max'], 0)} |")
    for j, q in enumerate(lat.get("por_rodada") or [], 1):
        w(f"| Rodada {j} (todas) | {q['n']} | {num(q['mediana'], 0)} | {num(q['p95'], 0)} | {num(q['max'], 0)} |")
    w("")
    w(f"A medida varia entre rodadas (mediana de {_faixa_ms(d['lat_med'])} e p95 de {_faixa_ms(d['lat_p95'])} "
      f"nas {d['n_rodadas']} rodadas; uma execução anterior deste script, em outro momento, mediu 89 ms e 231 ms "
      "numa rodada só), porque a máquina é de uso geral; leia como ordem de grandeza: cerca de 0,1 s por busca. "
      f"Banco sintético: {lat['banco_sintetico']}. Para comparação, a latência do modelo por consulta, no texto, "
      "é de segundos.")
    w("")
    w("## Conferência")
    w("")
    w(f"15 consultas ({', '.join(CONFERENCIA_MANUAL['ids'])}), gabarito e {cfg[CONFERENCIA_MANUAL['configuracao']]['rotulo']}:")
    for x in CONFERENCIA_MANUAL["achados"]:
        w(f"- {x};")
    w("")
    w("Duas conferências independentes refizeram, com SQL própria, a carga (registros sorteados contra o JSON do "
      "CSW, sem divergência), buscas do gabarito, as acurácias, a tabela cruzada, as contagens de homônimas, "
      "códigos, siglas e cortes de página, e obtiveram os mesmos números. Os ajustes de interpretação que elas "
      "apontaram (classificação dos zeros e dos erros com o mesmo resultado, homônimas aninhadas, municípios por "
      "substring, duplicatas do catálogo, grafias do MI, chamadas recusadas, áreas de suprimento e latência) estão "
      "incorporados nesta versão.")
    w("")
    w("## Limitações e o que o mapeamento aproxima")
    w("")
    w(f"- **O dump não é o catálogo inteiro.** A coleta de 28/09/2026 tem {mil(dump.get('registros_no_dump'))} "
      f"registros, mas só {mil(dump.get('identificadores_distintos'))} identificadores distintos: a paginação do "
      f"servidor CSW repetiu páginas ({mil(dump.get('copias_descartadas'))} cópias idênticas descartadas). O "
      f"servidor declara {mil(dump.get('numberOfRecordsMatched'))} registros; provavelmente cerca de "
      f"{mil(dump.get('copias_descartadas'))} registros do catálogo não foram coletados (não verificamos se o número "
      f"declarado conta registros distintos). O texto entregue cita \"{mil(dump.get('registros_no_dump'))} "
      f"registros\"; o número de registros distintos é {mil(dump.get('identificadores_distintos'))}. As contagens de "
      "homônimas e edições são, portanto, limites inferiores.")
    w("- **Projeto:** o CSW não traz projeto (`projeto` = '' em todos). As "
      f"{a['consultas_com_project']} consultas com `project` devolvem zero no gabarito e em qualquer configuração; "
      "elas contam como resultado igual sempre que a configuração também usa `project` ou também zera.")
    w("- **Datas:** `data_publicacao` = `data_criacao` = `dc:date` (o CSW não distingue). Diferenças entre "
      "`publicationPeriod` e `creationPeriod`, ou entre `sortField`, não aparecem no resultado.")
    areas = (carga.get("areas_suprimento") or {}).get("por_area") or []
    cob = next((x["fracao_de_cada_uf_coberta"] for x in areas if "fracao_de_cada_uf_coberta" in x), {})
    sem_cx = sum(x.get("registros_sem_caixa_valida", 0) for x in areas if "nome" in x)

    def _cob(sigla: str, ufs: tuple) -> str:
        return ", ".join(f"{u} {round(100 * cob.get(sigla, {}).get(u, 0))}%" for u in ufs)
    w(f"- **Áreas de suprimento:** não há polígonos oficiais; cada área é a união das caixas dos registros "
      "produzidos pelo CGEO. O filtro `supplyArea` passa a significar \"a região onde aquele CGEO tem produtos no "
      "catálogo\", que se afasta muito da área de suprimento real: o 1º CGEO cobre "
      f"{_cob('1° CGEO', ('RS', 'PR', 'SC', 'RR', 'AM'))}; o 2º cobre {_cob('2° CGEO', ('AP', 'AC', 'AM'))}; "
      f"o 4º cobre {_cob('4° CGEO', ('AM', 'PA', 'RR', 'AC'))}. Contagens absolutas com `supplyArea` não "
      f"representam a área real. {sem_cx} registros dos CGEO ficaram fora por não terem caixa válida (zerada, "
      "ausente ou em pixel); o teto de área por caixa não excluiu nenhuma. "
      f"{a['consultas_com_supplyArea']} das {res['n_busca']} consultas usam `supplyArea` em alguma leitura; para "
      "a métrica 'resultado igual' o efeito é pequeno, porque quando o gabarito e a configuração pedem a mesma área "
      "o resultado coincide de qualquer forma; a aproximação pesa quando a configuração erra a área.")
    tipos = mapa.get("tipo_produto") or {}
    escalas = mapa.get("escala") or {}
    w(f"- **Tipo e escala:** heurística sobre título e formato (o CSW não tem campo de tipo); "
      f"{mil(tipos.get('(tipo não identificado)', 0))} registros ficaram sem tipo e {mil(escalas.get('?', 0))} sem "
      "escala, com valores que nenhum filtro casa. Ausentes do acervo coletado: os tipos "
      f"{', '.join(mapa.get('tipos_do_schema_ausentes') or [])}; as escalas "
      f"{', '.join(mapa.get('escalas_do_schema_ausentes') or [])}.")
    sem_malha = (carga.get("ibge") or {}).get("lista_sem_malha") or []
    w(f"- **Municípios:** {len(sem_malha)} município da lista do IBGE não tem polígono na malha baixada "
      f"({', '.join(sem_malha)}); a única consulta que o pede zera por isso.")
    w(f"- **Locale do banco:** `{a['locale_do_banco']['ctype']}`; o `lower()` não converte maiúsculas acentuadas "
      "(afeta só keywords escritas em maiúsculas com acento, contadas acima).")
    w("- **Resultado igual com zero cartas:** quando o gabarito devolve zero, toda busca que também zera conta "
      "como igual; a coluna restrita ao gabarito com cartas corrige isso.")
    w("- **O gabarito testa a extração, não a satisfação do usuário.** Parte das combinações tem campos sorteados "
      "à parte e não corresponde a nenhum registro. O teste mede se a busca do sistema devolve as mesmas cartas "
      "que a busca do gabarito, não se o usuário achou o que queria.")
    w("- É uma análise exploratória feita depois da entrega. Não muda nenhum número do texto.")
    if res.get("avisos"):
        w("")
        w("Avisos do script: " + "; ".join(res["avisos"]))
    w("")
    return "\n".join(L)


def _campos(d: dict[str, int], n: int = 6) -> str:
    itens = list(d.items())[:n]
    resto = sum(v for _, v in list(d.items())[n:])
    s = ", ".join(f"{k} ({v})" for k, v in itens) or "nenhum"
    return s + (f", outros ({resto})" if resto else "")


def _dist(d: dict[str, int]) -> str:
    return ", ".join(f"{k}: {v}" for k, v in d.items() if v)


def resumo(res: dict) -> str:
    cfg = res["configuracoes"]
    a = res["ambiguidade"]
    t3, s3 = cfg["e4b/tc3"], cfg["e4b/se3"]
    n3 = t3["contagens"]
    ss = a["siglas_simulacao"]
    sr = a["siglas_execucoes_reais"]
    ho, ed, mu = a["homonimas"], a["edicoes"], a["municipios"]
    z = a["zeros_preferencial"]
    d = derivados(res)
    i3 = d["inof3"]
    ngv = n3["n_gab_nao_vazio"]
    dup = d["duplicatas"]
    ex_h = ho.get("exemplo_lugares_distintos", [])
    p_lote, r_lote = pct(t3["acuracia_param_lote"]), pct(t3["acuracia_resultado_lote"])
    p_545 = pct(n3.get("acerto_param_gab_nao_vazio", 0), ngv)
    r_545 = pct(n3.get("acerto_resultado_gab_nao_vazio", 0), ngv)
    L = [
        "# Busca no acervo real: resumo para o slide",
        "",
        "Análise exploratória feita depois da entrega, sem rodar modelos. As buscas do lote 2 (o gabarito e o que "
        "cada configuração emitiu) foram executadas no acervo real do BDGEx, com a SQL do sistema sem mudança.",
        "",
        f"1. **Acervo real carregado.** {mil(res['tabelas']['datasets'])} registros distintos do CSW do BDGEx, "
        f"{mil(res['tabelas']['municipios'])} municípios e {res['tabelas']['estados']} UFs do IBGE. A SQL leva "
        f"cerca de 0,1 s por busca (mediana de {_faixa_ms(d['lat_med'])} e p95 de {_faixa_ms(d['lat_p95'])} em "
        f"{d['n_rodadas']} rodadas).",
        f"2. **O acerto se sustenta no resultado.** TC v3 (Gemma 4 E4B), lote inteiro, {p_lote} por parâmetros e "
        f"{r_lote} por resultado (mesmo conjunto de cartas). Só nas {ngv} consultas cujo gabarito tem cartas, "
        f"{p_545} e {r_545}. SE v3, {pct(s3['acuracia_param_lote'])} e {pct(s3['acuracia_resultado_lote'])}.",
        f"3. **A pontuação por parâmetros não infla o acerto.** No TC v3, {n3.get('cruz_certo_igual', 0)} das "
        f"{d['certos3']} buscas com parâmetros certos devolvem as mesmas cartas do gabarito (a que difere é uma "
        f"keyword sem acento). Dos {d['erros3']} erros de parâmetro com busca, {n3.get('cruz_errado_igual', 0)} "
        f"devolvem as mesmas cartas, mas só {i3.get(INOF_REAL, 0)} são de fato inofensivos "
        f"({i3.get(INOF_ZERO, 0)} zeram nos dois lados, {i3.get(INOF_DATA, 0)} trocam o campo de data e só "
        f"coincidem porque o CSW tem uma data só, {i3.get(INOF_LIMIT, 0)} mudam só o limit).",
        f"4. **O acervo real é ambíguo.** {ho['lugares_distintos']} de {ho['n_consultas_por_nome']} pedidos por nome "
        f"casam folhas homônimas em lugares distintos (por exemplo, {ho.get('exemplo_nome')} em {len(ex_h)} folhas, "
        f"{', '.join(ex_h)}). "
        f"{mu['casam_mais_de_um_municipio']} de {mu['n_consultas_com_city']} pedidos por município casam mais de um "
        "município (substring e homônimos de outras UFs). "
        f"{ed['consultas_com_2_ou_mais_registros_do_codigo']} de {ed['n_consultas_por_codigo']} pedidos por código "
        f"trazem 2 ou mais registros (produtos, edições e duplicatas do catálogo, que tem {mil(dup.get('registros'))} "
        f"registros duplicados em {mil(dup.get('grupos'))} grupos). {mil(d['mi'].get('codigos_com_duas_grafias'))} "
        f"códigos MI aparecem com e sem zero à esquerda. Em {a['mais_de_10']} de {res['n_busca']} buscas a primeira "
        "página corta o resultado, e a ordem por data mostra primeiro a edição mais recente.",
        f"5. **Sigla no filtro de estado quebra a busca.** Só {ss['resultado_igual_ao_do_nome']} das 27 siglas "
        f"devolvem o mesmo que o nome da UF, {ss['nao_casam_nenhuma']} não casam estado nenhum e "
        f"{ss['casam_outra_e_nao_a_propria']} casam o estado errado (\"SP\" casa Espírito Santo). Nas rodadas, "
        f"{sr.get('execucoes', 0)} execuções puseram sigla, todas nas v2, e {sr.get('resultado_muda', 0)} mudaram o "
        "resultado. A v3 converte a sigla e não emitiu nenhuma.",
        f"6. **Limites.** O dump do CSW tem {mil(res['tabelas']['datasets'])} registros distintos dos "
        f"{mil((res.get('carga') or {}).get('dump_csw', {}).get('numberOfRecordsMatched'))} declarados (a paginação "
        "repetiu páginas). O CSW não traz projeto nem distingue publicação de criação, e a área de suprimento foi "
        "aproximada pela região onde cada CGEO tem produtos no catálogo. "
        f"{z['n']} buscas preferenciais zeram ({z['dos_quais_todas_as_leituras_zeram']} em todas as leituras), "
        f"{d['zeros_projeto']} por projeto, que o CSW não traz, {d['zeros_tipo_escala']} por tipo ou escala que o "
        f"acervo não tem, {d['zeros_combinacao']} por combinação de campos sorteados à parte e {d['zeros_outros']} "
        "por outros motivos.",
        "",
        "## Resposta ao Maj Diniz",
        "",
    ]
    L.append(" ".join([
        f"Carregamos num PostGIS os {mil(res['tabelas']['datasets'])} registros distintos do CSW do BDGEx e as "
        "malhas do IBGE e executamos, com a SQL do sistema sem mudança, as buscas do gabarito e as que cada "
        "configuração emitiu no lote 2.",
        f"A avaliação por parâmetros não escondia erro do modelo, porque no TC v3 {n3.get('cruz_certo_igual', 0)} "
        f"das {d['certos3']} buscas com parâmetros certos devolvem as mesmas cartas do gabarito e o acerto passa "
        f"de {p_lote} por parâmetros para {r_lote} por resultado ({p_545} e {r_545} nas {ngv} consultas cujo "
        "gabarito tem cartas).",
        "O que ela escondia é a ambiguidade do próprio acervo, que pesa igual sobre o gabarito e sobre o modelo.",
        f"Em {ho['lugares_distintos']} de {ho['n_consultas_por_nome']} pedidos por nome há folhas homônimas em "
        f"lugares distintos, em {mu['casam_mais_de_um_municipio']} de {mu['n_consultas_com_city']} pedidos por "
        f"município o filtro casa mais de um município e em {ed['consultas_com_2_ou_mais_registros_do_codigo']} de "
        f"{ed['n_consultas_por_codigo']} pedidos por código vêm vários registros entre produtos, edições e "
        "duplicatas do catálogo.",
        f"A sigla no filtro de estado é o caso mais sério, já que só {ss['resultado_igual_ao_do_nome']} das 27 "
        "siglas devolvem o mesmo que o nome da UF, e é por isso que o validador da versão 3 troca a sigla pelo nome.",
        "A busca custa cerca de 0,1 s no acervo real, contra os segundos que o modelo leva.",
        "Ficam como trabalho futuro desambiguar folha e município pela UF ou pelo código, normalizar acento e o "
        "zero à esquerda do MI, agrupar edições e duplicatas e repetir o teste com a coleta completa do CSW, o "
        "campo de projeto e as áreas de suprimento oficiais.",
    ]))
    L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dsn", default=DSN_PADRAO)
    ap.add_argument("--so-relatorio", action="store_true", help="refaz os .md a partir de resultados.json")
    a = ap.parse_args()
    SAIDA.mkdir(parents=True, exist_ok=True)
    arq = SAIDA / "resultados.json"
    if not a.so_relatorio:
        res = avaliar(a.dsn)
        arq.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    res = json.loads(arq.read_text(encoding="utf-8"))
    (SAIDA / "relatorio.md").write_text(relatorio(res), encoding="utf-8")
    (SAIDA / "resumo_slide.md").write_text(resumo(res), encoding="utf-8")
    print(f"resultados: {arq.relative_to(RAIZ)}; relatorio.md e resumo_slide.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
