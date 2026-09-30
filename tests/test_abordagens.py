"""Registro único das abordagens (pfc_busca.abordagens) e o comando pfc (pfc_busca.cli)."""

import json
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest

from pfc_busca import abordagens, agent, agent_estruturado, cli, ferramentas, v2, v3
from pfc_busca.evaluation import run_evaluation as rv

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture
def ollama_falso(monkeypatch):
    """Os construtores só consultam o Ollama em `capacidades`; o resto (ChatOllama, ollama.Client) é preguiçoso."""
    caps = lambda modelo, base_url=None: ["completion", "tools"]  # noqa: E731
    monkeypatch.setattr(agent, "capacidades", caps)
    monkeypatch.setattr(agent_estruturado, "capacidades", caps)


def test_nomes_prefixos_e_familias():
    nomes = list(abordagens.REGISTRO)
    prefixos = [a.prefixo for a in abordagens.REGISTRO.values()]
    assert len(set(nomes)) == len(nomes) and len(set(prefixos)) == len(prefixos)
    assert all(a.familia in abordagens.FAMILIAS for a in abordagens.REGISTRO.values())
    assert [a.nome for a in abordagens.REGISTRO.values() if a.recomendada] == [abordagens.RECOMENDADA]
    assert abordagens.obter(abordagens.RECOMENDADA).familia == "TC"
    # o que roda no Groq é exatamente o que tem fábrica para o Groq
    assert {a.nome for a in abordagens.REGISTRO.values() if not a.so_ollama} == {"tool_calling", "saida_estruturada"}


def test_toda_abordagem_dos_modulos_esta_no_registro():
    # uma variante nova num módulo que não entrou no registro não seria aceita por pfc-avaliar nem pela API
    dos_modulos = {"tool_calling", *agent_estruturado.ABORDAGENS, *v2.ABORDAGENS_V2, *v3.ABORDAGENS_V3}
    assert dos_modulos == set(abordagens.NOMES)
    assert all(abordagens.obter(n).prefixo == p for n, p in v3.PREFIXOS.items())


def test_nome_desconhecido():
    with pytest.raises(abordagens.AbordagemDesconhecida, match="tool_calling_v3"):
        abordagens.obter("tool_calling_v9")


CLASSES = {
    "tool_calling": agent.Tradutor, "saida_estruturada": agent_estruturado.TradutorEstruturado,
    "prototipo": agent_estruturado.TradutorEstruturado, "tool_calling_v2": v2.TradutorV2,
    "saida_estruturada_v2": v2.TradutorEstruturadoV2, "tool_calling_v3d": v3.TradutorV3,
    "tool_calling_v3a": v3.TradutorV3, "tool_calling_v3": v3.TradutorV3,
    "saida_estruturada_v3": v3.TradutorEstruturadoV3,
}


@pytest.mark.parametrize("nome", list(CLASSES))
def test_fabrica_cria_o_mesmo_tradutor_que_antes(nome, ollama_falso):
    t = abordagens.criar_tradutor(nome, "modelo-falso", base_url="http://ollama:11434")
    assert type(t) is CLASSES[nome] and callable(t.traduzir)
    assert t.base_url == "http://ollama:11434"
    if nome != "tool_calling":
        assert getattr(t, "abordagem", None) == nome
    # run_evaluation.criar_tradutor (pfc-avaliar) passa pela mesma fábrica
    args = SimpleNamespace(abordagem=nome, modelo="modelo-falso", provedor="ollama", base_url="http://ollama:11434")
    assert type(rv.criar_tradutor(args)) is CLASSES[nome]


def test_fabrica_do_groq(monkeypatch):
    from pfc_busca.agent_groq import TradutorEstruturadoGroq, TradutorGroq

    monkeypatch.setenv("GROQ_API_KEY", "chave-de-teste")
    assert type(abordagens.criar_tradutor("tool_calling", "qwen/qwen3.8-27b", provedor="groq")) is TradutorGroq
    assert type(abordagens.criar_tradutor("saida_estruturada", "qwen/qwen3.8-27b", provedor="groq")) \
        is TradutorEstruturadoGroq
    with pytest.raises(ValueError, match="só no Ollama"):
        abordagens.criar_tradutor("tool_calling_v3", "qwen/qwen3.8-27b", provedor="groq")
    with pytest.raises(ValueError, match="provedor"):
        abordagens.criar_tradutor("tool_calling", "x", provedor="openrouter")


def test_identidade_da_configuracao():
    c = abordagens.configuracao("tool_calling", "qwen3:4b-instruct-2507-q4_K_M")
    assert c["prompt_sha256"] == rv.hash_prompt("tool_calling") and len(c["sha256"]) == 64
    assert c["sha256"] != abordagens.configuracao("tool_calling", "gemma4:e2b-it-qat")["sha256"]
    assert c["sha256"] != abordagens.configuracao("saida_estruturada", "qwen3:4b-instruct-2507-q4_K_M")["sha256"]


