"""Ferramentas auxiliares da v3 e validador dos parâmetros de busca.

A v3 dá ao Tool Calling o que a Saída Estruturada não tem por construção: consultar funções no meio
da resposta e receber um retorno. As funções são determinísticas e seguem o manual de anotação
(`docs/manual_de_anotacao.md`), que é a especificação do comportamento esperado:

- `identificar_nome`: diz se um trecho da consulta é UF (inclusive sigla), município (lista do IBGE,
  com a UF), folha do acervo (índice do BDGEx), região ou nada disso — com a forma canônica;
- `normalizar_codigo`: forma canônica de um código MI ou INOM (sem prefixo; INOM com hífens) e se ele
  consta no índice do acervo;
- `normalizar_escala`: escala canônica do SCN, ou o conjunto aceito para expressões qualitativas;
- `resolver_periodo`: intervalo ISO de uma expressão de tempo, pela tabela do manual (a aritmética
  de datas sai do modelo e vai para o código);
- `validar_parametros`: o que `buscar_catalogo` confere antes de executar — erros de forma (sigla no
  lugar do nome, prefixo no código, escala fora do enumerado) e avisos de evidência (campo sem
  trecho correspondente na consulta: tipo de produto a partir de "cartas", limite sem número,
  estado deduzido do município).

As mesmas funções servem ao controle da Saída Estruturada v3 (validação com nova tentativa), para
que a diferença entre as duas meça o mecanismo, e não o código.
"""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

from pfc_busca import schema

DADOS = Path(__file__).resolve().parent / "dados"

UFS = {"AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
       "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso",
       "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
       "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
       "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
       "SE": "Sergipe", "TO": "Tocantins"}
ESTADO_OU_CAPITAL = {"sao paulo", "rio de janeiro"}
SIGLAS_AMBIGUAS = {"SE", "ES", "TO", "PA", "MA", "AL", "AM", "AP", "PE", "MS", "SC"}
REGIOES = ["amazonia legal", "centro oeste", "nordeste", "sudeste", "norte", "sul", "litoral", "semiarido",
           "sertao nordestino", "pantanal", "fronteira", "planalto central", "regiao"]
TIPOS = [
    ("SCN Carta Ortoimagem Banda P Pol HH", r"banda p\b"),
    ("SCN Carta Ortoimagem Banda X Pol HH", r"banda x\b"),
    ("SCN Carta Topográfica Vetorial", r"vetoria"),
    ("SCN Carta Topográfica Matricial", r"topografic|\btopo\b"),
    ("SCN Carta Ortoimagem", r"ortoimg|ortoimage|\bortos?\b|ortofoto"),
    ("MDT — RAM", r"\bmdts?\b|modelos? digita(?:l|is) d[oe] terreno"),
    ("MDS — RAM", r"\bmdss?\b|modelos? digita(?:l|is) de superficie"),
    ("CIRC", r"\bcirc\b"),
    ("Cartas Temáticas Não SCN", r"\btematic"),
]
PROJETOS = [
    ("Base Cartográfica Digital da Bahia", r"base cartografica digital da bahia|\bbcd (?:da )?bahia"),
    ("Base Cartográfica Digital de Rondônia", r"base cartografica digital de rondonia|\bbcd (?:de )?rondonia|projeto rondonia"),
    ("Base Cartográfica Digital do Amapá", r"base cartografica digital do amapa|\bbcd (?:do )?amapa"),
    ("Mapeamento Sistemático", r"mapeamento sistematico|cartografia sistematica"),
    ("Olimpíadas Rio 2016", r"olimpiada|rio 2016|jogos olimpicos"),
    ("Copa do Mundo 2014", r"copa do mundo|copa 2014"),
    ("Copa das Confederações", r"copa das confederacoes"),
    ("NGA-BECA", r"\bnga\b|\bbeca\b"),
    ("AMAN", r"\baman\b"),
]
NUMERAIS = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
            "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "quinze": 15, "vinte": 20, "trinta": 30,
            "cem": 100}
