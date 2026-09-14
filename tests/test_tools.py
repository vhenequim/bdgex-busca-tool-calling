"""A SQL é montada pelo código a partir dos parâmetros — nunca pelo modelo."""

from pfc_busca import tools


def test_sem_parametros_lista_tudo_com_limite_padrao():
    contagem, principal, args = tools.montar_sql({})
    assert "WHERE" not in contagem and "WHERE" not in principal
    assert args == []
    assert "ORDER BY data_publicacao DESC LIMIT 10" in principal


def test_filtros_exatos_e_periodo():
    _, principal, args = tools.montar_sql({
        "scale": "1:25.000", "productType": "SCN Carta Ortoimagem", "project": "AMAN",
        "publicationPeriod": {"start": "2023-01-01", "end": "2023-12-31"},
    })
    assert "escala = %s" in principal and "tipo_produto = %s" in principal and "projeto = %s" in principal
    assert "data_publicacao) BETWEEN" in principal
    assert args == ["1:25.000", "SCN Carta Ortoimagem", "AMAN", "2023-01-01", "2023-12-31"]


def test_periodo_so_com_um_limite():
    _, principal, args = tools.montar_sql({"creationPeriod": {"end": "2019-12-31"}})
    assert "data_criacao) <= " in principal and args == ["2019-12-31"]
    _, principal, args = tools.montar_sql({"publicationPeriod": {"start": "2020-01-01"}})
    assert "data_publicacao) >= " in principal and args == ["2020-01-01"]


def test_keyword_usa_seis_argumentos_como_no_prototipo():
    _, principal, args = tools.montar_sql({"keyword": "2965-2-NE"})
    assert principal.count("%s") == 6
    assert args == ["2965-2-NE"] * 5 + ["%2965-2-NE%"]
    assert "websearch_to_tsquery" in principal and "mi = %s" in principal and "inom = %s" in principal


def test_espaciais_usam_tabelas_do_prototipo():
    _, principal, args = tools.montar_sql({
        "state": "Pará", "city": "Belém", "supplyArea": "1° Centro de Geoinformação",
    })
    assert "FROM estados e" in principal and "FROM municipios m" in principal and "FROM areas_suprimento a" in principal
    assert args == ["%Belém%", "%Pará%", "1° Centro de Geoinformação"]


def test_ordenacao_e_limite_do_modelo():
    _, principal, _ = tools.montar_sql({"sortField": "creationDate", "sortDirection": "ASC", "limit": 5})
    assert principal.rstrip().endswith("ORDER BY data_criacao ASC LIMIT 5")


def test_limite_invalido_cai_no_padrao_e_e_teto_100():
    _, principal, _ = tools.montar_sql({"limit": "cinco"})
    assert "LIMIT 10" in principal
    _, principal, _ = tools.montar_sql({"limit": 10_000})
    assert "LIMIT 100" in principal


def test_direcao_invalida_vira_desc():
    _, principal, _ = tools.montar_sql({"sortDirection": "para cima"})
    assert "ORDER BY data_publicacao DESC" in principal
