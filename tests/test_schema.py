from pfc_busca import schema


def test_enums_tem_os_tamanhos_do_apendice_a():
    assert len(schema.ESCALAS) == 8
    assert len(schema.TIPOS_PRODUTO) == 9
    assert len(schema.CENTROS_GEOINFORMACAO) == 5
    assert len(schema.PROJETOS) == 9
    assert len(schema.CAMPOS) == 12


def test_ferramenta_espelha_os_enums():
    props = schema.FERRAMENTA_BUSCAR_CATALOGO["function"]["parameters"]["properties"]
    assert set(props) == set(schema.CAMPOS)
    assert props["scale"]["enum"] is schema.ESCALAS
    assert props["productType"]["enum"] is schema.TIPOS_PRODUTO
    assert props["supplyArea"]["enum"] is schema.CENTROS_GEOINFORMACAO
    assert props["project"]["enum"] is schema.PROJETOS


def test_normalizar_texto():
    assert schema.normalizar_texto("São Paulo") == "sao paulo"
    assert schema.normalizar_texto("  Rio de  Janeiro. ") == "rio de janeiro"
    assert schema.normalizar_texto("SF-22-Y-D") == "sf 22 y d"


def test_parametros_busca_compacta_e_converte_limit():
    p = schema.ParametrosBusca(state="Pará", limit="5", publicationPeriod={"start": "2026-01-01"})
    assert p.compactar() == {"state": "Pará", "limit": 5, "publicationPeriod": {"start": "2026-01-01"}}


def test_parametros_busca_preserva_campo_inventado():
    p = schema.ParametrosBusca(state="Pará", regiao="Norte")
    assert p.compactar()["regiao"] == "Norte"


def test_periodo_vazio_e_descartado():
    p = schema.ParametrosBusca(publicationPeriod={})
    assert p.compactar() == {}
