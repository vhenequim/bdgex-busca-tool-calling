"""Configurações v3: Tool Calling com ferramentas auxiliares e validação com retorno, em degraus.

Desenho (docs/v3.md). Todas partem da v2 (`pfc_busca.v2`) com as descrições corrigidas dos efeitos
colaterais medidos no lote 1 (siglas devolvidas como valor, prefixo em códigos, limit em plural). Cada
degrau acrescenta uma peça ao anterior:

    tool_calling_v3d   descrições v3 (uma chamada: buscar_catalogo ou recusar_consulta, como a v2)
    tool_calling_v3a   + ferramentas auxiliares (identificar_nome, normalizar_codigo, normalizar_escala,
                       resolver_periodo) e pedir_esclarecimento com usuário simulado, num laço de chamadas
    tool_calling_v3    + retorno: buscar_catalogo confere os parâmetros antes de executar e devolve erros e
                       avisos; a recusa de uma consulta com critério do catálogo é devolvida uma vez
    saida_estruturada_v3   CONTROLE: Saída Estruturada com as descrições v3 e o MESMO retorno (validação e
                       recusa contestada) como nova tentativa, sem as ferramentas auxiliares no meio da resposta.

A diferença entre tool_calling_v3 e saida_estruturada_v3 mede o que o mecanismo acrescenta; a diferença
entre degraus mede o que cada peça acrescenta.

Usuário simulado: quando o modelo chama pedir_esclarecimento (ou escreve uma pergunta como texto), a
resposta é sempre a mesma — "não tenho outros detalhes; pode buscar com o que eu disse" —, e o número de
perguntas é registrado.

Uma variante com orientações escritas a partir dos erros de desenvolvimento (markdowns com frontmatter)
foi testada no desenvolvimento e descartada: não mudou o resultado (docs/v3_desenvolvimento.md,
experimentos/orientacoes/).
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import time
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from pydantic import ValidationError

from pfc_busca import agent, agent_estruturado, ferramentas, schema, v2
from pfc_busca.agent import Traducao, _classificar_erro

MAX_CHAMADAS_MODELO = 6
MAX_TENTATIVAS_BUSCA = 3
MAX_PERGUNTAS = 2
MAX_NOVAS_TENTATIVAS_SE = 2
# Contexto do modelo na v3. O padrão do Ollama (4.096 tokens) é suficiente para a v1 e a v2 (1,3 a 2,6 mil tokens
# de prompt), mas a v3 manda ~3,3 mil tokens só de prompt e ferramentas por chamada, mais os resultados das
# ferramentas; perto do limite, o Ollama corta o começo do prompt — o prompt de sistema.
NUM_CTX_V3 = 8192
RESPOSTA_USUARIO = ("Resposta do usuário: não tenho outros detalhes além do que escrevi; pode buscar com o que eu "
                    "disse.")
# como o modelo confirma uma recusa contestada (ferramentas.mensagem_recusa)
CONFIRMAR_RECUSA_TC = "chame recusar_consulta de novo para confirmar a recusa."
CONFIRMAR_RECUSA_SE = 'responda de novo só com {"fora_do_escopo": true} para confirmar a recusa.'

# ---------------------------------------------------------------------------
# Especificação v3: v2 com os efeitos colaterais corrigidos
# ---------------------------------------------------------------------------

DESCRICOES_V3 = dict(v2.DESCRICOES_V2)
DESCRICOES_V3.update({
    "keyword": (
        "Código MI, código INOM ou nome próprio da carta/folha citado na consulta. Só o código, como está escrito, "
        "sem o prefixo: 'MI 1234-5' → '1234-5'; 'folha MI-1234-5-NO' → '1234-5-NO'; INOM em maiúsculas e com hífens "
        "('sb20xa' → 'SB-20-X-A'). Não acrescente nem remova sufixos. Nome próprio só quando vier logo depois de "
        "'carta' ou 'folha', copiado como está. Se houver dois códigos, informe o primeiro. Palavras genéricas "
        "('carta', 'folha', 'mapa') e tipos de produto nunca são keyword."
    ),
    "state": (
        "Estado brasileiro citado na consulta, sempre pelo NOME por extenso e com acentos ('Amazonas', 'Pará', "
        "'Distrito Federal'), nunca a sigla: converta siglas para o nome ('MT' → 'Mato Grosso'). Não deduza o estado "
        "a partir do município, da folha ou do nome de um projeto ('BCD da Bahia' é projeto); regiões ('Nordeste', "
        "'Sul', 'Amazônia Legal') não são estados."
    ),
    "city": (
        "Município brasileiro citado na consulta, com o nome inteiro e acentos, mesmo quando o nome contém o de um "
        "estado ('Santa Rosa do Piauí', 'Aparecida de Goiânia'). Não use para estado, região ou nome de carta."
    ),
    "limit": (
        "Quantidade de resultados, só quando a consulta disser um número ('as 5 mais antigas' → 5; 'três cartas' "
        "→ 3) ou pedir UM resultado no singular ('a carta mais recente' → 1). Plural sem número ('as mais "
        "recentes', 'as últimas cartas') → não preencha."
    ),
    "productType": v2.DESCRICOES_V2["productType"] + " Na dúvida, não preencha.",
})


def _ferramenta_busca_v3(com_validacao: bool) -> dict[str, Any]:
    f = copy.deepcopy(schema.FERRAMENTA_BUSCAR_CATALOGO)
    f["function"]["description"] = (
        "Busca produtos cartográficos do território brasileiro no catálogo do acervo da DSG. Preencha somente os "
        "parâmetros explicitamente presentes na consulta; não invente valores nem deduza um parâmetro de outro. "
        "Uma consulta sem nenhum parâmetro reconhecível ainda é uma busca: chame com os parâmetros vazios."
        + (" Antes de executar, a ferramenta confere os parâmetros e devolve erros ou avisos para você corrigir."
           if com_validacao else "")
    )
    for campo, texto in DESCRICOES_V3.items():
        f["function"]["parameters"]["properties"][campo]["description"] = texto
    return f


def _funcao(nome: str, descricao: str, parametros: dict[str, str], obrigatorios: list[str]) -> dict[str, Any]:
    return {"type": "function", "function": {
        "name": nome, "description": descricao,
        "parameters": {"type": "object",
                       "properties": {k: {"type": "string", "description": d} for k, d in parametros.items()},
                       "required": obrigatorios}}}


BUSCAR_V3 = _ferramenta_busca_v3(com_validacao=False)
BUSCAR_V3_VALIDADA = _ferramenta_busca_v3(com_validacao=True)
PEDIR = _funcao("pedir_esclarecimento",
                "Faz UMA pergunta ao usuário. Use só quando a consulta pedir produtos do acervo sem NENHUM critério "
                "(nem lugar, escala, tipo, código, data, projeto ou CGEO). Com qualquer critério, busque.",
                {"pergunta": "A pergunta, em uma frase, em português."}, ["pergunta"])
IDENTIFICAR = _funcao("identificar_nome",
                      "Diz se um nome citado na consulta é estado (inclusive sigla), município (com a UF), folha do "
                      "acervo ou região, e dá a forma canônica. Use para cada lugar ou nome de carta da consulta.",
                      {"nome": "O trecho exatamente como está na consulta (ex.: 'AM', 'Campinas, SP', "
                               "'santa rosa do piaui', 'Rio das Pedras')."}, ["nome"])
CODIGO = _funcao("normalizar_codigo", "Forma canônica de um código MI ou INOM e se ele consta no acervo.",
                 {"codigo": "O código como está na consulta (ex.: 'MI 1234-5', 'sb20xa')."}, ["codigo"])
ESCALA = _funcao("normalizar_escala", "Escala canônica do SCN para uma menção de escala ('25k', '1:50000', "
                 "'grande escala').", {"texto": "A menção à escala como está na consulta."}, ["texto"])
PERIODO = _funcao("resolver_periodo", "Intervalo ISO (start/end) de uma expressão de tempo, resolvido com a data "
                  "atual pelas regras do catálogo.", {"expressao": "A expressão de tempo como está na consulta "
                                                                   "(ex.: 'no ano passado', 'últimos 3 meses')."},
                  ["expressao"])
AUXILIARES = {"identificar_nome": IDENTIFICAR, "normalizar_codigo": CODIGO, "normalizar_escala": ESCALA,
              "resolver_periodo": PERIODO}

VARIANTES = {
    # abordagem: (ferramentas auxiliares e laço de chamadas, retorno: validação e recusa contestada)
    "tool_calling_v3d": (False, False),
    "tool_calling_v3a": (True, False),
    "tool_calling_v3": (True, True),
}
ABORDAGENS_V3 = tuple(VARIANTES) + ("saida_estruturada_v3",)
PREFIXOS = {"tool_calling_v3d": "tc3d-", "tool_calling_v3a": "tc3a-", "tool_calling_v3": "tc3-",
            "saida_estruturada_v3": "se3-"}

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_REGRAS_V3 = """Regras:
1. Preencha somente os parâmetros explicitamente presentes na consulta. Não invente valores, não deduza um parâmetro de outro (o estado a partir do município, o CGEO a partir da região, o projeto a partir do estado) e não acrescente ordenação, limite ou tipo de produto que não foram pedidos.
2. Converta cada valor para a forma canônica descrita na definição do parâmetro."""

_TC_SIMPLES = v2._CABECALHO + """