RE_MI = re.compile(r"^\d{1,4}(?:-[1-4](?:-(?:NO|NE|SO|SE))?)?$")
RE_INOM = re.compile(r"^[NS][A-H]-\d{2}(?:-[VXYZ](?:-[A-D](?:-(?:VI|IV|V|III|II|I)(?:-[1-4](?:-(?:NO|NE|SO|SE))?)?)?)?)?$")
RE_INOM_COMPACTO = re.compile(
    r"^([NS][A-H])(\d{2})([VXYZ])?([A-D])?(VI|IV|V|III|II|I)?([1-4])?(NO|NE|SO|SE)?$")
PREFIXOS_CODIGO = re.compile(r"^(?:c[oó]digo|folha|carta|mi|inom|articula[cç][aã]o)\b[\s:.-]*", re.I)
PALAVRAS_GENERICAS = {"carta", "cartas", "folha", "folhas", "mapa", "mapas", "produto", "produtos",
                      "ortoimagem", "ortoimagens", "acervo"}


def norm(texto: Any) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", str(texto or "")) if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s.lower()).split())


# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def municipios() -> dict[str, list[tuple[str, str]]]:
    """nome normalizado -> [(nome, sigla da UF)]."""
    saida: dict[str, list[tuple[str, str]]] = {}
    for nome, sigla, _uf in json.loads((DADOS / "municipios_ibge.json").read_text(encoding="utf-8")):
        saida.setdefault(norm(nome), []).append((nome, sigla))
    return saida


@lru_cache(maxsize=1)
def indice_acervo() -> dict[str, Any] | None:
    arq = DADOS / "indice_folhas.json"
    if not arq.exists():
        return None
    bruto = json.loads(arq.read_text(encoding="utf-8"))
    folhas: dict[str, list[tuple[str, dict]]] = {}
    for nome, info in bruto["folhas"].items():
        folhas.setdefault(norm(nome), []).append((nome, info))
    return {"folhas": folhas, "mi": bruto["mi"], "inom": bruto["inom"]}


@lru_cache(maxsize=1)
def _chaves_nomes() -> list[str]:
    chaves = list(municipios())
    idx = indice_acervo()
    if idx:
        chaves += list(idx["folhas"])
    return chaves


NOMES_UF = {norm(n): n for n in UFS.values()}


# ---------------------------------------------------------------------------
# identificar_nome
# ---------------------------------------------------------------------------

def _uf_de(texto: str) -> str | None:
    t = texto.strip().upper()
    if t in UFS:
        return UFS[t]
    return NOMES_UF.get(norm(texto))


def identificar_nome(nome: str) -> str:
    bruto = (nome or "").strip()
    t = norm(bruto)
    if not t:
        return "Informe o trecho da consulta com o nome (ex.: identificar_nome(nome='Campinas, SP'))."
    t = re.sub(r"^(?:o |a )?(?:estado|municipio|cidade|regiao) (?:de |do |da |dos |das )?", "", t) or t
    linhas: list[str] = []
    # "Município, UF" / "Município (UF)" / "Município - UF" / "Município/UF"
    m = re.match(r"^(.*?)[\s,/(–-]+\(?([A-Za-z]{2})\)?$", bruto)
    if m and m.group(2).upper() in UFS and norm(m.group(1)) in municipios():
        cidade = norm(m.group(1))
        sigla = m.group(2).upper()
        candidatos = [c for c in municipios()[cidade] if c[1] == sigla] or municipios()[cidade]
        nome_m = candidatos[0][0]
        return (f"'{bruto}': município {nome_m} ({sigla}), com a sigla da UF na consulta → city='{nome_m}' e "
                f"state='{UFS[sigla]}'.")
    if len(t) == 2 and t.upper() in UFS:
        return f"'{bruto}': sigla de UF → state='{UFS[t.upper()]}' (escreva o nome por extenso, nunca a sigla)."
    if t in NOMES_UF:
        nome_uf = NOMES_UF[t]
        if t in ESTADO_OU_CAPITAL:
            return (f"'{bruto}': sem as palavras 'estado' ou 'cidade', é ambíguo entre o estado e a capital; "
                    f"o padrão é state='{nome_uf}'.")
        return f"'{bruto}': estado → state='{nome_uf}'."
    if t in REGIOES or t.startswith("regiao ") or any(t == r or t.startswith(r + " ") for r in REGIOES):
        if t not in municipios():
            return f"'{bruto}': região, não é estado nem município → não preencha state nem city para ela."
    achou_municipio = municipios().get(t)
    idx = indice_acervo()
    achou_folha = idx["folhas"].get(t) if idx else None
    if achou_municipio:
        ufs = sorted({s for _, s in achou_municipio})
        nome_m = achou_municipio[0][0]
        linhas.append(f"'{bruto}': município {nome_m} ({', '.join(ufs)}) → city='{nome_m}' (o nome inteiro; "
                      f"não acrescente state se a consulta não citar o estado).")
    if achou_folha:
        nome_f, info = achou_folha[0]
        escalas = ", ".join(info.get("escalas") or []) or "escala não informada"
        linhas.append(f"'{bruto}': nome de folha do acervo ({nome_f}; {escalas}) → se a consulta disser 'carta' ou "
                      f"'folha' antes do nome, keyword='{nome_f}'.")
    if linhas:
        return " ".join(linhas)
    proximos = difflib.get_close_matches(t, _chaves_nomes(), n=3, cutoff=0.84)
    if proximos:
        sugestoes = []
        for p in proximos:
            if p in municipios():
                nome_m, sigla = municipios()[p][0]
                sugestoes.append(f"município {nome_m} ({sigla})")
            elif idx and p in idx["folhas"]:
                sugestoes.append(f"folha {idx['folhas'][p][0][0]}")
        return (f"'{bruto}': não encontrado exatamente; o mais próximo: {'; '.join(sugestoes)}. Use a grafia correta "
                f"se for o mesmo lugar.")
    return (f"'{bruto}': não é UF, município do IBGE nem folha conhecida do acervo. Se vier depois de 'carta' ou "
            f"'folha', use keyword com o nome como escrito; senão, não preencha state nem city.")


