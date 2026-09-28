"""Configurações v2 do Tool Calling e da Saída Estruturada (lote de validação, Cap. 5).

Motivação. Na análise de erros do Gemma 4 E4B nas 310 consultas (Tool Calling, v1), os erros
se concentraram em comportamentos que o manual de anotação especifica mas que a definição da
ferramenta não informava ao modelo:

- em 18% das execuções o modelo não chamou a ferramenta e pediu esclarecimento ("preciso
  saber o período exato da semana passada", "qual escala você considera maior que 100k");
- "cartas"/"mapas" sozinhos viraram `productType` (72 falsos positivos);
- períodos relativos saíram só com `start` igual à data atual ("este ano" → start = hoje);
- `1:2000` ficou sem o ponto de milhar; `2901` virou `2901-2-NE` (o código do exemplo da
  descrição); a região virou CGEO ("amazônia legal" → 1º CGEO) e o estado virou projeto
  ("mapas do amapá" → BCD do Amapá); "AM" virou Amapá;
- plural sem número ("as cartas mais antigas") ganhou `limit = 1`.

A v2 muda só a especificação, não o mecanismo:

1. Descrições dos parâmetros que explicitam as convenções do manual de anotação (quando
   preencher cada campo, a forma canônica, o que não deduzir), sem códigos de exemplo que
   possam ser copiados e com as siglas das 27 UFs.
2. Tool Calling v2: uma segunda ferramenta, `recusar_consulta(motivo)`, para a recusa
   explícita; o prompt manda chamar exatamente uma das duas e nunca pedir esclarecimento.
3. Saída Estruturada v2: as mesmas descrições, mais o campo `fora_do_escopo` no schema
   (a recusa passa a ser representável também na Saída Estruturada) e a mesma regra de não
   pedir esclarecimento.

As duas v2 recebem exatamente a mesma especificação; a comparação entre elas continua
isolando o mecanismo. O desenho da v2 usou as 310 consultas (análise de erros acima); por
isso o número da v2 nas 310 é otimista (dentro da amostra) e a medida que vale é a do lote
de validação, que o desenho da v2 não viu.

Escopo: configuração de AVALIAÇÃO. O pipeline da demonstração (`pipeline.py`) continua com a
v1, que é a configuração descrita no Cap. 4.
"""

from __future__ import annotations

import copy
import json
import time
from datetime import date
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import ValidationError

from pfc_busca import agent, agent_estruturado, schema
from pfc_busca.agent import Traducao, _classificar_erro
from pfc_busca.prompts import _DIAS_DA_SEMANA

# ---------------------------------------------------------------------------
# Especificação dos parâmetros (comum às duas v2)
# ---------------------------------------------------------------------------

SIGLAS_UF = ("AC Acre, AL Alagoas, AP Amapá, AM Amazonas, BA Bahia, CE Ceará, DF Distrito Federal, "
             "ES Espírito Santo, GO Goiás, MA Maranhão, MT Mato Grosso, MS Mato Grosso do Sul, MG Minas Gerais, "
             "PA Pará, PB Paraíba, PR Paraná, PE Pernambuco, PI Piauí, RJ Rio de Janeiro, RN Rio Grande do Norte, "
             "RS Rio Grande do Sul, RO Rondônia, RR Roraima, SC Santa Catarina, SP São Paulo, SE Sergipe, "
             "TO Tocantins")