Você tem duas ferramentas e deve chamar exatamente uma delas:
- buscar_catalogo: quando a consulta pedir produtos cartográficos do acervo do território brasileiro, mesmo que de forma vaga (nunca peça esclarecimento: busque com os parâmetros que a consulta permite preencher, mesmo que seja um só ou nenhum);
- recusar_consulta: quando a consulta não tratar de produtos cartográficos do acervo (outro assunto, lugar fora do Brasil ou fictício, pedido para produzir ou editar um mapa, conversa sem intenção de busca).

""" + _REGRAS_V3

_TC_FERRAMENTAS = v2._CABECALHO + """

Ferramentas:
- identificar_nome, normalizar_codigo, normalizar_escala e resolver_periodo são auxiliares: antes de buscar, confirme com elas a forma canônica de cada lugar, nome de carta, código, escala e expressão de tempo citados na consulta (pode chamar várias de uma vez). Para expressão de tempo, chame resolver_periodo e copie as datas que ela devolver, sem fazer a conta de cabeça.
- buscar_catalogo faz a busca.{linha_validacao}
- pedir_esclarecimento: só quando a consulta pedir produtos do acervo sem NENHUM critério (nem lugar, escala, tipo, código, data, projeto ou CGEO). Com qualquer critério, busque.
- recusar_consulta: quando a consulta não tratar de produtos cartográficos do acervo (outro assunto, lugar fora do Brasil ou fictício, pedido para produzir ou editar um mapa, conversa sem intenção de busca). Nome de lugar que você não reconhece não é motivo de recusa: confira com identificar_nome.
Termine sempre com buscar_catalogo, pedir_esclarecimento ou recusar_consulta.

