"""Linhas de base com Saída Estruturada, para comparar com o Tool Calling (Cap. 5).

A solução avaliada (``agent.Tradutor``) usa Tool Calling: o modelo decide se chama
``buscar_catalogo`` e com quais argumentos. Para medir o que essa troca rendeu, o
mesmo dataset e as mesmas métricas são aplicados a duas configurações com Saída
Estruturada, a abordagem do protótipo do 1º CGEO:

``saida_estruturada``
    Isola o mecanismo. Mesmo modelo, mesmo prompt de sistema (sem as instruções
    sobre chamar ou não a ferramenta, que não se aplicam), zero-shot, sem
    dicionário, temperatura 0 e mesmas descrições dos parâmetros; o modelo responde
    com um objeto JSON (modo JSON do Ollama, o mesmo que o Instructor usa no
    protótipo) conforme o schema dos parâmetros, incluído no prompt. O modelo não
    tem como recusar: a aplicação sempre executa a busca. Valores vazios ('' e limite
    0), que a aplicação ignoraria, são tratados como ausentes. (A decodificação restrita
    ao schema, testada antes, fechava os intervalos de datas depois do primeiro
    limite e foi descartada por penalizar a linha de base por um artefato da
    gramática.)

``prototipo``
    Reproduz o método do protótipo (``backend/src/services/llm/`` do repositório
    1cgeo/prototipo_busca_llm): dicionário COMMON_TERMS aplicado à consulta antes do
    modelo; prompt original, em inglês, com dez exemplos resolvidos; modo JSON do
    Ollama com a mensagem que o Instructor (modo JSON_SCHEMA, zod-stream de 2024-2025)
    acrescenta, que traz só a descrição geral do schema — o schema vai no campo
    ``response_format.schema``, que o Ollama ignora no tipo ``json_object``; validação
    pelo schema Zod (campo obrigatório ``reasoning`` e enumerados do protótipo), com
    até três novas tentativas que devolvem ao modelo os erros de validação; fallback
    por expressões regulares; e a
    validação pós-extração do protótipo (códigos MI/INOM, enumerados, limite e
    datas). Diferenças deliberadas, registradas no manifesto: temperatura 0 (o
    protótipo usa 0,6); os valores padrão de ordenação (publicationDate/DESC) que o
    protótipo acrescenta a toda busca não são contados como parâmetros extraídos; a
    validação de estado e município contra o banco não é feita (a avaliação não usa
    banco); e a saída é traduzida para o vocabulário do PFC pela tabela
    ``VOCABULARIO_PROTOTIPO``, a mesma correspondência usada para alinhar ao schema
    do PFC o gabarito dos casos de teste do protótipo (camada P).
"""

from __future__ import annotations

import calendar
import json
import re
import time
import unicodedata
from datetime import date, timedelta
from typing import Any

import ollama
from pydantic import ValidationError

from pfc_busca import schema
from pfc_busca.agent import (
    BASE_URL_PADRAO,
    KEEP_ALIVE,
    MAX_TOKENS_SAIDA,
    TIMEOUT_S,
    Traducao,
    _classificar_erro,
    capacidades,
)
from pfc_busca.prompts import _DIAS_DA_SEMANA
from pfc_busca.prototipo_termos import COMMON_TERMS

ABORDAGENS = ("saida_estruturada", "prototipo")
ROTULO_ABORDAGEM = {"saida_estruturada": "saida-estruturada", "prototipo": "prototipo"}
MAX_NOVAS_TENTATIVAS = 3          # max_retries do Instructor no protótipo
MODELO_PROTOTIPO = "phi4:14b"     # modelo do protótipo (service.ts)


def rotulo_modelo(tag: str, abordagem: str) -> str:
    """Identificador gravado nas execuções: distingue a linha de base da rodada com Tool Calling."""
    return f"{tag} [{ROTULO_ABORDAGEM[abordagem]}]"


# ---------------------------------------------------------------------------
# Configuração "saida_estruturada": mesmo prompt, mesmo schema, sem ferramenta
# ---------------------------------------------------------------------------

PARAMETROS = schema.FERRAMENTA_BUSCAR_CATALOGO["function"]["parameters"]
FORMATO_SE = "json"   # modo JSON do Ollama; o schema vai no prompt

_MODELO_SE = """Você é o assistente de busca do catálogo de produtos cartográficos do acervo da Diretoria de Serviço Geográfico (DSG).

A data atual é {data_iso} ({dia_semana}, {data_br}). Use-a para resolver qualquer expressão de tempo relativo presente na consulta.

Instruções:
1. Extraia da consulta os parâmetros de busca do catálogo e responda somente com um objeto JSON que siga o schema abaixo. Siglas, abreviações e grafias sem acento são esperadas e devem ser reconhecidas e normalizadas.
2. Preencha somente os parâmetros explicitamente presentes na consulta. Não invente valores, não complete campos por suposição, não acrescente ordenação ou limite que não foram pedidos e não use valores de exemplo. Omita os parâmetros ausentes.
3. Converta cada valor para a forma canônica descrita na definição do parâmetro correspondente.

Schema dos parâmetros (JSON Schema):
{schema_json}"""


def montar_prompt_se(hoje: date) -> str:
    return _MODELO_SE.format(
        data_iso=hoje.isoformat(), dia_semana=_DIAS_DA_SEMANA[hoje.weekday()],
        data_br=hoje.strftime("%d/%m/%Y"),
        schema_json=json.dumps(PARAMETROS, ensure_ascii=False, indent=2),
    )