DESCRICOES_V2: dict[str, str] = {
    "keyword": (
        "Código MI, código INOM ou nome próprio da carta/folha citado na consulta. Copie o código exatamente "
        "como aparece, sem acrescentar nem remover sufixos e sem o prefixo ('MI', 'INOM', 'folha', 'carta'). "
        "INOM em maiúsculas e com hífens (grafia compacta 'sf22yd' → 'SF-22-Y-D'). Nome próprio só quando vier "
        "depois de 'carta' ou 'folha'. Se houver dois códigos, informe o primeiro. Palavras genéricas ('carta', "
        "'folha', 'mapa') nunca são keyword."
    ),
    "scale": (
        "Escala cartográfica do SCN citada na consulta, na grafia exata do enumerado, com ponto de milhar: "
        "'1:2000' → '1:2.000'; '1:25000', '25k' ou '25 mil' → '1:25.000'; '100k', '100 mil' ou 'cem mil' → "
        "'1:100.000'; 'detalhada' → '1:25.000'; 'pequena escala' → '1:250.000'. Se a consulta citar duas escalas, "
        "informe a primeira. Só preencha se a consulta falar de escala."
    ),
    "productType": (
        "Tipo de produto conforme ET-PCDG, só se a consulta nomear o tipo: 'topo'/'topográfica(s)' → 'SCN Carta "
        "Topográfica Matricial'; 'vetorial(is)' → 'SCN Carta Topográfica Vetorial'; 'orto'/'ortoimg'/'ortoimagem' → "
        "'SCN Carta Ortoimagem'; ortoimagem 'banda P' ou 'banda X' → a variante correspondente; 'mdt'/'modelo "
        "digital de terreno' → 'MDT — RAM'; 'mds'/'modelo digital de superfície' → 'MDS — RAM'; 'temática(s)' → "
        "'Cartas Temáticas Não SCN'. As palavras 'cartas', 'mapas', 'folhas' e 'produtos' sozinhas não definem "
        "tipo: nesse caso omita o parâmetro."
    ),
    "state": (
        "Estado brasileiro citado na consulta, por extenso e com acentos. Siglas: " + SIGLAS_UF + ". Não deduza o "
        "estado a partir do município; regiões ('Nordeste', 'Sul', 'Amazônia Legal') não são estados."
    ),
    "city": (
        "Município brasileiro citado na consulta, por extenso e com acentos. Não deduza o município a partir do "
        "estado nem o preencha com o nome de uma região."
    ),
    "supplyArea": (
        "Centro de Geoinformação (CGEO) citado na consulta: '1º CGEO', '1o cgeo', 'primeiro cgeo' ou '1º Centro "
        "de Geoinformação' → '1° Centro de Geoinformação' (idem do 2º ao 5º). Só preencha se a consulta citar o "
        "CGEO; não o deduza da região nem do estado."
    ),
    "project": (
        "Projeto institucional citado na consulta: 'olimpiadas'/'rio 2016' → 'Olimpíadas Rio 2016'; 'beca' → "
        "'NGA-BECA'; 'BCD de Rondônia' → 'Base Cartográfica Digital de Rondônia'. Só preencha se a consulta citar "
        "o projeto; o nome de um estado ou a palavra 'mapeamento' sozinhos não indicam projeto."
    ),
    "publicationPeriod": (
        "Intervalo de datas de PUBLICAÇÃO em ISO 8601, objeto com as chaves 'start' e 'end' (exatamente esses "
        "nomes). Use quando a expressão de tempo vier com verbo de publicação ('publicada', 'lançada') ou sem "
        "verbo. Dê o intervalo inteiro que a expressão cobre, resolvido com a data atual: um ano → de 1º de janeiro "
        "a 31 de dezembro desse ano; um mês → do primeiro ao último dia do mês; 'últimos N meses/anos/dias' → de N "
        "meses/anos/dias antes da data atual até a data atual; 'desde AAAA' → start AAAA-01-01 e end a data atual; "
        "'antes de AAAA' → só end, no último dia do ano anterior. Omita a chave que não se aplica."
    ),
    "creationPeriod": (
        "Intervalo de datas de CRIAÇÃO em ISO 8601 (mesmo formato e mesmas regras de publicationPeriod). Use "
        "quando a expressão de tempo vier com verbo de criação ('criada', 'feita', 'elaborada', 'produzida')."
    ),
    "sortField": (
        "Campo de ordenação, só quando a consulta pedir ordem ou posição ('mais recente', 'mais antiga', "
        "'primeiras', 'últimas', 'ordem cronológica'). 'creationDate' se a pista for de criação ou atualização "
        "('criada mais recentemente', 'última atualização', 'primeiro mapeamento feito'); 'publicationDate' nos "
        "demais casos."
    ),
    "sortDirection": (
        "Direção da ordenação, sempre junto com sortField: 'DESC' para 'mais recente(s)', 'último(s)', 'mais "
        "nova(s)'; 'ASC' para 'mais antiga(s)', 'primeiro(s)', 'ordem cronológica'."
    ),
    "limit": (
        "Quantidade de resultados, só quando a consulta der um número ('as 5 mais antigas' → 5; 'três cartas' → 3) "
        "ou pedir um único resultado no singular ('a carta mais recente' → 1). Plural sem número ('as mais "
        "recentes') → omita."
    ),
}