# ---------------------------------------------------------------------------
# normalizar_codigo
# ---------------------------------------------------------------------------

def forma_canonica_codigo(codigo: str) -> tuple[str | None, str | None]:
    """(código canônico, 'MI' | 'INOM') ou (None, None)."""
    t = (codigo or "").strip()
    for _ in range(3):
        t2 = PREFIXOS_CODIGO.sub("", t).strip()
        if t2 == t:
            break
        t = t2
    t = t.strip(" .,;").upper().replace("–", "-").replace(" ", "-")
    t = re.sub(r"-+", "-", t)
    if RE_MI.match(t):
        return t, "MI"
    if RE_INOM.match(t):
        return t, "INOM"
    compacto = t.replace("-", "")
    m = RE_INOM_COMPACTO.match(compacto)
    if m:
        partes = [p for p in m.groups() if p]
        canon = f"{partes[0]}-{partes[1]}" + "".join(f"-{p}" for p in partes[2:])
        if RE_INOM.match(canon):
            return canon, "INOM"
    return None, None


def normalizar_codigo(codigo: str) -> str:
    canon, tipo = forma_canonica_codigo(codigo)
    if not canon:
        return (f"'{codigo}' não é código MI (ex.: 2965-2-NE) nem INOM (ex.: SF-22-Y-D-II-4) válido. Se for nome de "
                f"folha, use identificar_nome.")
    idx = indice_acervo()
    existe = ""
    if idx:
        n = idx["mi" if tipo == "MI" else "inom"].get(canon)
        existe = f" Consta no acervo ({n} registro(s))." if n else " Não consta no índice do acervo (confira a grafia)."
    return f"Código {tipo} → keyword='{canon}' (só o código, sem 'MI', 'INOM', 'folha' ou 'carta').{existe}"


# ---------------------------------------------------------------------------
# normalizar_escala
# ---------------------------------------------------------------------------

ESCALAS_GRANDES = ["1:25.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000"]


