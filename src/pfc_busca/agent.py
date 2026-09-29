"""Camada de tradução: consulta em português → `tool call` estruturado.

É a etapa que o PFC avalia. Uma chamada ao modelo, via `ChatOllama` do
LangChain (Cap. 4, "Camada de Orquestração"), com a ferramenta
`buscar_catalogo` ligada por `bind_tools()`. O modelo decide se chama a
ferramenta e com quais argumentos; nada é corrigido depois — falhas viram
métrica, não fallback (Cap. 4, limitação 5).

Configuração comum a todos os modelos (Cap. 3, "Configuração dos Modelos"):
temperatura 0, até 1024 tokens de saída, zero-shot, mesmo prompt de sistema,
mesma ferramenta, thinking desativado onde o modelo o suporta.
"""

from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

import httpx
import ollama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from pydantic import ValidationError

from pfc_busca import schema
from pfc_busca.prompts import montar_system_prompt

BASE_URL_PADRAO = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MAX_TOKENS_SAIDA = 1024
TIMEOUT_S = 180.0
KEEP_ALIVE = "15m"


class ModeloIndisponivel(RuntimeError):
    """Servidor fora ou modelo não baixado — mensagem pronta para a tela."""


@dataclass
class Traducao:
    """Resultado de UMA chamada de tradução."""

    modelo: str
    hoje: str
    consulta: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    predito: dict[str, Any] | None = None        # args do 1º buscar_catalogo; None = não chamou
    chamou_ferramenta: bool = False
    texto_resposta: str = ""
    latencia_llm_ms: float | None = None
    tokens_prompt: int | None = None
    tokens_saida: int | None = None
    duracoes_ollama_ms: dict[str, float] = field(default_factory=dict)
    erro: str | None = None
    classe_erro: str | None = None               # timeout | indisponivel | args_invalidos | ferramenta_inexistente | falha
    extras: dict[str, Any] = field(default_factory=dict)  # só nas linhas de base (agent_estruturado)

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)


def capacidades(modelo: str, base_url: str = BASE_URL_PADRAO) -> list[str]:
    """`ollama show` → lista de capacidades (ex.: completion, tools, thinking)."""
    try:
        info = ollama.Client(host=base_url, timeout=10).show(modelo)
    except (ollama.ResponseError, httpx.HTTPError, ConnectionError) as erro:
        raise ModeloIndisponivel(
            f"não consegui consultar o modelo {modelo!r} em {base_url}: {erro}. "
            "O Ollama está aberto? O modelo foi baixado (ollama pull)?"
        ) from erro
    caps = getattr(info, "capabilities", None) or (info.get("capabilities") if isinstance(info, dict) else None)
    return list(caps or [])