# ---------------------------------------------------------------------------
# Configuração "prototipo": porte do método do protótipo
# ---------------------------------------------------------------------------

# Enumerados do protótipo (backend/src/types/api.ts)
ESCALAS_PROTOTIPO = list(schema.ESCALAS)
TIPOS_PROTOTIPO = [
    "Altura da vegetação", "CDGV EDGV Defesa F Ter Não SCN", "CTM Venezuela", "Carta Ortoimagem Especial",
    "Cartas CENSIPAM", "Cartas Temáticas Não SCN", "MDS - RAM", "MDT - RAM", "Modelo Tridimensional MDS",
    "Modelo Tridimensional MDT", "Nao SCN Carta Topografica Especial Matricial", "Ortoimagem",
    "Ortoimagem Radar Colorida", "Ortoimagem SCN", "Ortoimagem banda P", "Ortoimagem banda P pol HH",
    "Ortoimagem banda P pol HV", "Ortoimagem banda X pol HH", "SCN Carta Especial Matricial",
    "SCN Carta Ortoimagem", "SCN Carta Topografica Matricial", "SCN Carta Topografica Vetorial",
    "SCN Carta Topografica Vetorial EDGV 3.0", "Tematico CIRC", "Tematico CIRP", "Tematico CISC",
    "Tematico CISP", "Tematico CMIL", "Tematico CTBL", "Tematico CTP",
]
CENTROS_PROTOTIPO = list(schema.CENTROS_GEOINFORMACAO)
PROJETOS_PROTOTIPO = [
    "AMAN", "Base Cartográfica Digital da Bahia", "Base Cartográfica Digital de Rondônia",
    "Base Cartográfica Digital do Amapá", "COTer Não EDGV", "Cobertura Aerofotogramétrica do Estado de São Paulo",
    "Conversão do Mapeamento Sistematico do SCN para Vetorial", "Copa das Confederações", "Copa do Mundo 2014",
    "Mapeamento Sistemático", "Mapeamento de Áreas de Interesse da Força", "NGA-BECA", "Olimpíadas Rio 2016",
    "Produtos Temáticos Diversos", "Radiografia da Amazônia",
]
ENUMS_PROTOTIPO = {"scale": ESCALAS_PROTOTIPO, "productType": TIPOS_PROTOTIPO, "supplyArea": CENTROS_PROTOTIPO,
                   "project": PROJETOS_PROTOTIPO, "sortField": list(schema.CAMPOS_ORDENACAO),
                   "sortDirection": list(schema.DIRECOES_ORDENACAO)}

# Vocabulário do protótipo -> forma canônica do PFC (valores sem correspondente ficam como estão
# e contam como erro na comparação). Tipos de produto e projetos; escalas e centros coincidem.
VOCABULARIO_PROTOTIPO: dict[str, dict[str, str]] = {
    "productType": {
        "SCN Carta Topografica Matricial": "SCN Carta Topográfica Matricial",
        "SCN Carta Topografica Vetorial": "SCN Carta Topográfica Vetorial",
        "SCN Carta Topografica Vetorial EDGV 3.0": "SCN Carta Topográfica Vetorial",
        "SCN Carta Ortoimagem": "SCN Carta Ortoimagem",
        "Ortoimagem": "SCN Carta Ortoimagem",
        "Ortoimagem SCN": "SCN Carta Ortoimagem",
        "Ortoimagem banda P pol HH": "SCN Carta Ortoimagem Banda P Pol HH",
        "Ortoimagem banda X pol HH": "SCN Carta Ortoimagem Banda X Pol HH",
        "MDT - RAM": "MDT — RAM",
        "Modelo Tridimensional MDT": "MDT — RAM",
        "MDS - RAM": "MDS — RAM",
        "Modelo Tridimensional MDS": "MDS — RAM",
        "Tematico CIRC": "CIRC",
        "Cartas Temáticas Não SCN": "Cartas Temáticas Não SCN",
    },
}

