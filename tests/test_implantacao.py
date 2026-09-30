"""Implantação e documentação coerentes com o código: Dockerfile, .dockerignore, docker-compose.yml, CI e docs.

Nada aqui constrói imagem nem sobe serviço (isso é da integração contínua, job `imagem`): só confere que os
arquivos de implantação seguem o registro das abordagens e que a documentação cita comandos e arquivos que
existem.
"""

import re
from pathlib import Path

import pytest

from pfc_busca import abordagens, cli

RAIZ = Path(__file__).resolve().parents[1]
yaml = pytest.importorskip("yaml")   # PyYAML vem com o langchain-core
PADRAO = re.compile(r"\$\{(\w+):-([^}]*)\}")


def _ler(caminho: str) -> str:
    return (RAIZ / caminho).read_text(encoding="utf-8")


def test_dockerignore_nunca_leva_segredos_nem_o_indice_de_folhas():
    linhas = [x.strip() for x in _ler(".dockerignore").splitlines() if x.strip() and not x.startswith("#")]
    assert linhas[0] == "*"   # lista de permissão: só entra o que for reincluído
    assert {"!pyproject.toml", "!README.md", "!LICENSE", "!src"} <= set(linhas)
    assert {"**/.env", "**/.env.*", "**/*.env", "src/pfc_busca/dados/indice_folhas.json"} <= set(linhas)
    # uma exceção depois das exclusões as desfaria
    assert all(not x.startswith("!") for x in linhas[linhas.index("**/.env"):])


def test_dockerfile_sobe_a_api():
    texto = _ler("Dockerfile")
    assert re.search(r"^FROM python:3\.12-slim", texto, re.M)
    assert '"pfc_busca.api:app"' in texto and "/api/health" in texto
    assert not re.search(r"^COPY \. ", texto, re.M)   # só o que o .dockerignore permite, por partes
    from pfc_busca import api

    assert {"/api/health", "/api/search"} <= {r.path for r in api.app.routes}


def test_compose_api_segue_o_registro_e_nao_mexe_no_postgis():
    servicos = yaml.safe_load(_ler("docker-compose.yml"))["services"]
    pg = servicos["postgis"]
    assert pg["image"] == "postgis/postgis:16-3.4" and pg["ports"] == ["127.0.0.1:5433:5432"]
    api = servicos["api"]
    assert api["depends_on"] == {"postgis": {"condition": "service_healthy"}}
    env = api["environment"]
    padroes = {v: p for v, p in (PADRAO.fullmatch(str(x)).groups() for x in env.values() if PADRAO.fullmatch(str(x)))}
    assert padroes["PFC_ABORDAGEM"] == abordagens.RECOMENDADA
    assert padroes["PFC_MODELO_PADRAO"] == abordagens.MODELO_RECOMENDADO
    # variável própria: o OLLAMA_HOST do shell (endereço de escuta do servidor, ex.: 0.0.0.0) não vira URL
    assert "OLLAMA_HOST" not in padroes
    assert padroes["PFC_OLLAMA_URL_DOCKER"].startswith("http://")
    assert env["OLLAMA_BASE_URL"].startswith("${PFC_OLLAMA_URL_DOCKER")
    assert "@postgis:5432/" in env["PFC_DB_DSN"]
    assert all(v.endswith(":ro") for v in api["volumes"])
    assert {v.split(":")[1] for v in api["volumes"]} == {"/app/src/pfc_busca/dados", "/app/results"}


def test_ci_roda_ruff_e_pytest_em_python_312():
    wf = yaml.safe_load(_ler(".github/workflows/testes.yml"))
    passos = wf["jobs"]["testes"]["steps"]
    comandos = "\n".join(p.get("run", "") for p in passos)
    assert any(p.get("with", {}).get("python-version") == "3.12" for p in passos)
    assert 'pip install -e ".[dev]"' in comandos
    assert "ruff check src tests scripts" in comandos and "pytest -q" in comandos and "tests/" in comandos


DOCS = ["README.md", "docs/como_estender.md"]
# citados de propósito sem existir no repositório: não versionado, ou exemplo de versão futura
NAO_VERSIONADOS = {"src/pfc_busca/dados/indice_folhas.json"}
FUTURO = re.compile(r"v4|lote3|lote_validacao_3")
CAMINHO = re.compile(r"(?<![\w/.-])((?:src|scripts|tests|docs|notebooks|data|db)/[\w./-]+?\.(?:py|md|ipynb|json|txt|sql))\b")


@pytest.mark.parametrize("doc", DOCS)
def test_docs_citam_arquivos_que_existem(doc):
    citados = {c for c in CAMINHO.findall(_ler(doc)) if c not in NAO_VERSIONADOS and not FUTURO.search(c)}
    assert citados, doc
    faltam = sorted(c for c in citados if not (RAIZ / c).exists())
    assert not faltam, f"{doc} cita arquivos que não existem: {faltam}"


@pytest.mark.parametrize("doc", DOCS)
def test_docs_citam_comandos_que_existem(doc):
    texto = _ler(doc)
    validos = set(cli.disponiveis()) | {"abordagens", "api"}
    subcomandos = set(re.findall(r"\bpfc (\w+)", texto))
    assert subcomandos and subcomandos <= validos, subcomandos - validos
    import tomllib

    scripts = set(tomllib.loads(_ler("pyproject.toml"))["project"]["scripts"])
    atalhos = {"pfc-" + x for x in re.findall(r"\bpfc-(\w+)\b(?!-)", texto)}
    assert atalhos <= scripts, atalhos - scripts
    assert set(re.findall(r"--abordagem (\w+)", texto)) - {"NOME"} <= set(abordagens.NOMES) | {"tool_calling_v4"}
