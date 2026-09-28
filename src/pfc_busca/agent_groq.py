"""Tradutor para modelos servidos pelo Groq — resultado PARALELO, em nuvem.

Não é a configuração avaliada para implantação: o requisito RNF1 exige execução
local. Serve como referência: os mesmos prompt, ferramenta, dataset e métricas,
aplicados a modelos maiores servidos em nuvem. Os resultados ficam em
`results/groq-<modelo>/` e são reportados em seção própria, sempre rotulados como
nuvem.

A troca de provedor é exatamente a portabilidade que o LangChain oferece:
`ChatOllama` → `ChatOpenAI` apontado para o endpoint compatível do Groq. O
`bind_tools()` e a interpretação da resposta são os mesmos do tradutor local
(`agent.Tradutor._preencher`).

Particularidades do Groq tratadas aqui:
- limites do plano gratuito (tokens por minuto e por dia): um 429 faz o tradutor
  esperar o tempo pedido pelo servidor e repetir — a latência registrada é só a da
  tentativa que respondeu;
- o servidor valida os argumentos contra o schema e rejeita (HTTP 400,
  `tool_use_failed`) um tool call inválido. É um erro DO MODELO: os argumentos
  gerados, quando recuperáveis em `failed_generation`, são avaliados campo a campo,
  como no tradutor local.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import date
from typing import Any

import openai
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from pfc_busca import schema
from pfc_busca.agent import MAX_TOKENS_SAIDA, ModeloIndisponivel, Traducao, Tradutor
from pfc_busca.prompts import montar_system_prompt

BASE_URL_GROQ = "https://api.groq.com/openai/v1"
TIMEOUT_S = 60.0
ESPERA_MAXIMA_S = 6 * 3600  # teto de espera por limite diário


def esforco_de_raciocinio(modelo: str) -> str | None:
    """Menor esforço de raciocínio aceito por modelo (thinking desativado quando possível)."""
    if "qwen3" in modelo:
        return "none"
    if "gpt-oss" in modelo:
        return "low"  # a família gpt-oss não permite desligar o raciocínio
    return None


class TradutorGroq(Tradutor):
    """Mesma interface de `agent.Tradutor`; só a chamada ao modelo muda."""

    provedor = "groq"

    def __init__(self, modelo: str, *, chave: str | None = None, temperatura: float = 0.0,
                 max_tokens: int = MAX_TOKENS_SAIDA, timeout_s: float = TIMEOUT_S,
                 registrar=print):
        chave = chave or os.environ.get("GROQ_API_KEY", "").strip()
        if not chave:
            raise ModeloIndisponivel("GROQ_API_KEY ausente (defina no .env)")
        self.modelo = modelo
        self.base_url = BASE_URL_GROQ
        self.capacidades = ["tools"]
        self.esforco = esforco_de_raciocinio(modelo)
        self.thinking_desativado = self.esforco == "none"
        self.registrar = registrar
        extra = {"reasoning_effort": self.esforco} if self.esforco else {}
        self.llm = ChatOpenAI(model=modelo, base_url=BASE_URL_GROQ, api_key=chave,
                              temperature=temperatura, max_tokens=max_tokens,
                              timeout=timeout_s, max_retries=0, extra_body=extra or None)
        self.llm_com_ferramenta = self.llm.bind_tools([schema.FERRAMENTA_BUSCAR_CATALOGO],
                                                      tool_choice="auto")

    def traduzir(self, consulta: str, hoje: date) -> Traducao:
        resultado = Traducao(modelo=self.modelo, hoje=hoje.isoformat(), consulta=consulta)
        mensagens = [SystemMessage(content=montar_system_prompt(hoje)), HumanMessage(content=consulta)]
        resposta = self._invocar(self.llm_com_ferramenta, mensagens, resultado,
                                 {"tool_use_failed": self._rejeitado})
        if resposta is not None:
            self._preencher(resultado, resposta)
        return resultado

    def _invocar(self, executavel, mensagens: list, resultado: Traducao, rejeicoes: dict) -> AIMessage | None:
        """Chama o modelo com as esperas e novas tentativas do provedor.

        Devolve a resposta, ou None quando o resultado já foi preenchido com o erro. `rejeicoes`
        associa o código de um HTTP 400 (argumentos ou JSON rejeitados pelo servidor, erro do
        modelo) à função que registra a rejeição.
        """
        tentativas_falha = 0
        while True:
            inicio = time.perf_counter()
            try:
                resposta: AIMessage = executavel.invoke(mensagens)
            except openai.RateLimitError as erro:
                espera = _espera_pedida(erro)
                self.registrar(f"   limite do Groq ({self.modelo}): aguardando {espera:.0f} s")
                time.sleep(espera)
                continue
            except openai.BadRequestError as erro:
                resultado.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
                registrar_rejeicao = rejeicoes.get(_codigo(erro))
                if registrar_rejeicao:
                    registrar_rejeicao(resultado, erro)
                else:
                    resultado.classe_erro = "indisponivel"
                    resultado.erro = f"Groq recusou (HTTP 400): {_mensagem(erro)}"
                return None
            except (openai.APITimeoutError, openai.APIConnectionError, openai.InternalServerError) as erro:
                tentativas_falha += 1
                if tentativas_falha <= 3:
                    time.sleep(10 * tentativas_falha)
                    continue
                resultado.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
                resultado.classe_erro = "timeout" if isinstance(erro, openai.APITimeoutError) else "falha"
                resultado.erro = f"{type(erro).__name__}: {str(erro)[:200]}"
                return None
            except openai.APIStatusError as erro:
                resultado.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
                resultado.classe_erro = "falha"
                resultado.erro = f"Groq HTTP {erro.status_code}: {_mensagem(erro)}"
                return None
            resultado.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
            return resposta

    def _rejeitado(self, r: Traducao, erro: openai.BadRequestError) -> None:
        """O servidor rejeitou o tool call por não casar com o schema: erro do modelo."""
        r.chamou_ferramenta = True
        r.classe_erro = "args_invalidos"
        r.erro = f"rejeitado pelo servidor (tool_use_failed): {_mensagem(erro)[:200]}"
        args = _argumentos_de_failed_generation(_corpo(erro).get("failed_generation"))
        r.tool_calls = [{"name": schema.NOME_FERRAMENTA, "args": args, "invalida": True}]
        r.predito = {k: v for k, v in (args or {}).items() if v is not None}


class TradutorEstruturadoGroq(TradutorGroq):
    """Linha de base com Saída Estruturada no Groq, para os modelos de maior porte.

    O mesmo prompt e o mesmo tratamento da linha de base local (`agent_estruturado`,
    configuração ``saida_estruturada``): resposta em modo JSON
    (`response_format={"type": "json_object"}`), sem ferramenta, com o schema dos parâmetros
    no prompt e o mesmo esforço de raciocínio da rodada com Tool Calling do modelo. Um JSON
    rejeitado pelo servidor (`json_validate_failed`) é erro do modelo.
    """

    def __init__(self, modelo: str, **kwargs):
        from pfc_busca import agent_estruturado

        super().__init__(modelo, **kwargs)
        self.tag = modelo
        self.abordagem = "saida_estruturada"
        self.modelo = agent_estruturado.rotulo_modelo(modelo, "saida_estruturada")
        self.llm_json = self.llm.bind(response_format={"type": "json_object"})

    def descricao(self) -> dict[str, Any]:
        return {"abordagem": self.abordagem, "temperature": 0, "num_predict": MAX_TOKENS_SAIDA, "ferramenta": False,
                "formato": "modo JSON do Groq (json_object); schema dos parâmetros no prompt",
                "zero_shot": True, "few_shot": False, "dicionario_normalizacao": False, "fallback": False,
                "esforco_de_raciocinio": self.esforco}

    def traduzir(self, consulta: str, hoje: date) -> Traducao:
        from pfc_busca import agent_estruturado

        r = Traducao(modelo=self.modelo, hoje=hoje.isoformat(), consulta=consulta)
        r.chamou_ferramenta = True   # na Saída Estruturada a aplicação sempre busca
        mensagens = [SystemMessage(content=agent_estruturado.montar_prompt_se(hoje)), HumanMessage(content=consulta)]
        resposta = self._invocar(self.llm_json, mensagens, r, {"json_validate_failed": self._json_rejeitado})
        if resposta is None:
            if r.classe_erro in ("timeout", "indisponivel", "falha"):
                r.chamou_ferramenta, r.predito = False, None
            return r
        uso = getattr(resposta, "usage_metadata", None) or {}
        r.tokens_prompt, r.tokens_saida = uso.get("input_tokens"), uso.get("output_tokens")
        r.texto_resposta = str(resposta.content or "").strip()
        obj: Any = None
        try:
            obj = agent_estruturado._json(r.texto_resposta)
            r.predito = agent_estruturado.limpar_vazios(schema.ParametrosBusca.model_validate(obj).compactar())
        except (ValueError, ValidationError) as erro:
            r.classe_erro, r.erro = "args_invalidos", f"resposta fora do schema: {str(erro)[:200]}"
            r.predito = agent_estruturado.limpar_vazios(obj) if isinstance(obj, dict) else {}
        r.extras = {"objeto_vazio": not r.predito}
        return r

    def _json_rejeitado(self, r: Traducao, erro: openai.BadRequestError) -> None:
        from pfc_busca import agent_estruturado

        r.classe_erro = "args_invalidos"
        r.erro = f"JSON rejeitado pelo servidor (json_validate_failed): {_mensagem(erro)[:200]}"
        args = _argumentos_de_failed_generation(_corpo(erro).get("failed_generation"))
        r.predito = agent_estruturado.limpar_vazios(args or {})
        r.extras = {"objeto_vazio": not r.predito}


# ---------------------------------------------------------------------------
# Utilitários de erro
# ---------------------------------------------------------------------------

def _corpo(erro: openai.APIStatusError) -> dict:
    corpo = getattr(erro, "body", None)
    if isinstance(corpo, dict):
        return corpo.get("error", corpo) if isinstance(corpo.get("error"), dict) else corpo
    return {}


def _codigo(erro: openai.APIStatusError) -> str | None:
    return _corpo(erro).get("code")


def _mensagem(erro: openai.APIStatusError) -> str:
    return str(_corpo(erro).get("message") or erro)[:300]


def _espera_pedida(erro: openai.RateLimitError) -> float:
    cabecalhos = getattr(getattr(erro, "response", None), "headers", {}) or {}
    for chave in ("retry-after", "x-ratelimit-reset-tokens", "x-ratelimit-reset-requests"):
        valor = cabecalhos.get(chave)
        if valor:
            segundos = _segundos(valor)
            if segundos is not None:
                return min(max(segundos + 1.0, 2.0), ESPERA_MAXIMA_S)
    texto = _mensagem(erro)
    m = re.search(r"try again in ((?:\d+h)?(?:\d+m)?[\d.]+s)", texto)
    if m:
        segundos = _segundos(m.group(1))
        if segundos is not None:
            return min(segundos + 1.0, ESPERA_MAXIMA_S)
    return 30.0


def _segundos(valor: str) -> float | None:
    """'12', '12.5', '1m30.2s', '2h3m4s' → segundos."""
    valor = str(valor).strip()
    try:
        return float(valor)
    except ValueError:
        pass
    m = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:([\d.]+)s)?", valor)
    if not m or not any(m.groups()):
        return None
    h, mi, s = (float(x) if x else 0.0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def _argumentos_de_failed_generation(texto: Any) -> dict | None:
    """Recupera os argumentos de um tool call rejeitado, se o texto contiver um objeto JSON."""
    if not isinstance(texto, str):
        return None
    candidatos = []
    for m in re.finditer(r"\{", texto):
        profundidade = 0
        for fim in range(m.start(), len(texto)):
            if texto[fim] == "{":
                profundidade += 1
            elif texto[fim] == "}":
                profundidade -= 1
                if profundidade == 0:
                    candidatos.append(texto[m.start(): fim + 1])
                    break
        if candidatos:
            break
    for bruto in candidatos:
        try:
            obj = json.loads(bruto)
        except ValueError:
            continue
        if isinstance(obj, dict):
            if isinstance(obj.get("arguments"), dict):
                return obj["arguments"]
            if isinstance(obj.get("parameters"), dict):
                return obj["parameters"]
            return obj
    return None