_PROMPT_PROTOTIPO = r"""You are an expert in natural language processing specialized in extracting search parameters for cartographic data. Current date: ${today}.

Here are comprehensive examples of query analysis:

Query: "inom SF-22-Y-D-II-4-SE do primeiro cgeo criado na semana passada"
{
  "reasoning": "1. Found complete INOM code with SE suffix - must preserve entirely. 2. 'primeiro cgeo' translates to '1° Centro de Geoinformação'. 3. 'semana passada' with 'criado' means creation date 7-13 days before current date (${today}). 4. When relative dates are mentioned with 'criado', use creation period not publication.",
  "keyword": "SF-22-Y-D-II-4-SE",
  "supplyArea": "1° Centro de Geoinformação",
  "creationPeriod": {
    "start": "2025-01-27",
    "end": "2025-02-02"
  }
}

Query: "preciso do MDT-RAM MI 2965-2-NE do segundo cgeo em 5k"
{
  "reasoning": "1. Found complete MI code with directional suffix - use as keyword. 2. 'MDT-RAM' matches to 'MDT - RAM'. 3. 'segundo cgeo' normalizes to '2° Centro de Geoinformação'. 4. '5k' translates to '1:5.000'. 5. MI code presence makes this a specific chart request.",
  "keyword": "2965-2-NE",
  "supplyArea": "2° Centro de Geoinformação",
  "productType": "MDT - RAM",
  "scale": "1:5.000"
}

Query: "Carta Altura da Vegetação Passo da Seringueira em grande escala criada entre 2022 e 2023"
{
  "reasoning": "1. No MI/INOM patterns - use location name as keyword. 2. Explicit product type mention. 3. 'grande escala' standardizes to '1:1.000'. 4. Date range with 'criada' indicates creation period. 5. Use full year range for exact years mentioned.",
  "keyword": "Passo da Seringueira",
  "scale": "1:1.000",
  "productType": "Altura da vegetação",
  "creationPeriod": {
    "start": "2022-01-01",
    "end": "2023-12-31"
  }
}

Query: "SCN Carta Topografica Matricial detalhadas (2k ou 5k) de brasilia do ultimo trimestre"
{
  "reasoning": "1. Between multiple scales, choose most detailed (2k). 2. 'brasilia' normalizes to 'Brasília'. 3. 'ultimo trimestre' means previous complete quarter (2024-Q4). 4. Without creation/criação mention, assume publication date. 5. City name without MI/INOM is location filter, not keyword.",
  "scale": "1:2.000",
  "city": "Brasília",
  "productType": "SCN Carta Topografica Matricial",
  "publicationPeriod": {
    "start": "2024-10-01",
    "end": "2024-12-31"
  }
}

Query: "5 cartas mais antigas SF-22-Y-D ou MI 2965-2-NE do quarto cgeo em pequena escala"
{
  "reasoning": "1. Multiple identifiers - use first mentioned (SF-22-Y-D). 2. 'quarto cgeo' normalizes to '4° Centro de Geoinformação'. 3. 'pequena escala' means '1:250.000'. 4. '5 cartas' sets limit. 5. 'mais antigas' without creation context means publication date sorting.",
  "keyword": "SF-22-Y-D",
  "supplyArea": "4° Centro de Geoinformação",
  "scale": "1:250.000",
  "limit": 5,
  "sortField": "publicationDate",
  "sortDirection": "ASC"
}

Query: "cartas Tematico CTBL publicadas em 2023 do quinto cgeo em mg e es em media escala"
{
  "reasoning": "1. 'Tematico CTBL' is exact product type match. 2. Full year for 2023 publication. 3. 'quinto cgeo' normalizes to '5° Centro de Geoinformação'. 4. Multiple states - use first (MG → Minas Gerais). 5. 'media escala' means '1:50.000'.",
  "productType": "Tematico CTBL",
  "publicationPeriod": {
    "start": "2023-01-01",
    "end": "2023-12-31"
  },
  "supplyArea": "5° Centro de Geoinformação",
  "state": "Minas Gerais",
  "scale": "1:50.000"
}

Query: "mapeamento areas interesse em goias publicado depois de 2020 ordem mais antiga"
{
  "reasoning": "1. 'mapeamento areas interesse' matches 'Mapeamento de Áreas de Interesse da Força'. 2. 'goias' normalizes to 'Goiás'. 3. 'depois de 2020' means from 2020-01-01 to current date. 4. 'ordem mais antiga' with 'publicado' means ascending publication sort.",
  "project": "Mapeamento de Áreas de Interesse da Força",
  "state": "Goiás",
  "publicationPeriod": {
    "start": "2020-01-01",
    "end": "2025-02-03"
  },
  "sortField": "publicationDate",
  "sortDirection": "ASC"
}

Query: "Ortoimagem banda P pol HH de manaus do projeto NGA-BECA"
{
  "reasoning": "1. 'Ortoimagem banda P pol HH' is exact product type match. 2. Project reference matches 'NGA-BECA'. 3. City 'manaus' normalizes to 'Manaus'. 4. No MI/INOM or specific chart name - location is filter only.",
  "productType": "Ortoimagem banda P pol HH",
  "project": "NGA-BECA",
  "city": "Manaus"
}

Query: "MI 2901 de porto alegre com data de criação mais antiga"
{
  "reasoning": "1. Found valid MI code - use as keyword. 2. 'porto alegre' normalizes to 'Porto Alegre'. 3. 'data de criação mais antiga' explicitly indicates creation date ascending sort. 4. Location serves as filter due to MI presence.",
  "keyword": "2901",
  "city": "Porto Alegre",
  "sortField": "creationDate",
  "sortDirection": "ASC"
}

Query: "carta censipam SF-22-Y-D-II"
{
  "reasoning": "1. Found complete INOM code - use as keyword. 2. Product type explicitly mentioned as 'Cartas CENSIPAM'. 3. INOM takes precedence over other potential keywords.",
  "keyword": "SF-22-Y-D-II",
  "productType": "Cartas CENSIPAM"
}"""