def forma_canonica_escala(texto: str) -> tuple[str | None, list[str]]:
    t = norm(texto)
    if re.search(r"grande escala|escala grande", t):
        return None, ESCALAS_GRANDES
    if re.search(r"media escala|escala media", t):
        return None, ["1:50.000", "1:100.000"]
    if re.search(r"maior (?:que|do que) (?:1 )?100 ?(?:k|mil|000)", t):
        return None, ["1:50.000"] + ESCALAS_GRANDES
    if re.search(r"pequena escala|escala pequena", t):
        return "1:250.000", []
    if re.search(r"detalhad", t):
        return "1:25.000", []
    numero = None
    razao = re.search(r"1\s*[:/]\s*(\d[\d.\s]*)", str(texto or ""))
    m = re.search(r"\b(\d{1,3}) ?(?:k|mil)\b", t)
    if razao:
        denominador = int(re.sub(r"\D", "", razao.group(1)))
        if denominador % 1000:
            return None, []
        numero = denominador // 1000
    elif m:
        numero = int(m.group(1))
    else:
        m2 = re.search(r"\b1 (\d{4,6})\b", t) or re.search(r"^(\d{4,6})$", t)
        if m2:
            numero = int(m2.group(1)) // 1000
        else:
            for palavra, valor in NUMERAIS.items():
                if re.search(rf"\b{palavra} mil\b", t):
                    numero = valor
                    break
            if re.search(r"vinte e cinco mil", t):
                numero = 25
            if re.search(r"duzentos e cinquenta mil", t):
                numero = 250
    if numero is None:
        return None, []
    canon = f"1:{numero}.000"
    return (canon, []) if canon in schema.ESCALAS else (None, [])


def normalizar_escala(texto: str) -> str:
    canon, conjunto = forma_canonica_escala(texto)
    if canon:
        return f"'{texto}' → scale='{canon}'."
    if conjunto:
        return (f"'{texto}' é qualitativa: qualquer uma destas é aceita — {', '.join(conjunto)}. Escolha uma "
                f"(ex.: scale='{conjunto[0]}').")
    return f"'{texto}' não corresponde a nenhuma escala do SCN ({', '.join(schema.ESCALAS)}); não preencha scale."


# ---------------------------------------------------------------------------
# resolver_periodo
# ---------------------------------------------------------------------------

def _numero(texto: str) -> int | None:
    return int(texto) if texto.isdigit() else NUMERAIS.get(texto)


def regra_de_tempo(expressao: str) -> tuple[str | None, dict | None]:
    """(regra de relative_time, período absoluto) para uma expressão de tempo em português."""
    t = norm(expressao)
    fixas = [
        (r"segundo semestre (?:do ano )?passado", "segundo_semestre_anterior"),
        (r"ultimo trimestre do ano passado", "ultimo_trimestre_ano_anterior"),
        (r"(?:primeiro|1o|1) trimestre", "primeiro_trimestre_corrente"),
        (r"trimestre passado|trimestre anterior", "trimestre_anterior"),
        (r"\b(?:esse|este|deste|desse|neste|nesse) ano\b|\bano (?:atual|corrente)\b", "ano_corrente"),
        (r"\bano passado\b|\bano anterior\b", "ano_anterior"),
        (r"\b(?:2|dois) anos atras\b|\bha (?:2|dois) anos\b", "dois_anos_atras"),
        (r"\bmes passado\b|\bmes anterior\b", "mes_anterior"),
        (r"\b(?:este|esse|deste|desse|neste|nesse) mes\b|\bmes (?:atual|corrente)\b", "mes_corrente"),
        (r"\bsemana passada\b|\bsemana anterior\b", "semana_passada"),
        (r"\b(?:esta|essa|desta|dessa|nesta|nessa) semana\b", "semana_corrente"),
        (r"\bhoje\b", "hoje"),
    ]
    for padrao, regra in fixas:
        if re.search(padrao, t):
            return regra, None
    m = re.search(r"ultim[oa]s? (\d+|" + "|".join(NUMERAIS) + r") (dias?|meses|mes|anos?)\b", t)
    if m:
        n = _numero(m.group(1))
        unidade = {"dia": "dias", "dias": "dias", "mes": "meses", "meses": "meses", "ano": "anos", "anos": "anos"}[m.group(2)]
        if n:
            return f"ultimos_{n}_{unidade}", None
    m = re.search(r"\b(?:desde|a partir de) (\d{4})\b", t)
    if m:
        return f"desde_{m.group(1)}", None
    m = re.search(r"\b(?:depois de|apos|posteriores? a) (\d{4})\b", t)
    if m:
        return f"depois_de_{m.group(1)}", None
    m = re.search(r"\b(?:antes de|anteriores? a|ate) (\d{4})\b", t)
    if m:
        return f"antes_de_{m.group(1)}", None
    m = re.search(r"\b(?:entre|de) (\d{4}) (?:e|a|ate) (\d{4})\b", t)
    if m:
        a, b = sorted((int(m.group(1)), int(m.group(2))))
        return None, {"start": f"{a}-01-01", "end": f"{b}-12-31"}
    anos = re.findall(r"\b(19\d{2}|20\d{2})\b", t)
    if len(anos) == 1:
        return None, {"start": f"{anos[0]}-01-01", "end": f"{anos[0]}-12-31"}
    return None, None


