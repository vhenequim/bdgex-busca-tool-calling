# API do PFC (pfc_busca.api:app): POST /api/search e GET /api/health.
#
#   docker compose up -d --build api          # com o PostGIS e o Ollama do host (README, "Subir a API")
#   docker build -t pfc-busca-api .           # só a imagem
#
# A imagem leva pyproject.toml, README.md, LICENSE e src/ (ver .dockerignore); nunca o .env nem o
# índice de folhas do BDGEx (src/pfc_busca/dados/indice_folhas.json, não versionado), que o
# docker-compose monta do disco, junto com results/, quando existir.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    OLLAMA_BASE_URL=http://host.docker.internal:11434

WORKDIR /app

# 1) dependências, numa camada que só muda com o pyproject.toml. A instalação é editável de propósito:
#    o registro das abordagens procura results/ ao lado de src/ (pfc_busca.abordagens.RAIZ_REPO), e os
#    dados das ferramentas da v3 ficam em src/pfc_busca/dados/.
COPY pyproject.toml README.md LICENSE ./
RUN mkdir -p src/pfc_busca && touch src/pfc_busca/__init__.py \
    && pip install -e . \
    && rm -rf src

# 2) o código
COPY src ./src

RUN useradd --create-home --uid 1000 pfc
USER pfc

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=15s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=12)"

CMD ["uvicorn", "pfc_busca.api:app", "--host", "0.0.0.0", "--port", "8000"]
