-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de estados
CREATE TABLE estados (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    sigla CHAR(2) NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    CONSTRAINT uk_estados_nome UNIQUE (nome),
    CONSTRAINT uk_estados_sigla UNIQUE (sigla)
);

-- Tabela de municípios
CREATE TABLE municipios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sigla_estado CHAR(2) NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL
);

-- Tabela de áreas de suprimento
CREATE TABLE areas_suprimento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    sigla VARCHAR(10) NOT NULL,
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    CONSTRAINT uk_areas_suprimento_nome UNIQUE (nome),
    CONSTRAINT uk_areas_suprimento_sigla UNIQUE (sigla),
    CONSTRAINT ck_areas_suprimento_nome CHECK (
        nome IN (
            '1° Centro de Geoinformação',
            '2° Centro de Geoinformação',
            '3° Centro de Geoinformação',
            '4° Centro de Geoinformação',
            '5° Centro de Geoinformação'
        )
    ),
    CONSTRAINT ck_areas_suprimento_sigla CHECK (
        sigla IN ('1° CGEO', '2° CGEO', '3° CGEO', '4° CGEO', '5° CGEO')
    )
);

-- Tabela principal de datasets
CREATE TABLE datasets (
	id uuid NOT NULL DEFAULT uuid_generate_v4(),
    nome VARCHAR(200) NOT NULL,
    mi VARCHAR(20),
    inom VARCHAR(50),
    escala VARCHAR(10) NOT NULL,
    tipo_produto VARCHAR(50) NOT NULL,
    projeto VARCHAR(100) NOT NULL,
    data_publicacao DATE NOT NULL,
    data_criacao DATE NOT NULL,
    geom GEOMETRY(POLYGON, 4326) NOT NULL,
    texto_busca TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('portuguese', 
            nome || ' ' || 
            COALESCE(mi, '') || ' ' || 
            COALESCE(inom, '') || ' ' || 
            projeto
        )
    ) STORED,
    CONSTRAINT datasets_pk PRIMARY KEY (id)
);

-- Índices
-- Índice GiST para busca textual
CREATE INDEX idx_datasets_texto_busca ON datasets USING gin(texto_busca);

-- Índice GiST para geometrias
CREATE INDEX idx_datasets_geometry ON datasets USING gist(geom);
CREATE INDEX idx_estados_geometry ON estados USING gist(geom);
CREATE INDEX idx_municipios_geometry ON municipios USING gist(geom);
CREATE INDEX idx_areas_suprimento_geometry ON areas_suprimento USING gist(geom);

-- Índices para joins e filtros frequentes
CREATE INDEX idx_datasets_datas ON datasets (data_publicacao, data_criacao);
CREATE INDEX idx_datasets_filters ON datasets (escala, tipo_produto, projeto);

-- Índices específicos para MI e INOM
CREATE INDEX idx_datasets_mi ON datasets(mi);
CREATE INDEX idx_datasets_inom ON datasets(inom);

-- Índices para buscas por nome normalizadas
CREATE INDEX idx_estados_nome_normalizado ON estados(nome);
CREATE INDEX idx_municipios_nome_normalizado ON municipios(nome);