_DESCRICOES_PROTOTIPO = {
    "reasoning": "Explain how each parameter was extracted, mentioning which text evidence led to each decision. Always explain presence or absence of keyword, state, and sort choices",
    "keyword": 'Extract map identifiers in order: MI codes (like 2965-2-NE), INOM codes (like SF-22), or chart names. For chart names, look for complete proper names following "carta", "folha", "mapa" - for example "carta Vale do Guaporé" means keyword should be "Vale do Guaporé". Chart names often include geographical features or proper nouns',
    "scale": 'Match scales exactly (1:1.000 to 1:250.000). For relative terms: "maior/detalhada" use 1:1.000, "média" use 1:50.000, "menor/pequena" use 1:250.000. When comparing scales, more detailed (smaller denominator) always takes precedence',
    "productType": "Extract product type with priority: 1) Exact matches of technical terms (MDS, MDT, CIRC). 2) Specific product variations (banda P HH, banda X). 3) General categories. MDS/MDT without RAM suffix implies modelo tridimensional. Temático without type implies Cartas Temáticas Não SCN",
    "state": 'Extract state names even when part of prepositions: "do para" → "Pará", "de rondonia" → "Rondônia". Always normalize with proper capitals and accents',
    "city": 'Extract city names even when part of prepositions: "em cuiaba" → "Cuiabá". Always normalize with proper capitals and accents',
    "supplyArea": 'Convert cgeo variations to standard format. Must include numeric reference: primeiro/1º/1o → "1° Centro de Geoinformação"',
    "project": "Match project names exactly. Technical abbreviations (BECA → NGA-BECA) take precedence over partial matches",
    "publicationPeriod": 'Extract date ranges including relative ones: "semana passada" → 7-13 days ago, "depois de 2020" → from 2020-01-01 to current date, "esse ano" → full current year. Always extract "semana passada" even without explicit publication mention',
    "creationPeriod": 'Use only with explicit creation terms: "criado", "feito", "elaborado", "produzido". Calculate dates same as publication period',
    "sortField": 'Use creationDate when text mentions: "atualização", "primeiro mapeamento", "mais antigas" with creation context, "feito", "elaborado". For ambiguous terms like "mais antigas" without context, default to publicationDate',
    "sortDirection": 'Use ASC for "mais antigas", "primeiro", "antigas". Use DESC for "recentes", "últimas", "atuais"',
    "limit": "Extract numbers between 1-100 when they refer to quantity of results",
}


def _schema_prototipo() -> dict[str, Any]:
    """JSON Schema equivalente ao `ExtractedSearchParams` (Zod) do protótipo."""
    def anulavel(s: dict) -> dict:
        return {"anyOf": [s, {"type": "null"}]}

    periodo = {"type": "object", "properties": {
        "start": {"type": "string", "description": "Data inicial em formato ISO YYYY-MM-DD"},
        "end": {"type": "string", "description": "Data final em formato ISO YYYY-MM-DD"}},
        "required": ["start", "end"], "additionalProperties": False}
    props: dict[str, Any] = {"reasoning": {"type": "string"}}
    for campo in ("keyword", "state", "city"):
        props[campo] = anulavel({"type": "string"})
    for campo, valores in ENUMS_PROTOTIPO.items():
        props[campo] = anulavel({"type": "string", "enum": valores})
    for campo in ("publicationPeriod", "creationPeriod"):
        props[campo] = anulavel(periodo)
    props["limit"] = anulavel({"type": "number", "minimum": 1, "maximum": 100})
    props["sortField"]["default"] = "publicationDate"
    props["sortDirection"]["default"] = "DESC"
    for campo, descricao in _DESCRICOES_PROTOTIPO.items():
        props[campo]["description"] = descricao
    return {"type": "object", "properties": props, "required": ["reasoning"], "additionalProperties": False,
            "description": "Extract search parameters accurately, prioritizing explicit mentions over inferred values"}


SCHEMA_PROTOTIPO = _schema_prototipo()


def montar_prompt_prototipo(hoje: date) -> str:
    return _PROMPT_PROTOTIPO.replace("${today}", hoje.isoformat())


def instrucao_instructor() -> str:
    """Mensagem de sistema que o Instructor acrescenta no modo JSON_SCHEMA (zod-stream, `oai/params.ts`).

    Nesse modo o schema segue em `response_format.schema`, com `type: "json_object"`; o Ollama trata
    esse tipo como modo JSON e não usa o schema. O modelo vê, portanto, só esta descrição geral — os
    enumerados chegam a ele apenas pelas mensagens de erro das novas tentativas.
    """
    return ("Given a user prompt, you will return fully valid JSON based on the following description. "
            "You will return no other prose. You will take into account any descriptions or required parameters "
            "within the schema and return a valid and fully escaped JSON object that matches the schema and those "
            f"instructions.\n\ndescription: {SCHEMA_PROTOTIPO['description']}")


# -- pré-processamento com o dicionário (preprocessor.ts) ---------------------

def _normalizar_comparacao(texto: str) -> str:
    sem_acento = "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                         if not ("̀" <= c <= "ͯ"))
    return re.sub(r"[^A-Za-z0-9_\s]", "", sem_acento).strip()


def _equivalentes(a: str, b: str) -> bool:
    return _normalizar_comparacao(a) == _normalizar_comparacao(b)


def _posicoes(texto: str, termo: str) -> list[int]:
    normal, termo_n = _normalizar_comparacao(texto), _normalizar_comparacao(termo)
    posicoes, atual = [], 0
    while True:
        indice = normal.find(termo_n, atual)
        if indice == -1:
            break
        antes = " " if indice == 0 else normal[indice - 1]
        depois = " " if indice + len(termo_n) >= len(normal) else normal[indice + len(termo_n)]
        if antes.isspace() and depois.isspace():
            # mesma aproximação proporcional de posição do protótipo
            posicoes.append(len(texto[: int(len(texto) * indice / len(normal))]))
        atual = indice + 1
    return posicoes