def _ferramenta_busca_v2() -> dict[str, Any]:
    f = copy.deepcopy(schema.FERRAMENTA_BUSCAR_CATALOGO)
    f["function"]["description"] = (
        "Busca produtos cartográficos do território brasileiro no catálogo do acervo da DSG. Preencha somente os "
        "parâmetros explicitamente presentes na consulta; não invente valores nem deduza um parâmetro de outro. "
        "Uma consulta sem nenhum parâmetro reconhecível ainda é uma busca: chame com os parâmetros vazios."
    )
    for campo, texto in DESCRICOES_V2.items():
        f["function"]["parameters"]["properties"][campo]["description"] = texto
    return f


FERRAMENTA_BUSCAR_CATALOGO_V2 = _ferramenta_busca_v2()
PARAMETROS_V2 = FERRAMENTA_BUSCAR_CATALOGO_V2["function"]["parameters"]

NOME_RECUSA = "recusar_consulta"
FERRAMENTA_RECUSAR: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": NOME_RECUSA,
        "description": (
            "Recusa uma consulta que não pede produtos cartográficos do acervo: outro assunto, lugar fora do Brasil "
            "ou fictício, pedido para produzir ou editar um mapa, conversa sem intenção de busca. Não use para "
            "consultas vagas sobre o acervo: essas vão para buscar_catalogo."
        ),
        "parameters": {
            "type": "object",
            "properties": {"motivo": {"type": "string", "description": (
                "Uma frase, em português, dirigida ao usuário, explicando por que a consulta está fora do escopo "
                "do catálogo.")}},
            "required": ["motivo"],
        },
    },
}

_CABECALHO = """Você é o assistente de busca do catálogo de produtos cartográficos do acervo da Diretoria de Serviço Geográfico (DSG).

A data atual é {data_iso} ({dia_semana}, {data_br}). Use-a para resolver qualquer expressão de tempo relativo presente na consulta."""

_REGRAS_COMUNS = """Nunca peça esclarecimento nem confirmação: se a consulta pedir produtos do acervo, faça a busca com os parâmetros que ela permite preencher, mesmo que seja um só ou nenhum; expressões de tempo relativo você mesmo resolve com a data atual.
{n}. Preencha somente os parâmetros explicitamente presentes na consulta. Não invente valores, não complete campos por suposição, não deduza um parâmetro de outro (o estado a partir do município, o CGEO a partir da região, o projeto a partir do estado), não acrescente ordenação ou limite que não foram pedidos e não use valores de exemplo.
{m}. Converta cada valor para a forma canônica descrita na definição do parâmetro correspondente."""

_MODELO_TC_V2 = _CABECALHO + """

Você tem duas ferramentas e deve chamar exatamente uma delas:
- buscar_catalogo: quando a consulta pedir produtos cartográficos do acervo (cartas, folhas, mapas, ortoimagens, modelos digitais etc.) do território brasileiro, mesmo que de forma vaga;
- recusar_consulta: quando a consulta não tratar de produtos cartográficos do acervo (outro assunto, lugar fora do Brasil ou fictício, pedido para produzir ou editar um mapa, conversa sem intenção de busca).

Regras:
1. """ + _REGRAS_COMUNS.format(n=2, m=3)

_MODELO_SE_V2 = _CABECALHO + """

Instruções:
1. Responda somente com um objeto JSON que siga o schema abaixo. Omita os parâmetros ausentes.
2. Se a consulta não tratar de produtos cartográficos do acervo do território brasileiro (outro assunto, lugar fora do Brasil ou fictício, pedido para produzir ou editar um mapa, conversa sem intenção de busca), responda {{"fora_do_escopo": true}} e nada mais.
3. """ + _REGRAS_COMUNS.format(n=4, m=5) + """

Schema dos parâmetros (JSON Schema):
{schema_json}"""

