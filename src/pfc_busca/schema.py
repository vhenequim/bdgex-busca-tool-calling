"""Fonte única do schema de busca: enums, ferramenta `buscar_catalogo` e validação.

Os enums seguem o Apêndice A do PFC (`scripts/generate_dataset_paper.py`), NÃO os do
protótipo em `types/api.ts`. A diferença é
deliberada: o protótipo grafa "SCN Carta Topografica Matricial" (sem acento)
e "MDT - RAM" (hífen) e lista 30 tipos; o PFC recorta 9 tipos com a grafia
das ET-PCDG. Como a recuperação em nível de produto está fora do escopo, a
referência é o texto do PFC.

A descrição de cada parâmetro é o único lugar onde o modelo aprende a
normalizar ("25k" -> "1:25.000"). Não há dicionário nem few-shot em lugar
nenhum do pipeline — isso substitui as 159 entradas de `COMMON_TERMS` do
protótipo.
"""

from __future__ import annotations

import unicodedata
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

# ---------------------------------------------------------------------------
# Enums (Apêndice A)
# ---------------------------------------------------------------------------

ESCALAS = [
    "1:1.000", "1:2.000", "1:5.000", "1:10.000",
    "1:25.000", "1:50.000", "1:100.000", "1:250.000",
]

TIPOS_PRODUTO = [
    "SCN Carta Topográfica Matricial", "SCN Carta Topográfica Vetorial",
    "SCN Carta Ortoimagem", "SCN Carta Ortoimagem Banda P Pol HH",
    "SCN Carta Ortoimagem Banda X Pol HH", "MDT — RAM", "MDS — RAM",
    "CIRC", "Cartas Temáticas Não SCN",
]

CENTROS_GEOINFORMACAO = [
    "1° Centro de Geoinformação", "2° Centro de Geoinformação",
    "3° Centro de Geoinformação", "4° Centro de Geoinformação",
    "5° Centro de Geoinformação",
]

PROJETOS = [
    "Mapeamento Sistemático", "Olimpíadas Rio 2016", "Copa do Mundo 2014",
    "Copa das Confederações", "Base Cartográfica Digital da Bahia",
    "Base Cartográfica Digital de Rondônia", "Base Cartográfica Digital do Amapá",
    "NGA-BECA", "AMAN",
]

CAMPOS_ORDENACAO = ["publicationDate", "creationDate"]
DIRECOES_ORDENACAO = ["ASC", "DESC"]

# Ordem canônica dos 12 campos (tabelas do Cap. 5 seguem esta ordem).
CAMPOS = [
    "keyword", "scale", "productType", "state", "city", "supplyArea",
    "project", "publicationPeriod", "creationPeriod",
    "sortField", "sortDirection", "limit",
]

# Como cada campo é comparado com o gabarito (Cap. 2, "Nota sobre o critério
# de comparação"): enums exigem igualdade exata; strings livres são
# normalizadas; períodos exigem coincidência exata dos limites ISO.
CAMPOS_ENUM = {"scale", "productType", "supplyArea", "project", "sortField", "sortDirection"}
CAMPOS_TEXTO_LIVRE = {"keyword", "state", "city"}
CAMPOS_PERIODO = {"publicationPeriod", "creationPeriod"}
CAMPOS_INTEIRO = {"limit"}

# ---------------------------------------------------------------------------
# Ferramenta exposta ao modelo (formato OpenAI/Ollama)
# ---------------------------------------------------------------------------

NOME_FERRAMENTA = "buscar_catalogo"