def preprocessar_consulta(consulta: str) -> str:
    """Porte de `preprocessQuery`: substitui os termos do dicionário, do mais longo ao mais curto."""
    texto = consulta.strip()
    achados: list[tuple[int, int, str]] = []
    for termo, substituto in sorted(COMMON_TERMS.items(), key=lambda kv: -len(kv[0])):
        for inicio in _posicoes(texto, termo):
            fim, trecho = inicio, ""
            while fim <= len(texto):
                trecho = texto[inicio:fim]
                if _equivalentes(trecho, termo):
                    break
                fim += 1
            if _equivalentes(trecho, termo):
                achados.append((inicio, fim, substituto))
    achados.sort(key=lambda a: -a[0])
    finais = [a for i, a in enumerate(achados)
              if not any(j < i and a[0] < b[1] and a[1] > b[0] for j, b in enumerate(achados))]
    for inicio, fim, substituto in finais:
        texto = texto[:inicio] + substituto + texto[fim:]
    return texto


# -- validação do schema Zod ---------------------------------------------------

def validar_zod(obj: Any) -> tuple[dict[str, Any], list[str]]:
    """Validação equivalente ao `ExtractedSearchParams.parse` (campos desconhecidos são descartados)."""
    if not isinstance(obj, dict):
        return {}, ["Expected object"]
    erros: list[str] = []
    saida: dict[str, Any] = {}
    if not isinstance(obj.get("reasoning"), str):
        erros.append("reasoning: Required")
    for campo in ("keyword", "state", "city"):
        v = obj.get(campo)
        if v is None:
            continue
        if isinstance(v, str):
            saida[campo] = v
        else:
            erros.append(f"{campo}: Expected string")
    for campo, valores in ENUMS_PROTOTIPO.items():
        v = obj.get(campo)
        if v is None:
            continue
        if v in valores:
            saida[campo] = v
        else:
            erros.append(f"{campo}: Invalid enum value. Expected {' | '.join(repr(x) for x in valores)}, received {v!r}")
    for campo in ("publicationPeriod", "creationPeriod"):
        v = obj.get(campo)
        if v is None:
            continue
        if isinstance(v, dict) and isinstance(v.get("start"), str) and isinstance(v.get("end"), str):
            saida[campo] = {"start": v["start"], "end": v["end"]}
        else:
            erros.append(f"{campo}: Expected object with string start and end")
    v = obj.get("limit")
    if v is not None:
        if isinstance(v, (int, float)) and not isinstance(v, bool) and 1 <= v <= 100:
            saida["limit"] = int(v) if float(v).is_integer() else v
        else:
            erros.append("limit: Expected number between 1 and 100")
    return saida, erros


# -- validação pós-extração (validator.ts, sem a consulta ao banco) -----------

_MI = [re.compile(p) for p in (r"^\d{1,4}-[1-4]-(NO|NE|SO|SE)$", r"^\d{1,4}-[1-4]$", r"^\d{1,4}$", r"^\d{1,3}$")]
_INOM_BASE = re.compile(r"^[A-Z]{2}-\d{2}-[A-Z]-[A-Z]")
_INOM = [re.compile(p) for p in (r"^[A-Z]{2}-\d{2}-[A-Z]-[A-Z]$", r"^[A-Z]{2}-\d{2}-[A-Z]-[A-Z]-[IVX]{1,6}$",
                                 r"^[A-Z]{2}-\d{2}-[A-Z]-[A-Z]-[IVX]{1,6}-[1-4]$",
                                 r"^[A-Z]{2}-\d{2}-[A-Z]-[A-Z]-[IVX]{1,6}-[1-4]-(NO|NE|SO|SE)$")]


def _validar_keyword(keyword: str) -> str | None:
    k = keyword.strip().upper()
    if any(p.match(k) for p in _MI) or (_INOM_BASE.match(k) and any(p.match(k) for p in _INOM)):
        return k
    if re.match(r"^\d{1,4}(-[1-4](-[NS][EO])?)?$", k) or re.match(r"^[A-Z]{2}-\d{2}", k):
        return None      # parece MI/INOM, mas é inválido: o protótipo descarta
    return keyword


def _periodo_valido(p: Any) -> bool:
    if not isinstance(p, dict) or not p.get("start") or not p.get("end"):
        return False
    if not all(re.match(r"^\d{4}-\d{2}-\d{2}$", str(p[k])) for k in ("start", "end")):
        return False
    try:
        inicio, fim = date.fromisoformat(p["start"]), date.fromisoformat(p["end"])
    except ValueError:
        return False
    return inicio <= fim


def validar_extraidos(params: dict[str, Any]) -> dict[str, Any]:
    """Porte de `validateExtractedParams`, sem os valores padrão de ordenação nem a validação no banco."""
    out: dict[str, Any] = {}
    if isinstance(params.get("keyword"), str):
        k = _validar_keyword(params["keyword"])
        if k is not None:
            out["keyword"] = k
    for campo in ("state", "city"):
        if isinstance(params.get(campo), str):
            out[campo] = params[campo]
    for campo, valores in ENUMS_PROTOTIPO.items():
        if params.get(campo) and params[campo] in valores:
            out[campo] = params[campo]
    lim = params.get("limit")
    if isinstance(lim, (int, float)) and not isinstance(lim, bool) and 0 < lim <= 100:
        out["limit"] = lim
    for campo in ("publicationPeriod", "creationPeriod"):
        if params.get(campo) and _periodo_valido(params[campo]):
            out[campo] = params[campo]
    return out