def resolver_periodo(expressao: str, hoje: date) -> str:
    from pfc_busca.evaluation import relative_time

    regra, absoluto = regra_de_tempo(expressao)
    if regra and relative_time.existe(regra):
        periodo = relative_time.resolver(regra, hoje)
        descricao = relative_time.texto_regra(regra)
    elif absoluto:
        periodo, descricao = absoluto, "ano ou intervalo de anos explícito"
    else:
        return (f"Não reconheci '{expressao}' como expressão de tempo. Se for uma, escreva o intervalo em ISO "
                f"(AAAA-MM-DD) você mesmo; se não for, não preencha período.")
    return (f"'{expressao}' ({descricao}) → {json.dumps(periodo)}. Use publicationPeriod se a consulta tiver verbo de "
            f"publicação (publicada, lançada) ou nenhum verbo; creationPeriod se tiver criada, feita, elaborada ou "
            f"produzida.")


# ---------------------------------------------------------------------------
# Validador de buscar_catalogo
# ---------------------------------------------------------------------------

RE_ORDEM = re.compile(r"mais recente|mais antig|mais nov|mais velh|\bultim|\bprimeir|ordem|cronolog|recentes|antigas?\b"
                      r"|atualiza|\bnovas?\b|\bvelhas?\b|ordenad")
# pedido de UM resultado: ordenação no singular ("a carta mais recente", "só a mais antiga", "última atualização")
RE_SINGULAR_ORDEM = re.compile(r"\bmais recente\b|\bmais antig[ao]\b|\bmais nov[ao]\b|\bmais velh[ao]\b|"
                               r"\bultim[ao]\b(?! (?:trimestre|semestre|ano|mes|semana|dias?)\b)|"
                               r"\bprimeir[ao]\b(?! (?:cgeo|centro|trimestre|semestre)\b)")


def sigla_mencionada(sigla: str, consulta: str) -> bool:
    """A consulta cita a UF pela sigla? Em maiúsculas (fora de códigos), ou em minúsculas numa posição de UF."""
    if re.search(rf"(?<![A-Za-zÀ-ú\-]){sigla}(?![A-Za-zÀ-ú\-])", consulta):
        return True
    s, c = sigla.lower(), consulta.lower()
    fim = r"(?=\s*(?:[?.!,;:)]|$))"
    if re.search(rf"\(\s*{s}\s*\)", c) or re.search(rf"(?:[,/–]|\s-)\s*{s}\b{fim}", c):
        return True
    if re.search(rf"\b(?:do|da|de|no|na|em|pro|pra)\s+{s}\b{fim}", c):
        return True
    # depois de preposição, no meio da frase ("olimpíadas em al pro trabalho"); "se" fica de fora (pronome)
    if s != "se" and re.search(rf"\b(?:do|da|no|na|em)\s+{s}\b(?![\s-]?\d)", c):
        return True
    # sigla solta em minúsculas, desde que não seja o começo de um INOM ("sc-20-v-c")
    return sigla not in SIGLAS_AMBIGUAS and bool(re.search(rf"\b{s}\b(?![\s-]?\d)", c))


# apelidos que o manual aceita como menção ao estado (seção 2, state/city)
APELIDOS_UF = {"Rio de Janeiro": [r"\brio\b"], "Minas Gerais": [r"\bminas\b"]}
RE_NUMERO = re.compile(r"\b\d+\b|\b(?:" + "|".join(k for k in NUMERAIS if k not in ("um", "uma")) + r")\b")
RE_TEMPO = re.compile(r"\b(?:19|20)\d{2}\b|\bhoje\b|\bano\b|\bmes\b|\bsemana\b|trimestre|semestre|\bdias?\b|\bdesde\b|"
                      r"\bapos\b|\bantes\b|\bdepois\b|\bmeses\b|\banos\b")
RE_CGEO = re.compile(r"cgeo|centro de geoinforma")


def _codigo_na_consulta(keyword: str, q: str) -> bool:
    return norm(keyword) in q or norm(keyword).replace(" ", "") in q.replace(" ", "")


