"""Etapa 4 do lote de validação: filtros, concordância e montagem do dataset.

    python scripts/lote_validacao/montar_lote.py   # -> data/lote_validacao.json + data/lote_validacao/relatorio.md

Uma consulta redigida só entra no lote se passar, nesta ordem, por:

1. checagens automáticas do texto contra o alvo — cada trecho exigido aparece na consulta
   (sem acento e sem caixa); o verbo do período confere com o alvo (publicação, criação ou
   nenhum); não aparece marcador forte de um campo que o alvo não tem (tipo de produto,
   escala, CGEO, ano ou expressão de tempo, ordenação, projeto, sigla ou nome de UF, código);
   não aparecem nomes de campos do sistema;
2. deduplicação — texto normalizado diferente de todas as 310 consultas e das consultas do
   lote já aceitas;
3. anotação às cegas (passada A) compatível com o gabarito por construção — mesma decisão
   (buscar / buscar ou esclarecer / não buscar) e leituras compatíveis nos dois sentidos
   (a leitura preferencial do anotador é aceita pelo gabarito e a do gabarito é aceita pelo
   anotador; `audit.comparar_anotacao`, o mesmo critério da auditoria das 310).

O gabarito de cada consulta aceita é o do alvo (construção), confirmado pelo anotador; nada é
corrigido à mão. Toda consulta descartada fica registrada, com o motivo, em
`data/lote_validacao/descartes.json`.
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

from pfc_busca import schema  # noqa: E402
from pfc_busca.evaluation import audit, gabarito  # noqa: E402
from pfc_busca.evaluation.dataset_builder import (  # noqa: E402
    CAMINHO_SAIDA,
    carregar_dataset,
    normalizar_consulta,
    validar,
)

DIR = RAIZ / "data" / "lote_validacao"
ARQ_ALVOS = DIR / "alvos.json"
ARQ_REDIGIDAS = DIR / "consultas_redigidas.json"
ARQ_ANOT_A = DIR / "anotacao" / "anotacao_A.json"
ARQ_ANOT_B = DIR / "anotacao" / "anotacao_B.json"
DESTINO = RAIZ / "data" / "lote_validacao.json"
ARQ_RELATORIO = DIR / "relatorio.md"
ARQ_DESCARTES = DIR / "descartes.json"
PAPER = RAIZ.parent / "paper_revisado"   # se existir, as tabelas e macros vão também para PAPER/tabelas

UFS = ("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO").split()
NOMES_UF = ["acre", "alagoas", "amapa", "amazonas", "bahia", "ceara", "distrito federal", "espirito santo", "goias",
            "maranhao", "mato grosso", "mato grosso do sul", "minas gerais", "paraiba", "parana", "pernambuco",
            "piaui", "rio de janeiro", "rio grande do norte", "rio grande do sul", "rondonia", "roraima",
            "santa catarina", "sao paulo", "sergipe", "tocantins"]   # "pará" fica de fora: coincide com "para"

MARCADORES = {
    "productType": re.compile(r"\btopogr|\bortoim|\borto\b|\bortos\b|vetoria|\bmdts?\b|\bmdss?\b|\btematic|\bcirc\b"
                              r"|modelos? digita|\bbanda [px]\b"),
    "scale": re.compile(r"\b1 \d|\b\d+ ?k\b|\b\d+ mil\b|\bescala"),
    "supplyArea": re.compile(r"cgeo|centro de geoinforma"),
    "periodo": re.compile(r"\b(19|20)\d\d\b|\bhoje\b|ano passado|(este|esse|deste|desse|neste|nesse) (ano|mes)"
                          r"|mes passado|\bsemana\b|trimestre|semestre|ultimos \d+ (dias|meses|anos)|\bdesde\b"
                          r"|a partir de \d|\bantes de \d|\bdepois de \d|\bapos \d|anos atras"),
    "ordenacao": re.compile(r"mais recent|mais antig|mais nov|mais velh|ordem cronolog|\bultim[oa]s?\b"
                            r"|\bprimeir[oa]s?\b"),
    "project": re.compile(r"\bprojeto\b(?! de)|olimp|\bcopa\b|\bbcd\b|base cartografica digital|\bbeca\b|\baman\b"
                          r"|mapeamento sistematico|cartografia sistematica"),
    "keyword": re.compile(r"\bmi \d|\binom\b|\b[ns][a-h] ?\d\d ?[vxyz]\b"),
}
NUMERAL = r"(\d+|dois|duas|tres|quatro|cinco|seis|sete|oito|nove|dez|quinze|trinta)"
CONTEXTOS_NEUTROS = re.compile(r"\b(primeir[oa]|ultim[oa]) (cgeo|centro|trimestre|semestre)\b"
                               r"|\bultimos " + NUMERAL + r" (dias|meses|anos)\b"
                               r"|\b(primeir[oa]|ultim[oa])s? (vez|coisa)\b|\bdesde ja\b")
CAMPOS_DO_SISTEMA = re.compile(r"\b(keyword|supplyarea|producttype|sortfield|sortdirection|publicationperiod"
                               r"|creationperiod|enum)\b", re.I)
VERBOS = {"publicacao": re.compile(r"public|\blanc"), "criacao": re.compile(r"\bcria|\bfeit[ao]s?\b|elabor|produz")}


def norm(texto: str) -> str:
    return normalizar_consulta(texto)


_MUNICIPIOS: set[str] = set()


def municipios() -> set[str]:
    if not _MUNICIPIOS:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import catalogo

        _MUNICIPIOS.update(norm(m["nome"]) for m in catalogo.carregar_ibge())
    return _MUNICIPIOS


def _contem(texto_norm: str, trecho: str) -> bool:
    t = norm(trecho)
    return bool(t) and f" {t} " in f" {texto_norm} "


def checar(alvo: dict, consulta: str) -> list[str]:
    """Motivos de descarte das checagens automáticas (lista vazia = passou)."""
    motivos = []
    q = norm(consulta)
    if not q or len(consulta) > 400:
        return ["consulta vazia ou longa demais"]
    if CAMPOS_DO_SISTEMA.search(consulta):
        motivos.append("nome de campo do sistema")
    for grupo in alvo["superficies"]:
        if not any(_contem(q, x) for x in grupo):
            motivos.append(f"falta o trecho exigido {grupo[0]!r}")
    verbo = alvo.get("verbo_periodo")
    if verbo in VERBOS and not VERBOS[verbo].search(q):
        motivos.append(f"período sem o verbo de {verbo}")
    if verbo == "nenhum" and any(v.search(q) for v in VERBOS.values()):
        motivos.append("período deveria vir sem verbo de publicação/criação")
    if alvo["familia"] == "VF":
        return motivos
    # região que também é nome de município ("Sertão", RS): a seção 6.3 faria dela `city`, o que o
    # alvo não prevê — a consulta é descartada em vez de receber um gabarito discutível
    if alvo.get("subtipo") in ("regiao", "regiao_com_criterio") and "city" not in alvo["esperado"]:
        homonima = next((g[0] for g in alvo["superficies"] if norm(g[0]) in municipios()), None)
        if homonima:
            motivos.append(f"região homônima de município: {homonima!r}")
    # marcadores de campos ausentes do alvo, depois de retirar contextos neutros e os trechos exigidos
    # (do mais longo para o mais curto, para que o "2" de um limite não quebre o código "2392-3-SE")
    trechos = sorted({x for grupo in alvo["superficies"] for x in grupo if x}, key=len, reverse=True)
    resto = f" {CONTEXTOS_NEUTROS.sub(' ', q)} "
    for x in trechos:
        t = norm(x)
        while t and f" {t} " in resto:
            resto = resto.replace(f" {t} ", " ")
    esperado = alvo["esperado"]
    presentes = set(esperado)
    for campo, padrao in MARCADORES.items():
        if campo == "periodo":
            if presentes & {"publicationPeriod", "creationPeriod"}:
                continue
        elif campo == "ordenacao":
            if "sortDirection" in presentes:
                continue
        elif campo in presentes:
            continue
        m = padrao.search(resto)
        if m:
            motivos.append(f"marcador de {campo} ausente do alvo: {m.group(0).strip()!r}")
    if "state" not in presentes:
        restante_original = consulta
        for x in trechos:
            restante_original = re.sub(r"(?<!\w)" + re.escape(x) + r"(?!\w)", " ", restante_original, flags=re.I)
        sigla = re.search(r"\b(" + "|".join(UFS) + r")\b", restante_original)
        if sigla:
            motivos.append(f"sigla de UF ausente do alvo: {sigla.group(0)!r}")
        nome = next((n for n in NOMES_UF if f" {n} " in resto), None)
        if nome and "city" not in presentes and "keyword" not in presentes:
            motivos.append(f"nome de UF ausente do alvo: {nome!r}")
    return motivos


# Apelidos de projeto que NÃO são o nome completo, nem sigla, nem apelido informado na descrição da
# ferramenta: sem a palavra "projeto" na consulta, o manual (seção 2, `project`) torna o campo opcional.
APELIDOS_PARCIAIS = {"Copa do Mundo 2014": ("copa do mundo", "copa 2014")}


def _esperado_pelo_texto(esperado: dict, consulta: str) -> tuple[dict, str | None]:
    projeto = esperado.get("project")
    q = norm(consulta)
    if isinstance(projeto, str) and projeto in APELIDOS_PARCIAIS and not re.search(r"\bprojeto\b", q) \
            and any(_contem(q, x) for x in APELIDOS_PARCIAIS[projeto]):
        return ({**esperado, "project": {gabarito.OPCIONAL: projeto}},
                "apelido parcial do projeto sem a palavra 'projeto': project opcional (manual, project)")
    return esperado, None


def caso_do_alvo(alvo: dict, consulta: str) -> dict:
    esperado, nota = _esperado_pelo_texto(alvo["esperado"], consulta)
    notas = "; ".join(x for x in (alvo["notas"], nota) if x)
    caso = {
        "id": alvo["id"], "origem": "V", "familia": alvo["familia"], "categorias": alvo["categorias"],
        "consulta": consulta, "esperado": esperado, "trocas": alvo["trocas"], "fonte": alvo["fonte"],
        "espera_tool_call": alvo["espera_tool_call"], "observacional": False,
        "aceita_nao_chamar": alvo["aceita_nao_chamar"], "notas": notas,
        "registro": alvo["registro"], "persona": alvo["persona"], "subtipo": alvo["subtipo"],
    }
    caso["alternativas"] = gabarito.expandir_trocas(caso["esperado"], caso["trocas"])
    leituras = gabarito.resolver_leituras(caso, audit.DATA_REFERENCIA)
    caso["leituras_multiplas"] = audit._ambiguo_gabarito(leituras)
    return caso


def decisao_caso(c: dict) -> str:
    if not c["espera_tool_call"]:
        return "não buscar"
    return "buscar ou esclarecer" if c.get("aceita_nao_chamar") else "buscar"


def decisao_anotador(a: dict) -> str:
    if a.get("observacional"):
        return "observacional"
    if not a.get("chamar_ferramenta"):
        return "não buscar"
    return "buscar ou esclarecer" if a.get("aceita_nao_chamar") else "buscar"


def divergencias(caso: dict, a: dict) -> list[str]:
    dg, da = decisao_caso(caso), decisao_anotador(a)
    if dg != da:
        return [f"decisão: construção={dg} anotador={da}"]
    if dg == "não buscar":
        return []
    return audit.comparar_anotacao(caso, a)


def caso_do_anotador(caso: dict, a: dict) -> dict:
    """A anotação A no formato de caso (para medir A × B com as mesmas funções)."""
    leituras = audit._leituras_do_anotador(a)
    return {**caso, "esperado": leituras[0], "alternativas": leituras[1:], "trocas": [],
            "espera_tool_call": bool(a.get("chamar_ferramenta")), "observacional": bool(a.get("observacional")),
            "aceita_nao_chamar": bool(a.get("aceita_nao_chamar"))}


def _pct(a: int, b: int) -> str:
    return f"{a}/{b} ({100 * a / b:.1f}%)" if b else "—"


def main() -> int:
    alvos = {a["id"]: a for a in json.loads(ARQ_ALVOS.read_text(encoding="utf-8"))["alvos"]}
    redigidas = json.loads(ARQ_REDIGIDAS.read_text(encoding="utf-8"))
    anot_a = json.loads(ARQ_ANOT_A.read_text(encoding="utf-8"))
    anot_b = json.loads(ARQ_ANOT_B.read_text(encoding="utf-8")) if ARQ_ANOT_B.exists() else {}
    textos_310 = {norm(c["consulta"]): c["id"] for c in carregar_dataset(CAMINHO_SAIDA)}

    etapas = Counter()
    descartes: list[dict] = []
    aceitos: list[dict] = []
    vistos: dict[str, str] = {}
    todos_casos: list[dict] = []
    for id_, alvo in alvos.items():
        consulta = redigidas.get(id_)
        if not consulta:
            descartes.append({"id": id_, "familia": alvo["familia"], "etapa": "redação", "motivos": ["não redigida"]})
            continue
        etapas["redigidas"] += 1
        caso = caso_do_alvo(alvo, consulta)
        todos_casos.append(caso)
        registro = {"id": id_, "familia": alvo["familia"], "subtipo": alvo["subtipo"], "consulta": consulta}
        motivos = checar(alvo, consulta)
        if motivos:
            descartes.append({**registro, "etapa": "checagem automática", "motivos": motivos})
            continue
        etapas["passaram_checagem"] += 1
        t = norm(consulta)
        if t in textos_310 or t in vistos:
            descartes.append({**registro, "etapa": "deduplicação",
                              "motivos": [f"repete {textos_310.get(t) or vistos.get(t)}"]})
            continue
        etapas["passaram_dedup"] += 1
        a = anot_a.get(id_)
        if a is None:
            descartes.append({**registro, "etapa": "anotação às cegas", "motivos": ["sem anotação"]})
            continue
        div = divergencias(caso, a)
        if div:
            descartes.append({**registro, "etapa": "anotação às cegas", "motivos": div,
                              "anotacao": {k: a.get(k) for k in ("chamar_ferramenta", "aceita_nao_chamar",
                                                                 "parametros", "justificativa")}})
            continue
        etapas["aceitas"] += 1
        vistos[t] = id_
        aceitos.append(caso)

    problemas = validar(aceitos)
    if problemas:
        print("PROBLEMAS DE VALIDAÇÃO:")
        for p in problemas[:30]:
            print("  ", p)
        return 1

    # --- concordância ---------------------------------------------------------------------
    anotados = [c for c in todos_casos if c["id"] in anot_a]
    conc_a = audit.concordancia(anotados, anot_a)
    dec_a = [(decisao_caso(c), decisao_anotador(anot_a[c["id"]])) for c in anotados]
    kappa_dec_a = audit.kappa_cohen(dec_a)
    com_b = [c for c in anotados if c["id"] in anot_b]
    conc_ab = conc_b = None
    kappa_dec_ab = kappa_dec_b = None
    if com_b:
        casos_a = [caso_do_anotador(c, anot_a[c["id"]]) for c in com_b]
        conc_ab = audit.concordancia(casos_a, anot_b)
        kappa_dec_ab = audit.kappa_cohen([(decisao_anotador(anot_a[c["id"]]), decisao_anotador(anot_b[c["id"]]))
                                          for c in com_b])
        conc_b = audit.concordancia(com_b, anot_b)
        kappa_dec_b = audit.kappa_cohen([(decisao_caso(c), decisao_anotador(anot_b[c["id"]])) for c in com_b])
        compat_ab = sum(1 for c, ca in zip(com_b, casos_a, strict=True) if not divergencias(ca, anot_b[c["id"]]))
        compat_b = sum(1 for c in com_b if not divergencias(c, anot_b[c["id"]]))
        aceitos_ids = {c["id"] for c in aceitos}
        compat_b_aceitos = sum(1 for c in com_b if c["id"] in aceitos_ids and not divergencias(c, anot_b[c["id"]]))
        n_b_aceitos = sum(1 for c in com_b if c["id"] in aceitos_ids)

    # --- dataset ----------------------------------------------------------------------------
    campos = Counter(k for c in aceitos for k in c["esperado"])
    DESTINO.write_text(json.dumps({
        "fonte": "lote de validação independente (docs/lote_validacao.md): alvos sorteados de catálogos reais "
                 "(BDGEx/CSW e IBGE), redação controlada, filtros automáticos e anotação às cegas",
        "manual": "docs/manual_de_anotacao.md (seções 1 a 6)",
        "data_referencia_anotacao": audit.DATA_REFERENCIA.isoformat(),
        "total": len(aceitos),
        "por_familia": dict(Counter(c["familia"] for c in aceitos)),
        "campos": dict(campos),
        "casos": aceitos,
    }, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    ARQ_DESCARTES.write_text(json.dumps(descartes, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")

    # --- relatório --------------------------------------------------------------------------
    familias = sorted({a["familia"] for a in alvos.values()}, key=lambda f: "SCMTOAEF".index(f[1]))
    por_fam = defaultdict(Counter)
    for a in alvos.values():
        por_fam[a["familia"]]["alvos"] += 1
    for c in aceitos:
        por_fam[c["familia"]]["aceitas"] += 1
    for d in descartes:
        por_fam[d["familia"]][d["etapa"]] += 1
    L = [
        "# Lote de validação — relatório de montagem", "",
        f"Gerado em {datetime.now():%Y-%m-%d %H:%M} por `scripts/lote_validacao/montar_lote.py`. "
        f"Metodologia: `docs/lote_validacao.md`.", "",
        "## Funil", "",
        "| Etapa | Consultas |", "|---|---|",
        f"| Alvos sorteados | {len(alvos)} |",
        f"| Consultas redigidas | {etapas['redigidas']} |",
        f"| Passaram nas checagens automáticas | {etapas['passaram_checagem']} |",
        f"| Passaram na deduplicação | {etapas['passaram_dedup']} |",
        f"| Compatíveis com a anotação às cegas (A) — **lote final** | **{etapas['aceitas']}** |", "",
        "## Por família", "",
        "| Família | Alvos | Checagem automática | Deduplicação | Anotação às cegas | Aceitas |",
        "|---|---|---|---|---|---|",
    ]
    for f in familias:
        x = por_fam[f]
        L.append(f"| {f} | {x['alvos']} | {x['checagem automática']} | {x['deduplicação']} | "
                 f"{x['anotação às cegas']} | {x['aceitas']} ({100 * x['aceitas'] / x['alvos']:.0f}%) |")
    motivos = Counter()
    for d in descartes:
        for m in d["motivos"]:
            motivos[re.sub(r"'[^']*'|\{.*\}|\[.*\]|: construção=.*", "…", m)[:90]] += 1
    L += ["", "## Motivos de descarte (agrupados)", "", "| Motivo | Ocorrências |", "|---|---|"]
    L += [f"| {m} | {n} |" for m, n in motivos.most_common(30)]

    def bloco_concordancia(titulo: str, conc: dict, kappa_dec: float, compat: int | None = None) -> list[str]:
        return [
            "", f"### {titulo}", "",
            f"- consultas: {conc['n']}",
            f"- decisão (buscar / buscar ou esclarecer / não buscar): kappa de Cohen = {kappa_dec:.3f}",
            f"- leituras compatíveis nos dois sentidos: {_pct(compat if compat is not None else conc['compativeis'], conc['n'])}",
            f"- leitura preferencial idêntica (quando ambos buscam): "
            f"{_pct(conc['preferencial_identica'], conc['n_ambos_chamam'])}",
            f"- presença de cada campo na leitura preferencial: kappa = {conc['presenca_campos_kappa']:.3f}",
            f"- valor igual quando ambos preenchem o campo: {_pct(conc['valores_iguais'], conc['valores_n'])}",
            f"- detecção de leituras múltiplas: kappa = {conc['ambiguidade_kappa']:.3f} "
            f"(gabarito {conc['ambiguidade_gabarito']}, anotador {conc['ambiguidade_anotador']})",
        ]

    compat_a = sum(1 for c in anotados if not divergencias(c, anot_a[c["id"]]))
    L += ["", "## Concordância", "",
          "Medidas de `audit.concordancia` (as mesmas da auditoria das 310), calculadas sobre todas as consultas "
          "redigidas e anotadas, antes do filtro. A decisão tem três classes neste lote (E: buscar ou esclarecer)."]
    L += bloco_concordancia("Gabarito por construção × anotador A (todas as consultas)", conc_a, kappa_dec_a, compat_a)
    if com_b:
        L += bloco_concordancia("Anotador A × anotador B (amostra aleatória de 20%)", conc_ab, kappa_dec_ab, compat_ab)
        L += bloco_concordancia("Gabarito por construção × anotador B (mesma amostra)", conc_b, kappa_dec_b, compat_b)
        L += ["", f"Nas consultas da amostra que entraram no lote, o anotador B — que não participou do filtro — "
                  f"é compatível com o gabarito em {_pct(compat_b_aceitos, n_b_aceitos)}. Essa é a estimativa "
                  "independente da qualidade do gabarito do lote final."]
    cats = Counter(x for c in aceitos for x in c["categorias"])
    L += ["", "## Composição do lote final", "",
          "| Categoria | Consultas |", "|---|---|"] + [f"| {k} | {cats[k]} |" for k in "SCMTOAEF" if cats[k]]
    L += ["", f"Consultas com mais de uma leitura aceita: {sum(c['leituras_multiplas'] for c in aceitos)}; "
              f"categoria E (buscar ou esclarecer): {sum(bool(c['aceita_nao_chamar']) for c in aceitos)}; "
              f"fora do domínio: {sum(not c['espera_tool_call'] for c in aceitos)}.", "",
          "| Campo | Ocorrências no gabarito |", "|---|---|"] + [f"| `{c}` | {campos[c]} |" for c in schema.CAMPOS]
    L += ["", "| Registro | Consultas |", "|---|---|"] + [
        f"| {r} | {n} |" for r, n in Counter(c["registro"] for c in aceitos).most_common()]
    subtipos_alvo = Counter((a["familia"], a["subtipo"]) for a in alvos.values() if a["subtipo"])
    subtipos_lote = Counter((c["familia"], c["subtipo"]) for c in aceitos if c["subtipo"])
    L += ["", "| Subtipo (VA, VE, VF) | Alvos | Aceitas |", "|---|---|---|"] + [
        f"| {f}·{s} | {n} | {subtipos_lote[(f, s)]} |" for (f, s), n in sorted(subtipos_alvo.items())]
    rng = random.Random(7)
    L += ["", "## Exemplos aceitos (5 por família, sorteados)", ""]
    for f in familias:
        amostra = rng.sample([c for c in aceitos if c["familia"] == f], min(5, sum(c["familia"] == f for c in aceitos)))
        for c in amostra:
            gab = "não buscar" if not c["espera_tool_call"] else "; ".join(gabarito.formatar_leitura(c["esperado"])) or "{}"
            if c.get("aceita_nao_chamar"):
                gab += " (ou esclarecer)"
            L.append(f"- `{c['id']}` {c['consulta']} → {gab}")
    L += ["", "## Exemplos descartados (sorteados)", ""]
    for d in rng.sample(descartes, min(25, len(descartes))):
        L.append(f"- `{d['id']}` [{d['etapa']}] {d.get('consulta', '')} — {'; '.join(d['motivos'])[:220]}")
    ARQ_RELATORIO.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")

    # --- texto (macros \res{lotedados}{...}{...} e tabelas) ---------------------------------
    def pct_tex(a: int, b: int) -> str:
        return f"{100 * a / b:.1f}".replace(".", ",") + "\\%" if b else "---"

    def f3(v: float | None) -> str:
        return "---" if v is None else f"{v:.3f}".replace(".", ",")

    defs = {
        "alvos": len(alvos), "redigidas": etapas["redigidas"], "checagem": etapas["passaram_checagem"],
        "dedup": etapas["passaram_dedup"], "aceitas": etapas["aceitas"],
        "descartadas": etapas["redigidas"] - etapas["aceitas"],
        "pctaceitas": pct_tex(etapas["aceitas"], etapas["redigidas"]),
        "kappadecisao": f3(kappa_dec_a), "compat": pct_tex(compat_a, len(anotados)),
        "valoresiguais": pct_tex(conc_a["valores_iguais"], conc_a["valores_n"]),
        "kappapresenca": f3(conc_a["presenca_campos_kappa"]), "kappaambiguidade": f3(conc_a["ambiguidade_kappa"]),
        "multiplas": sum(c["leituras_multiplas"] for c in aceitos),
        "nE": sum(bool(c["aceita_nao_chamar"]) for c in aceitos), "nF": sum(not c["espera_tool_call"] for c in aceitos),
        "nB": len(com_b),
    }
    for k in "SCMTOAEF":
        defs[f"cat{k}"] = cats[k]
    if com_b:
        defs.update(kappadecisaoAB=f3(kappa_dec_ab), compatAB=pct_tex(compat_ab, len(com_b)),
                    kappapresencaAB=f3(conc_ab["presenca_campos_kappa"]),
                    valoresiguaisAB=pct_tex(conc_ab["valores_iguais"], conc_ab["valores_n"]),
                    compatBfinal=pct_tex(compat_b_aceitos, n_b_aceitos), nBfinal=n_b_aceitos,
                    compatBfinalabs=compat_b_aceitos)
    macros = ["% AUTO-GERADO por scripts/lote_validacao/montar_lote.py — não editar à mão",
              r"\providecommand{\res}[3]{\ifcsname res@#1@#2@#3\endcsname\csname res@#1@#2@#3\endcsname\else\textbf{??}\fi}"]
    macros += [f"\\expandafter\\def\\csname res@lotedados@geral@{k}\\endcsname{{{v}}}" for k, v in sorted(defs.items())]
    nomes_fam = {"VS": "Simples (um critério)", "VC": "Compostas", "VM": "Códigos MI/INOM", "VT": "Tempo",
                 "VO": "Ordenação", "VA": "Leituras múltiplas", "VE": "Subespecificadas", "VF": "Fora do domínio"}
    tab = [r"\begin{table}[htbp!]", r"\centering", r"\caption{Lote de validação: do alvo ao lote final, por família}",
           r"\label{tab:lote_composicao}", r"\footnotesize", r"\begin{tabular}{|l|l|c|c|c|c|}", r"\hline",
           r"\textbf{Família} & \textbf{Testa} & \textbf{Alvos} & \textbf{Checagens} & \textbf{Anotação às cegas} & "
           r"\textbf{Lote final} \\", r"\hline"]
    for f in familias:
        x = por_fam[f]
        tab.append(f"{f} & {nomes_fam[f]} & {x['alvos']} & $-${x['checagem automática'] + x['deduplicação']} & "
                   f"$-${x['anotação às cegas']} & {x['aceitas']} \\\\")
    tab += [r"\hline", f"\\textbf{{Total}} & & {len(alvos)} & $-${len(alvos) - etapas['passaram_dedup']} & "
            f"$-${etapas['passaram_dedup'] - etapas['aceitas']} & \\textbf{{{etapas['aceitas']}}} \\\\", r"\hline",
            r"\end{tabular}", r"\fonte{Elaborada pelos autores. Checagens: descartadas nas checagens automáticas "
            r"e na deduplicação. Anotação às cegas: descartadas por incompatibilidade entre o gabarito por construção "
            r"e a anotação A.}", r"\end{table}", ""]
    conc_linhas = [("Decisão (buscar / buscar ou esclarecer / não buscar), kappa", f3(kappa_dec_a),
                    f3(kappa_dec_ab) if com_b else "---"),
                   ("Leituras compatíveis nos dois sentidos", pct_tex(compat_a, len(anotados)),
                    pct_tex(compat_ab, len(com_b)) if com_b else "---"),
                   ("Leitura preferencial idêntica", pct_tex(conc_a["preferencial_identica"], conc_a["n_ambos_chamam"]),
                    pct_tex(conc_ab["preferencial_identica"], conc_ab["n_ambos_chamam"]) if com_b else "---"),
                   ("Presença dos campos, kappa", f3(conc_a["presenca_campos_kappa"]),
                    f3(conc_ab["presenca_campos_kappa"]) if com_b else "---"),
                   ("Valor igual quando ambos preenchem", pct_tex(conc_a["valores_iguais"], conc_a["valores_n"]),
                    pct_tex(conc_ab["valores_iguais"], conc_ab["valores_n"]) if com_b else "---"),
                   ("Detecção de leituras múltiplas, kappa", f3(conc_a["ambiguidade_kappa"]),
                    f3(conc_ab["ambiguidade_kappa"]) if com_b else "---")]
    tab_conc = [r"\begin{table}[htbp!]", r"\centering", r"\caption{Concordância na anotação às cegas do lote de validação}",
                r"\label{tab:lote_concordancia}", r"\footnotesize", r"\begin{tabular}{|l|c|c|}", r"\hline",
                rf"\textbf{{Medida}} & \textbf{{Construção $\times$ A}} (n={len(anotados)}) & "
                rf"\textbf{{A $\times$ B}} (n={len(com_b)}) \\", r"\hline"]
    tab_conc += [f"{m} & {a} & {b} \\\\" for m, a, b in conc_linhas]
    tab_conc += [r"\hline", r"\end{tabular}", r"\fonte{Elaborada pelos autores. Medidas de \texttt{audit.concordancia}, "
                 r"as mesmas da auditoria das 310 consultas, sobre todas as consultas redigidas (antes do filtro). "
                 r"A: anotação de todas as consultas; B: segunda anotação independente de uma amostra aleatória de 20\%.}",
                 r"\end{table}", ""]
    saidas_tex = {"numeros_lote_dados.tex": "\n".join(macros) + "\n", "tab_lote_composicao.tex": "\n".join(tab),
                  "tab_lote_concordancia.tex": "\n".join(tab_conc)}
    for nome, conteudo in saidas_tex.items():
        (DIR / nome).write_text(conteudo, encoding="utf-8", newline="\n")
        if PAPER.is_dir():
            (PAPER / "tabelas" / nome).write_text(conteudo, encoding="utf-8", newline="\n")

    print(f"{len(aceitos)} consultas no lote -> {DESTINO.relative_to(RAIZ)}")
    print(dict(etapas))
    print(f"kappa decisão (construção × A) = {kappa_dec_a:.3f}; compatíveis {compat_a}/{len(anotados)}")
    if com_b:
        print(f"A × B: kappa decisão = {kappa_dec_ab:.3f}; compatíveis {compat_ab}/{len(com_b)}; "
              f"B no lote final: {compat_b_aceitos}/{n_b_aceitos}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
