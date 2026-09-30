"""Registro único das abordagens de tradução: Tool Calling (TC) e Saída Estruturada (SE).

Cada configuração que o projeto sabe executar aparece aqui uma vez, com o que a identifica:

- nome: o valor de `pfc-avaliar --abordagem` e de `PFC_ABORDAGEM` na API;
- família (TC ou SE) e versão da especificação (v1, v2, v3; o método do protótipo);
- prefixo da pasta de resultados (`results/<prefixo><modelo>/`);
- se roda só no Ollama (não tem fábrica para o Groq);
- a fábrica do tradutor: um objeto com `traduzir(consulta, hoje) -> agent.Traducao`;
- o texto do prompt e a definição da ferramenta cujos SHA-256 vão para o manifesto de cada rodada.

`pfc-avaliar` (evaluation/run_evaluation.py), a API (api.py) e o comando `pfc` (cli.py) leem daqui.
Os módulos de cada versão (agent, agent_estruturado, v2, v3, ferramentas, schema, prompts) ficam
congelados: os hashes das rodadas da tese dependem do texto deles, e o registro só os importa e envolve.

Para acrescentar uma versão (por exemplo, tool_calling_v4):
1. escreva o tradutor num módulo próprio, com `traduzir(consulta, hoje) -> agent.Traducao`; para o
   manifesto de `pfc-avaliar`, também `modelo`, `base_url`, `thinking_desativado` e `descricao()`;
2. acrescente uma entrada `Abordagem(...)` em `_ENTRADAS`, com nome e prefixo novos;
3. rode `pytest`: tests/test_abordagens.py confere nomes e prefixos únicos e tests/test_regressao_abordagens.py,
   que os hashes das rodadas já gravadas em results/ continuam reproduzidos. A partir daí,
   `pfc abordagens` lista a entrada, e `pfc-avaliar --abordagem tool_calling_v4` e
   `PFC_ABORDAGEM=tool_calling_v4` passam a aceitá-la.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any

from pfc_busca import agent, agent_estruturado, ferramentas, prompts, schema, v2, v3

RAIZ_REPO = Path(__file__).resolve().parents[2]
DIR_RESULTADOS = RAIZ_REPO / "results"
FAMILIAS = {"TC": "Tool Calling", "SE": "Saída Estruturada"}
PROVEDORES = ("ollama", "groq")

# A configuração que a tese recomenda, e o modelo em que ela foi avaliada (lote 2 e 310 consultas, results/lote2
# e results/v3_310): é o padrão da API.
RECOMENDADA = "tool_calling_v3"
MODELO_RECOMENDADO = "gemma4:e4b-it-qat"

# (modelo, base_url) -> tradutor local; (modelo, registrar) -> tradutor no Groq
FabricaLocal = Callable[[str, str], Any]
FabricaGroq = Callable[[str, Callable[..., Any]], Any]


class AbordagemDesconhecida(ValueError):
    """Nome fora do registro; a mensagem lista os nomes válidos."""


@dataclass(frozen=True)
class Abordagem:
    nome: str
    familia: str                           # "TC" | "SE"
    versao: str                            # versão da especificação: "v1", "v2", "v3", "protótipo"
    prefixo: str                           # results/<prefixo><modelo>/
    descricao: str
    criar_local: FabricaLocal              # tradutor no Ollama
    texto_prompt: Callable[[], str]        # o que identifica prompt e especificação (manifesto: prompt_sha256)
    ferramenta: Callable[[], Any]          # definição da(s) ferramenta(s) (manifesto: ferramenta_sha256)
    criar_groq: FabricaGroq | None = None  # sem fábrica: roda só no Ollama
    dados: tuple[str, ...] = ()            # arquivos de ferramentas.DADOS que entram no hash (v3)

    @property
    def so_ollama(self) -> bool:
        return self.criar_groq is None

    @property
    def recomendada(self) -> bool:
        return self.nome == RECOMENDADA

    @property
    def nomes_ferramentas(self) -> list[str]:
        definicao = self.ferramenta()
        lista = definicao if isinstance(definicao, list) else [definicao]
        return [f["function"]["name"] for f in lista]

    def hash_prompt(self) -> str:
        return _sha256(self.texto_prompt())

    def hash_ferramenta(self) -> str:
        return _sha256(json.dumps(self.ferramenta(), ensure_ascii=False, sort_keys=True))

    def criar(self, modelo: str, *, provedor: str = "ollama", base_url: str = agent.BASE_URL_PADRAO,
              registrar: Callable[..., Any] = print) -> Any:
        """Tradutor desta abordagem; `agent.ModeloIndisponivel` se o Ollama ou o modelo não responderem."""
        if provedor == "ollama":
            return self.criar_local(modelo, base_url)
        if provedor == "groq":
            if self.criar_groq is None:
                raise ValueError(f"a abordagem {self.nome} roda só no Ollama")
            return self.criar_groq(modelo, registrar)
        raise ValueError(f"provedor desconhecido: {provedor!r} (válidos: {', '.join(PROVEDORES)})")


def _sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Fábricas: só envolvem os construtores que já existem
# ---------------------------------------------------------------------------

def _tc_v1(modelo: str, base_url: str) -> agent.Tradutor:
    return agent.Tradutor(modelo, base_url=base_url)


def _estruturado(abordagem: str, modelo: str, base_url: str) -> agent_estruturado.TradutorEstruturado:
    return agent_estruturado.TradutorEstruturado(modelo, abordagem, base_url=base_url)


def _v2(abordagem: str, modelo: str, base_url: str) -> Any:
    return v2.criar(modelo, abordagem, base_url=base_url)


def _v3(abordagem: str, modelo: str, base_url: str) -> Any:
    return v3.criar(modelo, abordagem, base_url=base_url)


def _groq_tc(modelo: str, registrar: Callable[..., Any]) -> Any:
    # importa openai/langchain_openai só quando o Groq é usado, como antes
    from pfc_busca.agent_groq import TradutorGroq

    return TradutorGroq(modelo, registrar=registrar)


def _groq_se(modelo: str, registrar: Callable[..., Any]) -> Any:
    from pfc_busca.agent_groq import TradutorEstruturadoGroq

    return TradutorEstruturadoGroq(modelo, registrar=registrar)


# ---------------------------------------------------------------------------
# O que entra nos hashes do manifesto (mesmos textos de antes do registro)
# ---------------------------------------------------------------------------

def _prompt_se_v1() -> str:
    return agent_estruturado._MODELO_SE + json.dumps(agent_estruturado.PARAMETROS, ensure_ascii=False, sort_keys=True)


def _prompt_prototipo() -> str:
    return agent_estruturado._PROMPT_PROTOTIPO + agent_estruturado.instrucao_instructor()


def _ferramenta_v1() -> dict[str, Any]:
    return schema.FERRAMENTA_BUSCAR_CATALOGO


DADOS_V3 = ("municipios_ibge.json", "indice_folhas.json")

_ENTRADAS = [
    Abordagem("tool_calling", "TC", "v1", "",
              "uma chamada com buscar_catalogo; zero-shot (a solução do Cap. 4)",
              _tc_v1, lambda: prompts._MODELO, _ferramenta_v1, criar_groq=_groq_tc),
    Abordagem("saida_estruturada", "SE", "v1", "se-",
              "mesmo prompt e schema da v1, resposta em JSON sem ferramenta (linha de base)",
              partial(_estruturado, "saida_estruturada"), _prompt_se_v1, _ferramenta_v1, criar_groq=_groq_se),
    Abordagem("prototipo", "SE", "protótipo", "prototipo-",
              "método do protótipo do 1º CGEO: dicionário, exemplos, novas tentativas e fallback (linha de base)",
              partial(_estruturado, "prototipo"), _prompt_prototipo, _ferramenta_v1),
    Abordagem("tool_calling_v2", "TC", "v2", "tc2-",
              "descrições com as convenções do manual e recusar_consulta (lote 1)",
              partial(_v2, "tool_calling_v2"), partial(v2.texto_hash, "tool_calling_v2"),
              lambda: [v2.FERRAMENTA_BUSCAR_CATALOGO_V2, v2.FERRAMENTA_RECUSAR]),
    Abordagem("saida_estruturada_v2", "SE", "v2", "se2-",
              "especificação v2 em JSON, com o campo fora_do_escopo (lote 1)",
              partial(_v2, "saida_estruturada_v2"), partial(v2.texto_hash, "saida_estruturada_v2"),
              lambda: v2.FERRAMENTA_BUSCAR_CATALOGO_V2),
    Abordagem("tool_calling_v3d", "TC", "v3", v3.PREFIXOS["tool_calling_v3d"],
              "degrau 1 da v3: descrições v3, uma chamada (buscar_catalogo ou recusar_consulta)",
              partial(_v3, "tool_calling_v3d"), partial(v3.texto_hash, "tool_calling_v3d"),
              partial(v3.ferramentas_da, "tool_calling_v3d"), dados=DADOS_V3),
    Abordagem("tool_calling_v3a", "TC", "v3", v3.PREFIXOS["tool_calling_v3a"],
              "degrau 2 da v3: + ferramentas auxiliares e pedir_esclarecimento num laço de chamadas",
              partial(_v3, "tool_calling_v3a"), partial(v3.texto_hash, "tool_calling_v3a"),
              partial(v3.ferramentas_da, "tool_calling_v3a"), dados=DADOS_V3),
    Abordagem("tool_calling_v3", "TC", "v3", v3.PREFIXOS["tool_calling_v3"],
              "v3 completa: + validação com retorno e recusa contestada (a recomendada)",
              partial(_v3, "tool_calling_v3"), partial(v3.texto_hash, "tool_calling_v3"),
              partial(v3.ferramentas_da, "tool_calling_v3"), dados=DADOS_V3),
    Abordagem("saida_estruturada_v3", "SE", "v3", v3.PREFIXOS["saida_estruturada_v3"],
              "controle da v3: descrições v3 e o mesmo retorno como nova tentativa, sem auxiliares",
              partial(_v3, "saida_estruturada_v3"), partial(v3.texto_hash, "saida_estruturada_v3"),
              partial(v3.ferramentas_da, "saida_estruturada_v3"), dados=DADOS_V3),
]

REGISTRO: dict[str, Abordagem] = {a.nome: a for a in _ENTRADAS}
NOMES: tuple[str, ...] = tuple(REGISTRO)


# ---------------------------------------------------------------------------
# Consulta ao registro
# ---------------------------------------------------------------------------

def obter(nome: str) -> Abordagem:
    try:
        return REGISTRO[nome]
    except KeyError:
        raise AbordagemDesconhecida(f"abordagem desconhecida: {nome!r}; válidas: {', '.join(NOMES)}") from None


def criar_tradutor(nome: str, modelo: str, *, provedor: str = "ollama", base_url: str = agent.BASE_URL_PADRAO,
                   registrar: Callable[..., Any] = print) -> Any:
    return obter(nome).criar(modelo, provedor=provedor, base_url=base_url, registrar=registrar)


def hash_prompt(nome: str) -> str:
    return obter(nome).hash_prompt()


def hash_ferramenta(nome: str) -> str:
    return obter(nome).hash_ferramenta()


def configuracao(nome: str, modelo: str) -> dict[str, str]:
    """Identidade de uma configuração implantada: abordagem, modelo e os dois hashes do manifesto.

    `sha256` resume os quatro; `prompt_sha256` e `ferramenta_sha256` são os mesmos gravados no manifesto
    de cada rodada, e podem ser comparados com ele diretamente."""
    a = obter(nome)
    ident = {"abordagem": a.nome, "modelo": modelo, "prompt_sha256": a.hash_prompt(),
             "ferramenta_sha256": a.hash_ferramenta()}
    return {**ident, "sha256": _sha256(json.dumps(ident, sort_keys=True))}


def rodadas_com_a_mesma_configuracao(nome: str, modelo: str, dir_resultados: Path = DIR_RESULTADOS) -> list[str]:
    """Rodadas locais em results/ feitas com esta abordagem, este modelo e os mesmos hashes (sem as descartadas
    e os ciclos de desenvolvimento). Lista vazia: a configuração não é nenhuma das avaliadas."""
    ident = configuracao(nome, modelo)
    if not dir_resultados.is_dir():
        return []
    iguais = []
    for m in sorted(dir_resultados.rglob("manifesto.json")):
        partes = m.relative_to(dir_resultados).parts
        if any(p.startswith(("_", "dev_")) for p in partes):
            continue
        try:
            d = json.loads(m.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if ((d.get("provedor") or "ollama") == "ollama" and (d.get("abordagem") or "tool_calling") == nome
                and d.get("modelo") == modelo and d.get("prompt_sha256") == ident["prompt_sha256"]
                and d.get("ferramenta_sha256") == ident["ferramenta_sha256"]):
            iguais.append(m.parent.relative_to(dir_resultados.parent).as_posix())
    return iguais


def estado_dos_dados(nome: str) -> dict[str, bool]:
    """Arquivo de dados das ferramentas -> existe? (vazio para as abordagens que não dependem de dados)."""
    return {arq: (ferramentas.DADOS / arq).exists() for arq in obter(nome).dados}


def avisos(nome: str) -> list[str]:
    """O que falta para a abordagem funcionar como foi avaliada. Vazio: nada falta."""
    a = obter(nome)
    estado = estado_dos_dados(nome)
    saida = []
    gerar = "gere-o com python scripts/v3/gerar_dados_ferramentas.py"
    if estado.get("municipios_ibge.json") is False:
        saida.append(f"{ferramentas.DADOS / 'municipios_ibge.json'} ausente: a validação e as ferramentas auxiliares "
                     f"da v3 falham e as consultas terminam em erro; {gerar}.")
    if estado.get("indice_folhas.json") is False:
        efeito = ("identificar_nome e normalizar_codigo funcionam sem o índice de folhas do BDGEx: não reconhecem "
                  "nomes de folha do acervo nem dizem se um código consta nele; "
                  if "identificar_nome" in a.nomes_ferramentas else "")
        saida.append(f"{ferramentas.DADOS / 'indice_folhas.json'} ausente (não é versionado): {efeito}o hash da "
                     f"configuração difere do das rodadas avaliadas, porque o arquivo entra nele; {gerar} a partir "
                     f"da coleta do BDGEx (scripts/lote_validacao/coletar_bdgex.py) ou copie-o do pacote do Colab.")
    return saida


def tabela() -> list[dict[str, Any]]:
    """Uma linha por abordagem, na ordem do registro (para `pfc abordagens`)."""
    return [{"nome": a.nome, "familia": a.familia, "versao": a.versao, "prefixo": a.prefixo,
             "so_ollama": a.so_ollama, "recomendada": a.recomendada, "descricao": a.descricao,
             # na SE a definição da ferramenta só entra no hash (é o schema do JSON), não é chamada
             "ferramentas": a.nomes_ferramentas if a.familia == "TC" else []} for a in REGISTRO.values()]