class Tradutor:
    def __init__(self, modelo: str, *, base_url: str = BASE_URL_PADRAO,
                 temperatura: float = 0.0, max_tokens: int = MAX_TOKENS_SAIDA,
                 timeout_s: float = TIMEOUT_S, keep_alive: str = KEEP_ALIVE,
                 desativar_thinking: bool = True, seed: int | None = None, num_ctx: int | None = None):
        self.modelo = modelo
        self.base_url = base_url
        self.capacidades = capacidades(modelo, base_url)
        if "tools" not in self.capacidades:
            raise ModeloIndisponivel(f"o modelo {modelo!r} não declara suporte a tools no Ollama")
        # `reasoning=False` envia `think: false` na API nativa. Só faz sentido
        # (e só é aceito sem aviso) em modelos que declaram a capacidade.
        self.thinking_desativado = desativar_thinking and "thinking" in self.capacidades
        kwargs: dict[str, Any] = {}
        if self.thinking_desativado:
            kwargs["reasoning"] = False
        if seed is not None:
            kwargs["seed"] = seed
        if num_ctx is not None:   # só a v3 define: prompts com várias ferramentas passam de 3 mil tokens
            kwargs["num_ctx"] = num_ctx
        self.llm = ChatOllama(
            model=modelo, base_url=base_url, temperature=temperatura,
            num_predict=max_tokens, keep_alive=keep_alive,
            client_kwargs={"timeout": timeout_s}, **kwargs,
        )
        self.llm_com_ferramenta = self.llm.bind_tools([schema.FERRAMENTA_BUSCAR_CATALOGO])

    # -- chamada ------------------------------------------------------------

    def traduzir(self, consulta: str, hoje: date) -> Traducao:
        resultado = Traducao(modelo=self.modelo, hoje=hoje.isoformat(), consulta=consulta)
        mensagens = [SystemMessage(content=montar_system_prompt(hoje)),
                     HumanMessage(content=consulta)]
        inicio = time.perf_counter()
        try:
            resposta: AIMessage = self.llm_com_ferramenta.invoke(mensagens)
        except Exception as erro:  # noqa: BLE001 — cada falha vira métrica, não crash
            resultado.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
            resultado.classe_erro, resultado.erro = _classificar_erro(erro)
            return resultado
        resultado.latencia_llm_ms = (time.perf_counter() - inicio) * 1000
        self._preencher(resultado, resposta)
        return resultado

    def _preencher(self, r: Traducao, resposta: AIMessage) -> None:
        r.texto_resposta = _texto(resposta.content)
        uso = getattr(resposta, "usage_metadata", None) or {}
        r.tokens_prompt = uso.get("input_tokens")
        r.tokens_saida = uso.get("output_tokens")
        meta = getattr(resposta, "response_metadata", None) or {}
        for chave in ("total_duration", "load_duration", "prompt_eval_duration", "eval_duration"):
            if meta.get(chave) is not None:
                r.duracoes_ollama_ms[chave.replace("_duration", "")] = meta[chave] / 1e6

        chamadas = list(getattr(resposta, "tool_calls", None) or [])
        # tool calls que o Ollama não conseguiu parsear chegam aqui
        invalidas = list(getattr(resposta, "invalid_tool_calls", None) or [])
        r.tool_calls = [{"name": c.get("name"), "args": c.get("args"), "id": c.get("id")} for c in chamadas]
        r.tool_calls += [{"name": c.get("name"), "args": c.get("args"), "id": c.get("id"),
                          "invalida": True, "erro": c.get("error")} for c in invalidas]
        r.chamou_ferramenta = bool(chamadas or invalidas)
        if not r.chamou_ferramenta:
            return

        principal = next((c for c in chamadas if c.get("name") == schema.NOME_FERRAMENTA), None)
        if principal is None:
            if invalidas and not chamadas:
                r.classe_erro, r.erro = "args_invalidos", f"tool call malformada: {invalidas[0].get('error')}"
            else:
                r.classe_erro = "ferramenta_inexistente"
                r.erro = f"chamou ferramenta(s) inexistente(s): {[c.get('name') for c in chamadas]}"
            r.predito = {}
            return

        args = principal.get("args") or {}
        if not isinstance(args, dict):
            r.classe_erro, r.erro = "args_invalidos", f"argumentos não são objeto: {args!r}"
            r.predito = {}
            return
        try:
            r.predito = schema.ParametrosBusca.model_validate(args).compactar()
        except ValidationError as erro:
            # Guarda como veio: a comparação campo a campo é quem vai contar o erro.
            r.classe_erro = "args_invalidos"
            r.erro = f"argumentos fora do tipo esperado: {erro.error_count()} erro(s)"
            r.predito = {k: v for k, v in args.items() if v is not None}


def _texto(conteudo: Any) -> str:
    if isinstance(conteudo, str):
        return conteudo.strip()
    if isinstance(conteudo, list):
        return " ".join(
            (b.get("text", "") if isinstance(b, dict) else str(b)) for b in conteudo
        ).strip()
    return str(conteudo or "").strip()


def _classificar_erro(erro: Exception) -> tuple[str, str]:
    texto = str(erro).strip().replace("\n", " ")[:300]
    if isinstance(erro, httpx.TimeoutException | TimeoutError):
        return "timeout", f"tempo esgotado ({TIMEOUT_S:.0f} s)"
    if isinstance(erro, httpx.ConnectError | ConnectionError):
        return "indisponivel", f"servidor do Ollama inacessível: {texto}"
    codigo = getattr(erro, "status_code", None)
    if isinstance(erro, ollama.ResponseError):
        if codigo in (400, 404):
            return "indisponivel", f"Ollama recusou (HTTP {codigo}): {texto}"
        return "falha", f"Ollama respondeu erro (HTTP {codigo}): {texto}"
    return "falha", f"{type(erro).__name__}: {texto}"


def versao_servidor(base_url: str = BASE_URL_PADRAO) -> str | None:
    try:
        return httpx.get(f"{base_url}/api/version", timeout=5).json().get("version")
    except (httpx.HTTPError, ValueError):
        return None