@pytest.mark.skipif(not (RAIZ / "results").is_dir(), reason="sem results/")
def test_rodadas_com_a_mesma_configuracao():
    rodadas = abordagens.rodadas_com_a_mesma_configuracao("tool_calling", "qwen3:4b-instruct-2507-q4_K_M")
    assert "results/qwen3-4b-instruct-2507-q4_K_M" in rodadas
    assert "results/estacao/qwen3-4b-instruct-2507-q4_K_M" in rodadas
    assert not any("_descartados" in r for r in rodadas)
    assert abordagens.rodadas_com_a_mesma_configuracao("tool_calling", "modelo-nunca-avaliado") == []
    if (ferramentas.DADOS / "indice_folhas.json").exists():
        assert "results/lote2/tc3-gemma4-e4b-it-qat" in abordagens.rodadas_com_a_mesma_configuracao(
            abordagens.RECOMENDADA, abordagens.MODELO_RECOMENDADO)


def test_v3_sem_indice_de_folhas_degrada_sem_quebrar(sem_indice):
    assert abordagens.estado_dos_dados("tool_calling_v3") == {"municipios_ibge.json": True,
                                                              "indice_folhas.json": False}
    assert abordagens.estado_dos_dados("tool_calling") == {} and abordagens.avisos("tool_calling") == []
    [aviso] = abordagens.avisos("tool_calling_v3")
    assert "indice_folhas.json" in aviso and "identificar_nome" in aviso and "hash" in aviso
    [aviso_se] = abordagens.avisos("saida_estruturada_v3")   # a SE v3 não chama as auxiliares: só o hash muda
    assert "hash" in aviso_se and "identificar_nome" not in aviso_se
    # as ferramentas respondem, só sem conferir o acervo
    assert ferramentas.indice_acervo() is None
    assert "acervo" not in ferramentas.normalizar_codigo("MI 2965-2-NE")
    assert "city='Campinas'" in ferramentas.identificar_nome("Campinas, SP")


def test_v3_sem_a_lista_do_ibge_avisa(sem_indice):
    (sem_indice / "municipios_ibge.json").unlink()
    avisos = abordagens.avisos("tool_calling_v3")
    assert len(avisos) == 2 and "municipios_ibge.json" in avisos[0] and "erro" in avisos[0]


# ---------------------------------------------------------------------------
# pfc (cli.py)
# ---------------------------------------------------------------------------

def test_pfc_abordagens_lista_o_registro(capsys):
    assert cli.main(["abordagens"]) == 0
    saida = capsys.readouterr().out
    assert all(nome in saida for nome in abordagens.NOMES) and "tc3-" in saida
    assert cli.main(["abordagens", "--json", "--hashes"]) == 0
    linhas = json.loads(capsys.readouterr().out)
    assert [x["nome"] for x in linhas] == list(abordagens.NOMES)
    v3c = next(x for x in linhas if x["nome"] == "tool_calling_v3")
    assert v3c["recomendada"] and v3c["ferramenta_sha256"] == rv.hash_ferramenta("tool_calling_v3")
    assert "identificar_nome" in v3c["ferramentas"]
    assert next(x for x in linhas if x["nome"] == "saida_estruturada")["ferramentas"] == []


def test_pfc_delega_ao_cli_existente(tmp_path, monkeypatch):
    (tmp_path / "modulo_falso_pfc.py").write_text(
        "import sys\nVISTO = {}\n"
        "def main(argv=None):\n    VISTO['argv'] = argv\n    VISTO['prog'] = sys.argv[0]\n    return 7\n",
        encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setitem(cli.DELEGADOS, "falso", ("modulo_falso_pfc", "teste"))
    antes = list(sys.argv)
    assert cli.main(["falso", "--modelo", "x", "--sem-sql"]) == 7
    import modulo_falso_pfc

    assert modulo_falso_pfc.VISTO == {"argv": ["--modelo", "x", "--sem-sql"], "prog": "pfc falso"}
    assert sys.argv == antes


def test_pfc_subcomandos_existem_e_desconhecido_falha(capsys):
    import importlib

    for nome, (modulo, _) in cli.disponiveis().items():
        assert callable(importlib.import_module(modulo).main), nome
    assert {"avaliar", "dataset", "relatorio", "auditar", "conferir", "lote", "lote2"} <= set(cli.disponiveis())
    assert cli.main(["xyz"]) == 2
    assert "subcomando desconhecido" in capsys.readouterr().err
    assert cli.main([]) == 0 and "abordagens" in capsys.readouterr().out


def test_pyproject_registra_pfc_sem_remover_os_antigos():
    scripts = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]
    assert scripts["pfc"] == "pfc_busca.cli:main"
    assert {"pfc-avaliar", "pfc-dataset", "pfc-relatorio", "pfc-auditar", "pfc-conferir"} <= set(scripts)