""" + _REGRAS_V3

_SE_V3 = v2._CABECALHO + """

Instruções:
1. Responda somente com um objeto JSON que siga o schema abaixo. Omita os parâmetros ausentes.
2. Se a consulta não tratar de produtos cartográficos do acervo do território brasileiro (outro assunto, lugar fora do Brasil ou fictício, pedido para produzir ou editar um mapa, conversa sem intenção de busca), responda {{"fora_do_escopo": true}} e nada mais. Uma consulta vaga sobre o acervo, ou só com uma região, não é fora do escopo: responda com os parâmetros que ela permite preencher, mesmo que nenhum.
3. """ + _REGRAS_V3.replace("Regras:\n1. ", "").replace("\n2. ", "\n4. ") + """

Schema dos parâmetros (JSON Schema):
{schema_json}"""

PARAMETROS_SE_V3: dict[str, Any] = copy.deepcopy(BUSCAR_V3["function"]["parameters"])
PARAMETROS_SE_V3["properties"] = {v2.CAMPO_FORA_DO_ESCOPO: v2.PARAMETROS_SE_V2["properties"][v2.CAMPO_FORA_DO_ESCOPO],
                                  **PARAMETROS_SE_V3["properties"]}


def _datas(hoje: date) -> dict[str, str]:
    return v2._datas(hoje)


LINHA_VALIDACAO = " Ela confere os parâmetros antes de executar; se devolver erros ou avisos, corrija e chame de novo."


def prompt_tc(abordagem: str, hoje: date) -> str:
    auxiliares, retorno = VARIANTES[abordagem]
    if not auxiliares:
        return _TC_SIMPLES.format(**_datas(hoje))
    return _TC_FERRAMENTAS.format(**_datas(hoje), linha_validacao=LINHA_VALIDACAO if retorno else "")


def prompt_se(hoje: date) -> str:
    return _SE_V3.format(**_datas(hoje), schema_json=json.dumps(PARAMETROS_SE_V3, ensure_ascii=False, indent=2))


def _sha_arquivo(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "ausente"


def texto_hash(abordagem: str) -> str:
    """Tudo o que define a configuração: prompts, ferramentas e o código/dados das ferramentas."""
    partes = [_TC_SIMPLES, _TC_FERRAMENTAS, LINHA_VALIDACAO, _SE_V3, RESPOSTA_USUARIO,
              json.dumps([BUSCAR_V3, BUSCAR_V3_VALIDADA, PEDIR, *AUXILIARES.values(), v2.FERRAMENTA_RECUSAR],
                         ensure_ascii=False, sort_keys=True),
              _sha_arquivo(Path(ferramentas.__file__)), _sha_arquivo(Path(__file__)),
              _sha_arquivo(ferramentas.DADOS / "municipios_ibge.json"),
              _sha_arquivo(ferramentas.DADOS / "indice_folhas.json"), abordagem]
    return "\n".join(partes)


def ferramentas_da(abordagem: str) -> list[dict[str, Any]]:
    if abordagem == "saida_estruturada_v3":
        return [BUSCAR_V3_VALIDADA]
    auxiliares, retorno = VARIANTES[abordagem]
    if not auxiliares:
        return [BUSCAR_V3, v2.FERRAMENTA_RECUSAR]
    return [*AUXILIARES.values(), BUSCAR_V3_VALIDADA if retorno else BUSCAR_V3, PEDIR, v2.FERRAMENTA_RECUSAR]


# ---------------------------------------------------------------------------
# Tool Calling v3
# ---------------------------------------------------------------------------

def _params(args: Any) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(args, dict):
        return None, "os argumentos precisam ser um objeto JSON"
    try:
        return agent_estruturado.limpar_vazios(schema.ParametrosBusca.model_validate(args).compactar()), None
    except ValidationError as erro:
        return None, f"argumentos fora do tipo esperado ({erro.error_count()} erro(s)): {str(erro)[:200]}"


def chamadas_em_texto(texto: str, nomes: set[str]) -> list[tuple[str, dict[str, Any]]]:
    """Chamadas de ferramenta que o modelo escreveu como texto em vez de emitir como tool call.

    O Gemma às vezes responde `pedir_esclarecimento(pergunta="...")` ou um JSON {"name": ..., "arguments": ...}
    no conteúdo da mensagem. Isso é tratado como chamada (e registrado em extras), não como texto livre.
    """
    import ast

    saida: list[tuple[str, dict[str, Any]]] = []
    for m in re.finditer(r"\b(" + "|".join(map(re.escape, sorted(nomes))) + r")\s*\(", texto or ""):
        inicio, profundidade = m.end() - 1, 0
        for k in range(inicio, len(texto)):
            profundidade += {"(": 1, ")": -1}.get(texto[k], 0)
            if profundidade == 0:
                try:
                    no = ast.parse(texto[m.start():k + 1].strip(), mode="eval").body
                    if isinstance(no, ast.Call):
                        saida.append((m.group(1), {kw.arg: ast.literal_eval(kw.value) for kw in no.keywords if kw.arg}))
                except (SyntaxError, ValueError):
                    pass
                break
    if not saida:   # sintaxe nativa do Gemma: nome{chave:<|"|>valor<|"|>,chave2:3,chave3:{start:<|"|>...<|"|>}}
        for m in re.finditer(r"\b(" + "|".join(map(re.escape, sorted(nomes))) + r")\s*\{", texto or ""):
            corpo, fim = _chaves(texto, m.end() - 1)
            if corpo is not None:
                saida.append((m.group(1), _argumentos_gemma(corpo)))
    if not saida:
        for m in re.finditer(r"\{[^{}]*\"name\"\s*:\s*\"(\w+)\"[^{}]*\"(?:arguments|parameters)\"\s*:\s*(\{[^{}]*\})",
                             texto or ""):
            if m.group(1) in nomes:
                try:
                    saida.append((m.group(1), json.loads(m.group(2))))
                except ValueError:
                    pass
    return saida


ASPAS_GEMMA = '<|"|>'


def _chaves(texto: str, inicio: int) -> tuple[str | None, int]:
    """Conteúdo entre a chave em `inicio` e a que a fecha (respeitando os delimitadores de texto do Gemma)."""
    profundidade, k, dentro = 0, inicio, False
    while k < len(texto):
        if texto.startswith(ASPAS_GEMMA, k):
            dentro = not dentro
            k += len(ASPAS_GEMMA)
            continue
        if not dentro:
            if texto[k] == "{":
                profundidade += 1
            elif texto[k] == "}":
                profundidade -= 1
                if profundidade == 0:
                    return texto[inicio + 1:k], k
        k += 1
    return None, k


def _argumentos_gemma(corpo: str) -> dict[str, Any]:
    """chave:<|"|>texto<|"|>, chave:123, chave:{...} -> dict."""
    args: dict[str, Any] = {}
    k = 0
    while k < len(corpo):
        m = re.match(r"\s*,?\s*(\w+)\s*:\s*", corpo[k:])
        if not m:
            break
        chave, k = m.group(1), k + m.end()
        if corpo.startswith(ASPAS_GEMMA, k):
            fim = corpo.find(ASPAS_GEMMA, k + len(ASPAS_GEMMA))
            fim = len(corpo) if fim < 0 else fim
            args[chave] = corpo[k + len(ASPAS_GEMMA):fim]
            k = fim + len(ASPAS_GEMMA)
        elif corpo.startswith("{", k):
            sub, fim = _chaves(corpo, k)
            args[chave] = _argumentos_gemma(sub or "")
            k = fim + 1
        else:
            v = re.match(r"[^,}]+", corpo[k:])
            bruto = v.group(0).strip() if v else ""
            args[chave] = int(bruto) if bruto.isdigit() else {"true": True, "false": False}.get(bruto, bruto)
            k += v.end() if v else 1
    return args


def executar_auxiliar(nome: str, args: dict[str, Any], consulta: str, hoje: date) -> str:
    args = args if isinstance(args, dict) else {}
    try:
        if nome == "identificar_nome":
            return ferramentas.identificar_nome(str(args.get("nome", "")))
        if nome == "normalizar_codigo":
            return ferramentas.normalizar_codigo(str(args.get("codigo", "")))
        if nome == "normalizar_escala":
            return ferramentas.normalizar_escala(str(args.get("texto", "")))
        if nome == "resolver_periodo":
            return ferramentas.resolver_periodo(str(args.get("expressao", "")), hoje)
    except Exception as erro:  # noqa: BLE001 — a ferramenta nunca derruba a rodada
        return f"Erro na ferramenta {nome}: {type(erro).__name__}"
    return f"Ferramenta inexistente: {nome}."


class TradutorV3(agent.Tradutor):
    """Tool Calling v3: laço de ferramentas auxiliares, com ou sem retorno, e usuário simulado."""

    def __init__(self, modelo: str, abordagem: str = "tool_calling_v3", **kwargs):
        if abordagem not in VARIANTES:
            raise ValueError(f"abordagem v3 desconhecida: {abordagem!r}")
        kwargs.setdefault("num_ctx", NUM_CTX_V3)
        super().__init__(modelo, **kwargs)
        self.abordagem = abordagem
        self.auxiliares, self.retorno = VARIANTES[abordagem]
        self.llm_com_ferramenta = self.llm.bind_tools(ferramentas_da(abordagem))
        self.nomes_ferramentas = {f["function"]["name"] for f in ferramentas_da(abordagem)}

    def descricao(self) -> dict[str, Any]:
        return {"abordagem": self.abordagem, "temperature": 0, "num_predict": agent.MAX_TOKENS_SAIDA,
                "ferramentas": [f["function"]["name"] for f in ferramentas_da(self.abordagem)],
                "ferramentas_auxiliares": self.auxiliares, "validacao_com_retorno": self.retorno,
                "max_chamadas_modelo": MAX_CHAMADAS_MODELO,
                "max_tentativas_busca": MAX_TENTATIVAS_BUSCA, "usuario_simulado": RESPOSTA_USUARIO,
                "num_ctx": NUM_CTX_V3, "recusa_com_retorno": self.retorno,
                "pergunta_em_texto_respondida": self.auxiliares}

    def traduzir(self, consulta: str, hoje: date) -> Traducao:
        r = Traducao(modelo=self.modelo, hoje=hoje.isoformat(), consulta=consulta)
        sistema = prompt_tc(self.abordagem, hoje)
        mensagens: list = [SystemMessage(content=sistema), HumanMessage(content=consulta)]
        traco: list[dict[str, Any]] = []
        usadas: Counter = Counter()
        chamadas = tentativas = perguntas = perguntas_texto = avisos_recebidos = chamadas_texto = 0
        avisados: dict | None = None
        cutucou = contestou = False
        final: tuple[str, Any] | None = None
        r.tokens_prompt = r.tokens_saida = 0
        inicio = time.perf_counter()
        try:
            while chamadas < MAX_CHAMADAS_MODELO and final is None:
                resposta: AIMessage = self.llm_com_ferramenta.invoke(mensagens)
                chamadas += 1
                uso = getattr(resposta, "usage_metadata", None) or {}
                r.tokens_prompt += uso.get("input_tokens") or 0
                r.tokens_saida += uso.get("output_tokens") or 0
                mensagens.append(resposta)
                pedidos = [(c.get("name"), c.get("args"), c.get("id"), False) for c in (resposta.tool_calls or [])]
                pedidos += [(c.get("name"), c.get("args"), c.get("id"), True)
                            for c in (getattr(resposta, "invalid_tool_calls", None) or [])]
                if not pedidos:
                    em_texto = chamadas_em_texto(agent._texto(resposta.content), self.nomes_ferramentas)
                    if em_texto:
                        chamadas_texto += 1
                        # a resposta vira uma chamada de verdade no histórico, para o diálogo seguir coerente
                        falsas = [{"name": n, "args": a, "id": f"texto-{chamadas}-{k}", "type": "tool_call"}
                                  for k, (n, a) in enumerate(em_texto)]
                        mensagens[-1] = AIMessage(content="", tool_calls=falsas)
                        pedidos = [(c["name"], c["args"], c["id"], False) for c in falsas]
                if not pedidos:
                    texto = agent._texto(resposta.content)
                    if not self.auxiliares:
                        final = ("texto", texto)
                        break
                    if "?" in texto and perguntas < MAX_PERGUNTAS:
                        # pergunta escrita como texto: numa conversa ela iria ao usuário, que responde o mesmo
                        # que a pedir_esclarecimento
                        perguntas += 1
                        perguntas_texto += 1
                        traco.append({"ferramenta": "(pergunta em texto)", "args": texto[:200],
                                      "resultado": RESPOSTA_USUARIO})
                        mensagens.append(HumanMessage(content=RESPOSTA_USUARIO))
                        continue
                    if cutucou:
                        final = ("texto", texto)
                        break
                    cutucou = True
                    traco.append({"ferramenta": "(texto)", "resultado": texto[:200]})
                    mensagens.append(HumanMessage(content="Responda chamando uma ferramenta: buscar_catalogo, "
                                                          "pedir_esclarecimento ou recusar_consulta."))
                    continue
                for nome, args, id_, invalida in pedidos:
                    usadas[nome] += 1
                    if final is not None:
                        mensagens.append(ToolMessage(content="Ignorada: a consulta já foi encerrada.", tool_call_id=id_ or nome))
                        continue
                    if nome == v2.NOME_RECUSA:
                        motivo = (args or {}).get("motivo") if isinstance(args, dict) else None
                        evidencias = (ferramentas.evidencias_de_catalogo(consulta)
                                      if self.retorno and not contestou else [])
                        if evidencias:   # recusa com retorno: uma vez, e só com critério do catálogo na consulta
                            contestou = True
                            msg = ferramentas.mensagem_recusa(evidencias, CONFIRMAR_RECUSA_TC)
                            traco.append({"ferramenta": nome, "args": motivo, "resultado": msg[:300]})
                            mensagens.append(ToolMessage(content=msg, tool_call_id=id_ or nome))
                            continue
                        final = ("recusa", motivo)
                        mensagens.append(ToolMessage(content="Consulta recusada.", tool_call_id=id_ or nome))
                    elif nome == schema.NOME_FERRAMENTA:
                        tentativas += 1
                        params, erro_tipo = _params(args) if not invalida else (None, "chamada malformada")
                        if params is None:
                            msg = f"BUSCA NÃO EXECUTADA: {erro_tipo}. Chame buscar_catalogo de novo."
                            if tentativas >= MAX_TENTATIVAS_BUSCA:
                                final = ("busca", {})
                        else:
                            erros, avisos = (ferramentas.validar_parametros(params, consulta, hoje)
                                             if self.retorno else ([], []))
                            aceitar = (tentativas >= MAX_TENTATIVAS_BUSCA or not erros
                                       and (not avisos or params == avisados))
                            if aceitar:
                                final = ("busca", params)
                                msg = "Busca executada."
                            else:
                                avisos_recebidos += 1
                                avisados = params if not erros else None
                                msg = ferramentas.mensagem_validacao(erros, avisos)
                        traco.append({"ferramenta": nome, "args": params if params is not None else str(args)[:200],
                                      "resultado": msg[:300]})
                        mensagens.append(ToolMessage(content=msg, tool_call_id=id_ or nome))
                    elif nome == "pedir_esclarecimento":
                        perguntas += 1
                        pergunta = (args or {}).get("pergunta") if isinstance(args, dict) else None
                        msg = RESPOSTA_USUARIO if perguntas <= MAX_PERGUNTAS else (
                            "O usuário não tem mais nada a acrescentar: busque com o que ele disse ou recuse.")
                        traco.append({"ferramenta": nome, "args": pergunta, "resultado": msg})
                        mensagens.append(ToolMessage(content=msg, tool_call_id=id_ or nome))
                    else:
                        msg = executar_auxiliar(nome, args, consulta, hoje)
                        traco.append({"ferramenta": nome, "args": args, "resultado": msg[:300]})
                        mensagens.append(ToolMessage(content=msg, tool_call_id=id_ or nome))
        except Exception as erro:  # noqa: BLE001 — falha vira métrica
            r.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
            r.classe_erro, r.erro = _classificar_erro(erro)
            r.extras = {"traco": traco, "chamadas_modelo": chamadas}
            return r
        r.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
        r.tool_calls = [{"name": t["ferramenta"], "args": t.get("args")} for t in traco]
        if final and final[0] == "busca":
            r.chamou_ferramenta, r.predito = True, final[1]
        else:
            r.chamou_ferramenta, r.predito = False, None
            r.texto_resposta = str(final[1] or "") if final else ""
        r.extras = {"traco": traco, "chamadas_modelo": chamadas, "tentativas_busca": tentativas,
                    "perguntas": perguntas, "avisos_recebidos": avisos_recebidos,
                    "recusou": bool(final and final[0] == "recusa"), "sem_final": final is None,
                    "ferramentas_usadas": dict(usadas), "cutucou": cutucou,
                    "chamadas_em_texto": chamadas_texto, "perguntas_em_texto": perguntas_texto,
                    "recusa_contestada": contestou}
        return r


# ---------------------------------------------------------------------------
# Controle: Saída Estruturada v3 (mesmas descrições, orientações e validação)
# ---------------------------------------------------------------------------

class TradutorEstruturadoV3(agent_estruturado.TradutorEstruturado):
    def __init__(self, modelo: str, **kwargs):
        super().__init__(modelo, "saida_estruturada", **kwargs)
        self.opcoes["num_ctx"] = NUM_CTX_V3
        self.abordagem = "saida_estruturada_v3"
        self.modelo = f"{modelo} [saida-estruturada-v3]"

    def descricao(self) -> dict[str, Any]:
        return {**super().descricao(), "abordagem": self.abordagem, "descricoes": "v3",
                "validacao": "ferramentas.validar_parametros como nova tentativa",
                "recusa_com_retorno": True,
                "novas_tentativas": MAX_NOVAS_TENTATIVAS_SE}

    def traduzir(self, consulta: str, hoje: date) -> Traducao:
        r = Traducao(modelo=self.modelo, hoje=hoje.isoformat(), consulta=consulta)
        sistema = prompt_se(hoje)
        mensagens = [{"role": "system", "content": sistema}, {"role": "user", "content": consulta}]
        tentativas, avisados, historico, contestou = 0, None, [], False
        inicio = time.perf_counter()
        try:
            while True:
                tentativas += 1
                resp = self._chat(mensagens, agent_estruturado.FORMATO_SE)
                self._acumular(r, resp)
                texto = (resp.message.content or "").strip()
                r.texto_resposta = texto
                try:
                    obj = agent_estruturado._json(texto)
                except ValueError:
                    obj = None
                if isinstance(obj, dict) and obj.get(v2.CAMPO_FORA_DO_ESCOPO) is True:
                    evidencias = [] if contestou else ferramentas.evidencias_de_catalogo(consulta)
                    if evidencias:   # a mesma recusa com retorno do Tool Calling v3
                        contestou = True
                        historico.append("fora_do_escopo contestado")
                        mensagens += [{"role": "assistant", "content": texto},
                                      {"role": "user", "content": ferramentas.mensagem_recusa(
                                          evidencias, CONFIRMAR_RECUSA_SE)}]
                        continue
                    r.chamou_ferramenta, r.predito = False, None
                    historico.append("fora_do_escopo")
                    break
                params = None
                if isinstance(obj, dict):
                    params, _ = _params({k: v for k, v in obj.items() if k != v2.CAMPO_FORA_DO_ESCOPO})
                if params is None:
                    erros, avisos = ["a resposta não é um objeto JSON válido no schema"], []
                else:
                    erros, avisos = ferramentas.validar_parametros(params, consulta, hoje)
                aceitar = tentativas > MAX_NOVAS_TENTATIVAS_SE or (params is not None and not erros
                                                                   and (not avisos or params == avisados))
                historico.append({"params": params, "erros": erros, "avisos": avisos})
                if aceitar:
                    r.chamou_ferramenta, r.predito = True, params if params is not None else {}
                    break
                avisados = params if not erros else None
                mensagens += [{"role": "assistant", "content": texto},
                              {"role": "user", "content": ferramentas.mensagem_validacao(erros, avisos).replace(
                                  "chame buscar_catalogo de novo", "responda de novo só com o objeto JSON").replace(
                                  "repita a chamada com os mesmos valores", "repita o mesmo objeto JSON")}]
        except Exception as erro:  # noqa: BLE001
            r.classe_erro, r.erro = _classificar_erro(erro)
            if r.classe_erro in ("timeout", "indisponivel"):
                r.chamou_ferramenta, r.predito = False, None
        r.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
        r.extras = {"tentativas": tentativas, "historico": historico,
                    "recusou": r.predito is None and r.classe_erro is None, "recusa_contestada": contestou}
        return r


def criar(modelo: str, abordagem: str, base_url: str = agent.BASE_URL_PADRAO):
    if abordagem == "saida_estruturada_v3":
        return TradutorEstruturadoV3(modelo, base_url=base_url)
    return TradutorV3(modelo, abordagem, base_url=base_url)