CAMPO_FORA_DO_ESCOPO = "fora_do_escopo"
PARAMETROS_SE_V2: dict[str, Any] = copy.deepcopy(PARAMETROS_V2)
PARAMETROS_SE_V2["properties"] = {
    CAMPO_FORA_DO_ESCOPO: {"type": "boolean", "description": (
        "true somente se a consulta não tratar de produtos cartográficos do acervo; nesse caso não preencha mais "
        "nada. Consultas vagas sobre o acervo não são fora do escopo.")},
    **PARAMETROS_SE_V2["properties"],
}


def _datas(hoje: date) -> dict[str, str]:
    return {"data_iso": hoje.isoformat(), "dia_semana": _DIAS_DA_SEMANA[hoje.weekday()],
            "data_br": hoje.strftime("%d/%m/%Y")}


def montar_prompt_tc_v2(hoje: date) -> str:
    return _MODELO_TC_V2.format(**_datas(hoje))


def montar_prompt_se_v2(hoje: date) -> str:
    return _MODELO_SE_V2.format(**_datas(hoje), schema_json=json.dumps(PARAMETROS_SE_V2, ensure_ascii=False, indent=2))


def texto_hash(abordagem: str) -> str:
    """Texto cujo SHA-256 identifica prompt + especificação de cada v2 (manifesto e conferência)."""
    if abordagem == "tool_calling_v2":
        return _MODELO_TC_V2 + json.dumps([FERRAMENTA_BUSCAR_CATALOGO_V2, FERRAMENTA_RECUSAR],
                                          ensure_ascii=False, sort_keys=True)
    return _MODELO_SE_V2 + json.dumps(PARAMETROS_SE_V2, ensure_ascii=False, sort_keys=True)


# ---------------------------------------------------------------------------
# Tool Calling v2
# ---------------------------------------------------------------------------

class TradutorV2(agent.Tradutor):
    """`agent.Tradutor` com as duas ferramentas e o prompt v2.

    Chamar `recusar_consulta` (sem `buscar_catalogo`) conta como não chamar a ferramenta de
    busca — é a recusa, pontuada exatamente como a recusa em texto da v1.
    """

    abordagem = "tool_calling_v2"

    def __init__(self, modelo: str, **kwargs):
        super().__init__(modelo, **kwargs)
        self.llm_com_ferramenta = self.llm.bind_tools([FERRAMENTA_BUSCAR_CATALOGO_V2, FERRAMENTA_RECUSAR])

    def descricao(self) -> dict[str, Any]:
        return {"abordagem": self.abordagem, "temperature": 0, "num_predict": agent.MAX_TOKENS_SAIDA,
                "ferramentas": [schema.NOME_FERRAMENTA, NOME_RECUSA], "zero_shot": True, "few_shot": False,
                "dicionario_normalizacao": False, "descricoes": "v2 (convenções do manual explícitas)",
                "pedir_esclarecimento": "proibido pelo prompt"}

    def traduzir(self, consulta: str, hoje: date) -> Traducao:
        resultado = Traducao(modelo=self.modelo, hoje=hoje.isoformat(), consulta=consulta)
        mensagens = [SystemMessage(content=montar_prompt_tc_v2(hoje)), HumanMessage(content=consulta)]
        inicio = time.perf_counter()
        try:
            resposta: AIMessage = self.llm_com_ferramenta.invoke(mensagens)
        except Exception as erro:  # noqa: BLE001
            resultado.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
            resultado.classe_erro, resultado.erro = _classificar_erro(erro)
            return resultado
        resultado.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
        self._preencher(resultado, resposta)
        return resultado

    def _preencher(self, r: Traducao, resposta: AIMessage) -> None:
        super()._preencher(r, resposta)
        nomes = [c.get("name") for c in r.tool_calls]
        recusa = next((c for c in r.tool_calls if c.get("name") == NOME_RECUSA), None)
        r.extras = {"recusou": False, "respondeu_em_texto": not r.chamou_ferramenta}
        if recusa is not None and schema.NOME_FERRAMENTA not in nomes:
            motivo = (recusa.get("args") or {}).get("motivo") if isinstance(recusa.get("args"), dict) else None
            r.chamou_ferramenta = False
            r.predito = None
            r.classe_erro = r.erro = None
            r.texto_resposta = r.texto_resposta or str(motivo or "")
            r.extras.update(recusou=True, motivo=motivo)
        elif recusa is not None:
            r.extras["buscou_e_recusou"] = True
            if r.classe_erro == "ferramenta_inexistente":
                r.classe_erro = r.erro = None