def limpar_vazios(params: dict[str, Any]) -> dict[str, Any]:
    """Descarta valores vazios ('' , limite 0, limites de período vazios) que o modelo às vezes emite
    para campos ausentes na Saída Estruturada. A aplicação os ignoraria; tratá-los como ausentes
    favorece a linha de base (nas rodadas com Tool Calling, nenhum valor vazio foi emitido)."""
    out: dict[str, Any] = {}
    for campo, valor in params.items():
        if isinstance(valor, dict):
            valor = {k: v for k, v in valor.items() if v not in (None, "")}
            if not valor:
                continue
        elif valor is None or (isinstance(valor, str) and not valor.strip()):
            continue
        elif campo == "limit" and isinstance(valor, (int, float)) and not isinstance(valor, bool) and valor <= 0:
            continue
        out[campo] = valor
    return out


def para_vocabulario_pfc(params: dict[str, Any]) -> dict[str, Any]:
    out = dict(params)
    for campo, tabela in VOCABULARIO_PROTOTIPO.items():
        if campo in out and out[campo] in tabela:
            out[campo] = tabela[out[campo]]
    return out


# -- fallback por expressões regulares (utils.ts) ------------------------------

def _mes_js(d: date, mes_zero: int) -> date:
    """`Date.setMonth` do JavaScript (mês 0-based, com transbordo), preservando o dia quando possível."""
    ano = d.year + mes_zero // 12
    mes = mes_zero % 12 + 1
    ultimo = calendar.monthrange(ano, mes)[1]
    if d.day > ultimo:  # JS transborda para o mês seguinte
        return date(ano, mes, ultimo) + timedelta(days=d.day - ultimo)
    return date(ano, mes, d.day)


def _ultimo_dia(ano: int, mes_zero: int) -> date:
    """`new Date(ano, mes_zero + 1, 0)`: último dia do mês `mes_zero` (0-based, com transbordo)."""
    ano += mes_zero // 12
    mes = mes_zero % 12 + 1
    return date(ano, mes, calendar.monthrange(ano, mes)[1])


def _primeiro_dia(ano: int, mes_zero: int) -> date:
    ano += mes_zero // 12
    return date(ano, mes_zero % 12 + 1, 1)


def _datas_fallback(texto: str, hoje: date) -> dict[str, dict[str, str]]:
    r: dict[str, dict[str, str]] = {}
    ano, mes = hoje.year, hoje.month
    iso = date.isoformat
    if re.search(r"últim[oa]s?\s+6\s+meses|ultim[oa]s?\s+6\s+meses", texto, re.I):
        r["publication"] = {"start": iso(_mes_js(hoje, mes - 6)), "end": iso(hoje)}
    elif re.search(r"últim[oa]s?\s+3\s+meses|ultim[oa]s?\s+3\s+meses", texto, re.I):
        r["publication"] = {"start": iso(_mes_js(hoje, mes - 3)), "end": iso(hoje)}
    elif re.search(r"esse ano|este ano", texto, re.I):
        r["publication"] = {"start": f"{ano}-01-01", "end": f"{ano}-12-31"}
    elif re.search(r"ano passado|último ano|ultim[oa] ano", texto, re.I):
        r["publication"] = {"start": f"{ano - 1}-01-01", "end": f"{ano - 1}-12-31"}
    m = re.search(r"em (\d{4})", texto, re.I)
    if m and 2000 <= int(m.group(1)) <= ano:
        r["publication"] = {"start": f"{m.group(1)}-01-01", "end": f"{m.group(1)}-12-31"}
    m = re.search(r"entre (\d{4})\s+e\s+(\d{4})", texto, re.I)
    if m and int(m.group(1)) <= int(m.group(2)) <= ano:
        r["publication"] = {"start": f"{m.group(1)}-01-01", "end": f"{m.group(2)}-12-31"}
    if re.search(r"últim[oa] trimestre|ultim[oa] trimestre", texto, re.I):
        q = (mes - 1) // 3 * 3
        r["publication"] = {"start": iso(_primeiro_dia(ano, q)), "end": iso(_ultimo_dia(ano, q + 2))}
    m = re.search(r"(primeir[oa]|segund[oa]|terceir[oa]|quart[oa]) trimestre(?: de )?(\d{4})?", texto, re.I)
    if m:
        a = int(m.group(2)) if m.group(2) else ano
        if a <= ano:
            ini = 3 if re.search("segund", m.group(1), re.I) else 6 if re.search("terceir", m.group(1), re.I) \
                else 9 if re.search("quart", m.group(1), re.I) else 0
            r["publication"] = {"start": iso(_primeiro_dia(a, ini)), "end": iso(_ultimo_dia(a, ini + 2))}
    if re.search(r"últim[oa] semestre|ultim[oa] semestre", texto, re.I):
        s = (mes - 1) // 6 * 6
        r["publication"] = {"start": iso(_primeiro_dia(ano, s)), "end": iso(_ultimo_dia(ano, s + 5))}
    m = re.search(r"(primeir[oa]|segund[oa]) semestre(?: de )?(\d{4})?", texto, re.I)
    if m:
        a = int(m.group(2)) if m.group(2) else ano
        if a <= ano:
            ini = 0 if re.search("primeir", m.group(1), re.I) else 6
            r["publication"] = {"start": iso(_primeiro_dia(a, ini)), "end": iso(_ultimo_dia(a, ini + 5))}
    if re.search(r"criad[oa]|elaborad[oa]|produzid[oa]", texto, re.I) and "publication" in r:
        r["creation"] = r.pop("publication")
    return r