def validar_parametros(params: dict[str, Any], consulta: str, hoje: date | None = None) -> tuple[list[str], list[str]]:
    """(erros, avisos). Erros: forma fora do padrão (a busca não é executada). Avisos: campo sem evidência."""
    erros: list[str] = []
    avisos: list[str] = []
    q = norm(consulta)
    for campo in params:
        if campo not in schema.CAMPOS:
            erros.append(f"{campo}: parâmetro inexistente; os válidos são {', '.join(schema.CAMPOS)}.")
    for campo in ("scale", "productType", "supplyArea", "project", "sortField", "sortDirection"):
        v = params.get(campo)
        if v is None:
            continue
        validos = schema.valores_validos(campo) or []
        if v not in validos:
            dica = ""
            if campo == "scale":
                canon, conjunto = forma_canonica_escala(str(v))
                dica = f" Use '{canon}'." if canon else (f" Use um de {conjunto}." if conjunto else "")
            erros.append(f"{campo}: '{v}' não é um valor válido.{dica or ' Valores válidos: ' + '; '.join(validos)}")
    estado = params.get("state")
    if estado is not None:
        e = str(estado).strip()
        if norm(e) not in NOMES_UF:
            partes = e.split()
            if e.upper() in UFS:
                erros.append(f"state: '{e}' é sigla; use o nome por extenso: state='{UFS[e.upper()]}'.")
            elif partes and partes[0].upper() in UFS and norm(" ".join(partes[1:])) in NOMES_UF:
                erros.append(f"state: use só o nome: state='{NOMES_UF[norm(' '.join(partes[1:]))]}'.")
            else:
                erros.append(f"state: '{e}' não é o nome de uma UF brasileira. Se for região, não preencha state; se "
                             f"for município, use city.")
        else:
            nome_uf = NOMES_UF[norm(e)]
            sigla = next(s for s, n in UFS.items() if n == nome_uf)
            apelido = any(re.search(a, q) for a in APELIDOS_UF.get(nome_uf, []))
            if not (norm(nome_uf) in q or sigla_mencionada(sigla, consulta) or apelido):
                avisos.append(f"state='{nome_uf}': o estado não aparece na consulta. Não deduza o estado a partir do "
                              f"município, da folha ou do nome de um projeto; remova state se a consulta não o citar.")
    cidade = params.get("city")
    if cidade is not None:
        c = norm(cidade)
        if c in NOMES_UF and c not in ESTADO_OU_CAPITAL:
            avisos.append(f"city='{cidade}': é nome de estado; se a consulta fala do estado, use state.")
        elif c not in municipios():
            proximo = difflib.get_close_matches(c, list(municipios()), n=1, cutoff=0.84)
            if proximo:
                avisos.append(f"city='{cidade}': não é município do IBGE; o mais próximo é "
                              f"'{municipios()[proximo[0]][0][0]}'. Use a grafia correta se for o mesmo.")
            else:
                avisos.append(f"city='{cidade}': não é município do IBGE. Se for nome de folha ('carta X'), use "
                              f"keyword; se for região, não preencha.")
        else:
            maiores = [k for k in municipios() if k != c and k.startswith(c + " ") and k in q]
            if maiores:
                avisos.append(f"city='{cidade}': a consulta cita o município '{municipios()[maiores[0]][0][0]}', "
                              f"com o nome inteiro; use-o sem separar partes do nome.")
    kw = params.get("keyword")
    if kw is not None:
        k = str(kw).strip()
        if norm(k) in PALAVRAS_GENERICAS or not norm(k):
            erros.append(f"keyword: '{k}' é palavra genérica, não nome de carta nem código; remova keyword.")
        elif k in schema.TIPOS_PRODUTO or norm(k) in {norm(t) for t in schema.TIPOS_PRODUTO}:
            erros.append(f"keyword: '{k}' é tipo de produto; use productType e remova keyword.")
        else:
            canon, tipo = forma_canonica_codigo(k)
            sem_prefixo = PREFIXOS_CODIGO.sub("", k).strip()
            if canon and canon != k and (sem_prefixo != k or canon.replace("-", "") == k.upper().replace("-", "")):
                erros.append(f"keyword: '{k}' → use só o código na forma canônica: keyword='{canon}'.")
            elif not canon and not _codigo_na_consulta(k, q):
                avisos.append(f"keyword='{k}': esse texto não aparece na consulta; use o nome ou código como está "
                              f"escrito nela.")
            elif not canon and norm(k) in municipios() and not re.search(rf"\b(?:carta|folha)s? {re.escape(norm(k))}\b", q):
                avisos.append(f"keyword='{k}': é nome de município e não vem depois de 'carta' ou 'folha'; use city.")
    for campo in ("publicationPeriod", "creationPeriod"):
        p = params.get(campo)
        if p is None:
            continue
        if not isinstance(p, dict) or not p or not set(p) <= {"start", "end"}:
            erros.append(f"{campo}: use um objeto com as chaves 'start' e/ou 'end' em AAAA-MM-DD.")
            continue
        try:
            datas = {k: date.fromisoformat(v) for k, v in p.items()}
        except (TypeError, ValueError):
            erros.append(f"{campo}: datas em ISO, AAAA-MM-DD.")
            continue
        if "start" in datas and "end" in datas and datas["start"] > datas["end"]:
            erros.append(f"{campo}: start depois de end.")
        if not RE_TEMPO.search(q):
            avisos.append(f"{campo}: a consulta não tem expressão de tempo; remova o período.")
        elif hoje and set(p) == {"start"} and datas["start"] == hoje:
            avisos.append(f"{campo}: o intervalo começa hoje e não tem fim; confira a expressão com resolver_periodo.")
    if params.get("productType") and not any(re.search(pad, q) for _, pad in TIPOS):
        avisos.append(f"productType='{params['productType']}': a consulta não nomeia um tipo de produto; 'cartas', "
                      f"'mapas' e 'folhas' sozinhos não definem tipo — remova productType.")
    if params.get("supplyArea") and not RE_CGEO.search(q):
        avisos.append("supplyArea: a consulta não cita um Centro de Geoinformação (CGEO); remova supplyArea.")
    if params.get("project") and not re.search(r"\bprojeto\b", q) and not any(re.search(p, q) for _, p in PROJETOS):
        avisos.append("project: a consulta não cita um projeto; remova project.")
    if (params.get("sortField") or params.get("sortDirection")) and not RE_ORDEM.search(q):
        avisos.append("sortField/sortDirection: a consulta não pede ordem nem posição (mais recente, mais antiga, "
                      "primeiras, últimas); remova a ordenação.")
    limite = params.get("limit")
    if limite is not None:
        if not isinstance(limite, int) or limite <= 0:
            erros.append("limit: número inteiro positivo.")
        elif not tem_quantidade(consulta) and not (limite == 1 and RE_SINGULAR_ORDEM.search(q)):
            avisos.append(f"limit={limite}: a consulta não diz quantos resultados quer (nem pede um só, no singular); "
                          f"remova limit.")
    avisos += campos_faltando(params, consulta)
    return erros, avisos