# ---------------------------------------------------------------------------
# Saída Estruturada v2
# ---------------------------------------------------------------------------

class TradutorEstruturadoV2(agent_estruturado.TradutorEstruturado):
    """Saída Estruturada com a especificação v2 e o campo `fora_do_escopo`."""

    def __init__(self, modelo: str, **kwargs):
        super().__init__(modelo, "saida_estruturada", **kwargs)
        self.abordagem = "saida_estruturada_v2"
        self.modelo = f"{modelo} [saida-estruturada-v2]"

    def descricao(self) -> dict[str, Any]:
        return {**super().descricao(), "abordagem": self.abordagem, "descricoes": "v2 (convenções do manual explícitas)",
                "recusa": f"campo {CAMPO_FORA_DO_ESCOPO} no schema", "pedir_esclarecimento": "proibido pelo prompt"}

    def texto_prompt(self, hoje: date) -> str:
        return montar_prompt_se_v2(hoje)

    def traduzir(self, consulta: str, hoje: date) -> Traducao:
        r = Traducao(modelo=self.modelo, hoje=hoje.isoformat(), consulta=consulta)
        r.chamou_ferramenta = True
        inicio = time.perf_counter()
        try:
            self._saida_estruturada_v2(r, consulta, hoje)
        except Exception as erro:  # noqa: BLE001
            r.classe_erro, r.erro = _classificar_erro(erro)
            if r.classe_erro in ("timeout", "indisponivel"):
                r.chamou_ferramenta = False
                r.predito = None
        r.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
        return r

    def _saida_estruturada_v2(self, r: Traducao, consulta: str, hoje: date) -> None:
        mensagens = [{"role": "system", "content": montar_prompt_se_v2(hoje)}, {"role": "user", "content": consulta}]
        resp = self._chat(mensagens, agent_estruturado.FORMATO_SE)
        self._acumular(r, resp)
        r.texto_resposta = (resp.message.content or "").strip()
        obj: Any = None
        try:
            obj = agent_estruturado._json(r.texto_resposta)
        except ValueError as erro:
            r.classe_erro, r.erro = "args_invalidos", f"resposta fora do schema: {str(erro)[:200]}"
            r.predito = {}
            r.extras = {"recusou": False, "objeto_vazio": True}
            return
        fora = isinstance(obj, dict) and obj.get(CAMPO_FORA_DO_ESCOPO) is True
        if fora:
            outros = {k: v for k, v in obj.items() if k != CAMPO_FORA_DO_ESCOPO}
            r.chamou_ferramenta = False
            r.predito = None
            r.extras = {"recusou": True, "parametros_junto_da_recusa": agent_estruturado.limpar_vazios(outros)}
            return
        params = {k: v for k, v in obj.items() if k != CAMPO_FORA_DO_ESCOPO} if isinstance(obj, dict) else obj
        try:
            r.predito = agent_estruturado.limpar_vazios(schema.ParametrosBusca.model_validate(params).compactar())
        except (ValueError, ValidationError) as erro:
            r.classe_erro, r.erro = "args_invalidos", f"resposta fora do schema: {str(erro)[:200]}"
            r.predito = agent_estruturado.limpar_vazios(params) if isinstance(params, dict) else {}
        r.extras = {"recusou": False, "objeto_vazio": not r.predito}


ABORDAGENS_V2 = ("tool_calling_v2", "saida_estruturada_v2")


def criar(modelo: str, abordagem: str, base_url: str = agent.BASE_URL_PADRAO):
    if abordagem == "tool_calling_v2":
        return TradutorV2(modelo, base_url=base_url)
    if abordagem == "saida_estruturada_v2":
        return TradutorEstruturadoV2(modelo, base_url=base_url)
    raise ValueError(f"abordagem v2 desconhecida: {abordagem!r}")