def extracao_fallback(texto: str, hoje: date) -> dict[str, Any]:
    """Porte de `fallbackExtraction` (usado só quando a extração pelo modelo falha)."""
    r: dict[str, Any] = {}
    baixo = texto.lower()
    m = re.search(r"1:([0-9.]+)\.?000", texto, re.I)
    escala = f"1:{m.group(1)}.000" if m and f"1:{m.group(1)}.000" in ESCALAS_PROTOTIPO else None
    if escala is None:
        for padrao in (r"\b(\d+)k\b", r"\b(\d+)\.000\b", r"\b(\d+)000\b"):
            m = re.search(padrao, texto, re.I)
            if m and f"1:{m.group(1)}.000" in ESCALAS_PROTOTIPO:
                escala = f"1:{m.group(1)}.000"
                break
    if escala is None:
        if re.search(r"\b(grande|detalhad[ao]|maior)\b", texto, re.I):
            escala = "1:1.000"
        elif re.search(r"\b(media|média)\b", texto, re.I):
            escala = "1:50.000"
        elif re.search(r"\b(pequena|menor)\b", texto, re.I):
            escala = "1:250.000"
    if escala:
        r["scale"] = escala
    tipo = next((t for t in TIPOS_PROTOTIPO if t.lower() in baixo), None)
    if tipo is None:
        if re.search(r"\bmds\b", baixo):
            tipo = "Modelo Tridimensional MDS" if "modelo" in baixo else "MDS - RAM"
        elif re.search(r"\bmdt\b", baixo):
            tipo = "Modelo Tridimensional MDT" if "modelo" in baixo else "MDT - RAM"
        elif "ortoimagem" in baixo or "orto" in baixo:
            if "scn" in baixo:
                tipo = "Ortoimagem SCN"
            elif "radar" in baixo:
                tipo = "Ortoimagem Radar Colorida"
            elif "banda p" in baixo or "polarizacao p" in baixo:
                tipo = ("Ortoimagem banda P pol HH" if "hh" in baixo else
                        "Ortoimagem banda P pol HV" if "hv" in baixo else "Ortoimagem banda P")
            elif ("banda x" in baixo or "polarizacao x" in baixo) and "hh" in baixo:
                tipo = "Ortoimagem banda X pol HH"
            elif "especial" in baixo:
                tipo = "Carta Ortoimagem Especial"
            else:
                tipo = "Ortoimagem"
        else:
            for chave, valor in {"circ": "Tematico CIRC", "cirp": "Tematico CIRP", "cisc": "Tematico CISC",
                                 "cisp": "Tematico CISP", "cmil": "Tematico CMIL", "ctbl": "Tematico CTBL",
                                 "ctp": "Tematico CTP"}.items():
                if chave in baixo:
                    tipo = valor
                    break
    if tipo:
        r["productType"] = tipo
    m = re.search(r"(\d)[ºo°]?\s*cgeo", texto, re.I)
    if m and m.group(1) in "12345":
        r["supplyArea"] = f"{m.group(1)}° Centro de Geoinformação"
    for termo, nome in COMMON_TERMS.items():
        if termo.lower() in baixo and nome in PROJETOS_PROTOTIPO:
            r["project"] = nome
            break
    if re.search(r"recent|nov[oa]|atual|últim[oa]", texto, re.I):
        r["sortField"], r["sortDirection"] = "publicationDate", "DESC"
    elif re.search(r"antig[oa]", texto, re.I):
        r["sortField"], r["sortDirection"] = "publicationDate", "ASC"
    m = re.search(r"\b(\d+)\s*(carta|resultado|item)", texto, re.I)
    if m and 0 < int(m.group(1)) <= 100:
        r["limit"] = int(m.group(1))
    datas = _datas_fallback(texto, hoje)
    if "publication" in datas:
        r["publicationPeriod"] = datas["publication"]
    if "creation" in datas:
        r["creationPeriod"] = datas["creation"]
    return r


# ---------------------------------------------------------------------------
# Tradutor
# ---------------------------------------------------------------------------

def _json(texto: str) -> Any:
    texto = texto.strip()
    if texto.startswith("```"):
        texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto)
    return json.loads(texto)


