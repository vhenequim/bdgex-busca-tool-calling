"""Fixtures compartilhadas."""

import shutil

import pytest

from pfc_busca import ferramentas


def _limpar_caches_das_ferramentas():
    for f in (ferramentas.municipios, ferramentas.indice_acervo, ferramentas._chaves_nomes,
              ferramentas._municipios_com_nome_de_uf):
        f.cache_clear()


@pytest.fixture
def sem_indice(tmp_path, monkeypatch):
    """Dados das ferramentas como num clone do repositório: a lista do IBGE, sem o índice de folhas do BDGEx."""
    shutil.copy(ferramentas.DADOS / "municipios_ibge.json", tmp_path / "municipios_ibge.json")
    _limpar_caches_das_ferramentas()
    monkeypatch.setattr(ferramentas, "DADOS", tmp_path)
    yield tmp_path
    _limpar_caches_das_ferramentas()