RE_CODIGO_NA_CONSULTA = re.compile(r"\b(?:mi|folha|carta)[\s-]*\d{1,4}(?:-[1-4](?:-(?:no|ne|so|se))?)?"
                                   r"(?![\d:./]|\s?(?:mil|k)\b)|"
                                   r"\b[ns][a-h][\s-]?\d{2}[\s-]?[vxyz]\b|"
                                   r"\b[ns][a-h]\d{2}[vxyz]", re.I)
RE_ORDEM_PEDIDA = re.compile(r"mais recente|mais antig|mais nov|mais velh|ordem cronolog|em ordem|\bultim[oa]s? "
                             r"(?!\d|dois|tres|quatro|cinco|seis|sete|oito|nove|dez|quinze|trinta|mes|ano|semana|"
                             r"trimestre|semestre|dias)|\bprimeir[oa]s? (?!cgeo|centro|trimestre|semestre)")


def tem_quantidade(consulta: str) -> bool:
    """A consulta diz quantos resultados quer? Números de códigos, escalas, anos, CGEOs e prazos não contam."""
    t = re.sub(r"\b[ns][a-h][\s-]?\d{2}(?:[\s-]?[a-z0-9]{1,3}\b)*", " ", consulta, flags=re.I)
    t = RE_CODIGO_NA_CONSULTA.sub(" ", t)
    t = re.sub(r"1\s*[:/]\s*[\d.]+|\b\d+\s?(?:k|mil)\b|\b(?:19|20)\d{2}\b|\b\d\s*[ºo°]\s*(?:cgeo|centro)", " ", t,
               flags=re.I)
    q = norm(t)
    q = re.sub(r"ultim[oa]s? (?:\d+|" + "|".join(NUMERAIS) + r") (?:dias?|meses|mes|anos?)", " ", q)
    q = re.sub(r"\b(?:\d+|dois) anos atras\b|\b\d+ cgeo\b", " ", q)
    return bool(RE_NUMERO.search(q))