FERRAMENTA_BUSCAR_CATALOGO: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": NOME_FERRAMENTA,
        "description": (
            "Busca produtos cartográficos no catálogo do acervo da DSG. "
            "Preencha somente os parâmetros explicitamente presentes na consulta; "
            "não invente valores."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Código MI (ex.: '2965-2-NE'), código INOM (ex.: 'SF-22-Y-D-II-4') ou nome próprio da carta (ex.: 'Passo da Seringueira'). Informar apenas o código, sem o prefixo 'MI '.",
                },
                "scale": {
                    "type": "string",
                    "description": "Escala cartográfica do SCN. Normalizar abreviações: '25k' → '1:25.000'; 'detalhada' → '1:25.000'; 'pequena escala' → '1:250.000'.",
                    "enum": ESCALAS,
                },
                "productType": {
                    "type": "string",
                    "description": "Tipo de produto conforme ET-PCDG. Normalizar: 'topo'/'topográfica' → 'SCN Carta Topográfica Matricial'; 'orto'/'ortoimg' → 'SCN Carta Ortoimagem'; 'mdt' → 'MDT — RAM'.",
                    "enum": TIPOS_PRODUTO,
                },
                "state": {
                    "type": "string",
                    "description": "Nome do estado brasileiro por extenso, com acentos (ex.: 'São Paulo', 'Rio de Janeiro', 'Pará'). Normalizar siglas: 'RJ' → 'Rio de Janeiro'.",
                },
                "city": {
                    "type": "string",
                    "description": "Nome do município por extenso, com acentos.",
                },
                "supplyArea": {
                    "type": "string",
                    "description": "Centro de Geoinformação responsável. Normalizar: '1º CGEO'/'primeiro cgeo' → '1° Centro de Geoinformação'.",
                    "enum": CENTROS_GEOINFORMACAO,
                },
                "project": {
                    "type": "string",
                    "description": "Projeto institucional. Normalizar: 'olimpiadas'/'rio 2016' → 'Olimpíadas Rio 2016'; 'beca' → 'NGA-BECA'.",
                    "enum": PROJETOS,
                },
                "publicationPeriod": {
                    "type": "object",
                    "description": "Intervalo de datas de publicação em ISO 8601, como objeto com as chaves 'start' e 'end' (exatamente esses nomes). Expressões relativas ('esse ano', 'últimos 3 meses') devem ser resolvidas usando a data atual informada no prompt de sistema. Omita a chave que não se aplica.",
                    "properties": {
                        "start": {"type": "string", "description": "AAAA-MM-DD"},
                        "end": {"type": "string", "description": "AAAA-MM-DD"},
                    },
                    "additionalProperties": False,
                },
                "creationPeriod": {
                    "type": "object",
                    "description": "Intervalo de datas de criação em ISO 8601, como objeto com as chaves 'start' e 'end' (exatamente esses nomes; mesmas regras de publicationPeriod).",
                    "properties": {
                        "start": {"type": "string", "description": "AAAA-MM-DD"},
                        "end": {"type": "string", "description": "AAAA-MM-DD"},
                    },
                    "additionalProperties": False,
                },
                "sortField": {"type": "string", "enum": CAMPOS_ORDENACAO},
                "sortDirection": {"type": "string", "enum": DIRECOES_ORDENACAO},
                "limit": {"type": "integer", "description": "Quantidade máxima de resultados (ex.: 'as 5 mais antigas' → 5)."},
            },
            "required": [],
        },
    },
}

# ---------------------------------------------------------------------------
# Validação do que o modelo devolve
# ---------------------------------------------------------------------------


class Periodo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start: str | None = None
    end: str | None = None


class ParametrosBusca(BaseModel):
    """Argumentos de `buscar_catalogo` como o modelo os emite.

    `extra="allow"` de propósito: um campo inventado fora do schema é um
    ERRO DO MODELO que precisa ser contado como falso positivo, não
    silenciado pela validação.
    """

    model_config = ConfigDict(extra="allow")

    keyword: str | None = None
    scale: str | None = None
    productType: str | None = None
    state: str | None = None
    city: str | None = None
    supplyArea: str | None = None
    project: str | None = None
    publicationPeriod: Periodo | None = None
    creationPeriod: Periodo | None = None
    sortField: str | None = None
    sortDirection: str | None = None
    limit: int | None = None

    @field_validator("limit", mode="before")
    @classmethod
    def _limit_inteiro(cls, v):
        # "5" como string ainda é um 5; o que não for número fica como veio
        # para virar erro de tipo na comparação.
        if isinstance(v, str) and v.strip().isdigit():
            return int(v)
        return v

    def compactar(self) -> dict[str, Any]:
        """Dicionário só com os campos preenchidos (o que entra na métrica)."""
        saida: dict[str, Any] = {}
        for chave, valor in self.model_dump(exclude_none=True).items():
            if isinstance(valor, dict):
                valor = {k: v for k, v in valor.items() if v is not None}
                if not valor:
                    continue
            saida[chave] = valor
        return saida


# ---------------------------------------------------------------------------
# Normalização para comparação de strings livres
# ---------------------------------------------------------------------------


def normalizar_texto(texto: str) -> str:
    """lowercase, sem acentos, sem pontuação, espaços colapsados (Cap. 2)."""
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn"
    )
    limpo = "".join(c if c.isalnum() or c.isspace() else " " for c in sem_acento.lower())
    return " ".join(limpo.split())


def valores_validos(campo: str) -> list[str] | None:
    """Enum de um campo, ou None se for texto livre / período / inteiro."""
    return {
        "scale": ESCALAS,
        "productType": TIPOS_PRODUTO,
        "supplyArea": CENTROS_GEOINFORMACAO,
        "project": PROJETOS,
        "sortField": CAMPOS_ORDENACAO,
        "sortDirection": DIRECOES_ORDENACAO,
    }.get(campo)