class TradutorEstruturado:
    """Mesma interface de `agent.Tradutor` (`traduzir(consulta, hoje) -> Traducao`)."""

    def __init__(self, modelo: str, abordagem: str, *, base_url: str = BASE_URL_PADRAO,
                 temperatura: float = 0.0, max_tokens: int = MAX_TOKENS_SAIDA,
                 timeout_s: float = TIMEOUT_S, keep_alive: str = KEEP_ALIVE,
                 desativar_thinking: bool = True):
        if abordagem not in ABORDAGENS:
            raise ValueError(f"abordagem desconhecida: {abordagem!r}")
        self.tag = modelo
        self.abordagem = abordagem
        self.modelo = rotulo_modelo(modelo, abordagem)
        self.base_url = base_url
        self.capacidades = capacidades(modelo, base_url)
        self.thinking_desativado = desativar_thinking and "thinking" in self.capacidades
        self.opcoes = {"temperature": temperatura, "num_predict": max_tokens}
        self.keep_alive = keep_alive
        self.cliente = ollama.Client(host=base_url, timeout=timeout_s)

    def descricao(self) -> dict[str, Any]:
        base = {"abordagem": self.abordagem, "temperature": self.opcoes["temperature"],
                "num_predict": self.opcoes["num_predict"], "ferramenta": False}
        if self.abordagem == "saida_estruturada":
            return {**base, "formato": "modo JSON do Ollama; schema dos parâmetros no prompt",
                    "zero_shot": True, "few_shot": False, "dicionario_normalizacao": False, "fallback": False}
        return {**base, "formato": "modo JSON; descrição do schema no prompt (Instructor JSON_SCHEMA com Ollama)",
                "zero_shot": False, "few_shot": True, "dicionario_normalizacao": True, "fallback": True,
                "novas_tentativas": MAX_NOVAS_TENTATIVAS, "temperatura_do_prototipo": 0.6,
                "ordenacao_padrao_contada": False, "validacao_de_local_no_banco": False}

    def texto_prompt(self, hoje: date) -> str:
        if self.abordagem == "saida_estruturada":
            return montar_prompt_se(hoje)
        return montar_prompt_prototipo(hoje) + "\n\n" + instrucao_instructor()

    def _chat(self, mensagens: list[dict], formato: Any) -> Any:
        kwargs: dict[str, Any] = {"model": self.tag, "messages": mensagens, "format": formato,
                                  "options": self.opcoes, "keep_alive": self.keep_alive}
        if self.thinking_desativado:
            kwargs["think"] = False
        return self.cliente.chat(**kwargs)

    @staticmethod
    def _acumular(r: Traducao, resp: Any) -> None:
        r.tokens_prompt = (r.tokens_prompt or 0) + (getattr(resp, "prompt_eval_count", None) or 0)
        r.tokens_saida = (r.tokens_saida or 0) + (getattr(resp, "eval_count", None) or 0)
        for chave in ("total_duration", "load_duration", "prompt_eval_duration", "eval_duration"):
            v = getattr(resp, chave, None)
            if v is not None:
                nome = chave.replace("_duration", "")
                r.duracoes_ollama_ms[nome] = r.duracoes_ollama_ms.get(nome, 0.0) + v / 1e6

    def traduzir(self, consulta: str, hoje: date) -> Traducao:
        r = Traducao(modelo=self.modelo, hoje=hoje.isoformat(), consulta=consulta)
        # Na Saída Estruturada a aplicação sempre executa a busca: não há como recusar.
        r.chamou_ferramenta = True
        inicio = time.perf_counter()
        try:
            if self.abordagem == "saida_estruturada":
                self._saida_estruturada(r, consulta, hoje)
            else:
                self._prototipo(r, consulta, hoje)
        except Exception as erro:  # noqa: BLE001 — falha vira métrica
            r.classe_erro, r.erro = _classificar_erro(erro)
            if r.classe_erro in ("timeout", "indisponivel"):
                r.chamou_ferramenta = False
                r.predito = None
        r.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
        return r

    def _saida_estruturada(self, r: Traducao, consulta: str, hoje: date) -> None:
        mensagens = [{"role": "system", "content": montar_prompt_se(hoje)}, {"role": "user", "content": consulta}]
        resp = self._chat(mensagens, FORMATO_SE)
        self._acumular(r, resp)
        r.texto_resposta = (resp.message.content or "").strip()
        obj: Any = None
        try:
            obj = _json(r.texto_resposta)
            r.predito = limpar_vazios(schema.ParametrosBusca.model_validate(obj).compactar())
        except (ValueError, ValidationError) as erro:
            # Guarda o que veio (a comparação campo a campo conta o erro); sem objeto, a busca sai sem filtros.
            r.classe_erro, r.erro = "args_invalidos", f"resposta fora do schema: {str(erro)[:200]}"
            r.predito = limpar_vazios(obj) if isinstance(obj, dict) else {}
        r.extras = {"objeto_vazio": not r.predito}

    def _prototipo(self, r: Traducao, consulta: str, hoje: date) -> None:
        pre = preprocessar_consulta(consulta)
        mensagens = [{"role": "system", "content": montar_prompt_prototipo(hoje)},
                     {"role": "user", "content": pre},
                     {"role": "system", "content": instrucao_instructor()}]
        extraidos: dict[str, Any] | None = None
        erros: list[str] = []
        tentativas = 0
        while tentativas <= MAX_NOVAS_TENTATIVAS:
            tentativas += 1
            resp = self._chat(mensagens, "json")
            self._acumular(r, resp)
            texto = (resp.message.content or "").strip()
            r.texto_resposta = texto
            try:
                obj = _json(texto)
            except ValueError as erro:
                obj, erros = None, [f"Invalid JSON: {erro}"]
            else:
                parcial, erros = validar_zod(obj)
                if not erros:
                    extraidos = parcial
                    break
            mensagens += [{"role": "assistant", "content": texto},
                          {"role": "user", "content": "Please correct the function call; errors encountered:\n"
                                                      + "\n".join(erros)}]
        usou_fallback = extraidos is None
        if usou_fallback:
            extraidos = extracao_fallback(pre, hoje)
            r.erro = f"extração falhou após {tentativas} tentativa(s); fallback por regex: {'; '.join(erros)[:200]}"
        validados = validar_extraidos(extraidos)
        r.predito = para_vocabulario_pfc(limpar_vazios(validados))
        r.extras = {"texto_preprocessado": pre, "tentativas": tentativas, "usou_fallback": usou_fallback,
                    "saida_prototipo": validados, "objeto_vazio": not r.predito}