def _uf_citada(consulta: str) -> str | None:
    """Sigla de UF citada como critério: em maiúsculas, ou depois de vírgula/parêntese/barra/hífen."""
    for sigla, nome in UFS.items():
        if sigla_mencionada(sigla, consulta):
            return nome
    m = re.search(r"\bestado d[eoa]s? ([a-zà-ú ]+)", consulta.lower())
    if m:
        for n in sorted(NOMES_UF, key=len, reverse=True):
            if norm(m.group(1)).startswith(n):
                return NOMES_UF[n]
    return None


def campos_faltando(params: dict[str, Any], consulta: str) -> list[str]:
    """Avisos de campo AUSENTE cuja evidência está na consulta (o lado do recall)."""
    q = norm(consulta)
    avisos = []
    if "state" not in params:
        uf = _uf_citada(consulta)
        if uf:
            avisos.append(f"a consulta cita a UF {uf}; se ela é critério da busca, preencha state='{uf}'.")
    if "supplyArea" not in params and RE_CGEO.search(q):
        avisos.append("a consulta cita um Centro de Geoinformação; preencha supplyArea (ex.: '3° Centro de "
                      "Geoinformação').")
    if "keyword" not in params and RE_CODIGO_NA_CONSULTA.search(consulta):
        avisos.append("a consulta cita um código MI ou INOM; preencha keyword com o código (use normalizar_codigo).")
    if not ({"publicationPeriod", "creationPeriod"} & set(params)):
        # anos dentro de escalas ("1:2000"), códigos e nomes de projeto ("rio 2016") não são expressão de tempo
        limpa = norm(re.sub(r"1\s*[:/]\s*[\d.]+|\b\d+\s?(?:k|mil)\b", " ", consulta))
        for _, padrao in PROJETOS:
            limpa = re.sub(padrao, " ", limpa)
        limpa = RE_CODIGO_NA_CONSULTA.sub(" ", limpa)
        regra, absoluto = regra_de_tempo(limpa)
        if regra or absoluto:
            avisos.append("a consulta tem uma expressão de tempo; preencha publicationPeriod ou creationPeriod "
                          "(use resolver_periodo).")
    if "scale" not in params:
        canon, conjunto = forma_canonica_escala(consulta)
        if canon or conjunto:
            avisos.append("a consulta cita uma escala; preencha scale (use normalizar_escala).")
    if "productType" not in params:
        tipo = next((nome for nome, padrao in TIPOS if re.search(padrao, q)), None)
        if tipo:
            avisos.append(f"a consulta nomeia um tipo de produto; preencha productType (ex.: '{tipo}').")
    if "project" not in params:
        projeto = next((nome for nome, padrao in PROJETOS
                        if re.search(padrao, q) and not re.fullmatch(r".*cartografia sistematica.*", q)), None)
        if projeto:
            avisos.append(f"a consulta cita um projeto; preencha project='{projeto}'.")
    if not (params.get("sortField") or params.get("sortDirection")) and RE_ORDEM_PEDIDA.search(q):
        avisos.append("a consulta pede ordem ou posição (mais recente, mais antiga, primeiras, últimas); preencha "
                      "sortField e sortDirection.")
    return avisos


def mensagem_validacao(erros: list[str], avisos: list[str]) -> str:
    if erros:
        return ("BUSCA NÃO EXECUTADA. Corrija e chame buscar_catalogo de novo:\n- " + "\n- ".join(erros + avisos))
    return ("AVISOS sobre os parâmetros (a busca ainda não foi executada). Corrija o que for necessário e chame "
            "buscar_catalogo de novo; se os parâmetros estiverem certos, repita a chamada com os mesmos valores:\n- "
            + "\n- ".join(avisos))
