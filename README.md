# pfc_busca — camada de tradução linguística com Tool Calling (PFC · IME)

Reimplementação, em Python, da camada que converte uma consulta em português
("mapas do rio em 25k publicados em 2023") nos parâmetros estruturados de
busca do catálogo cartográfico da DSG — via **Tool Calling** nativo em modelos
locais (Ollama), com avaliação sistemática sobre 310 consultas anotadas.

Contexto, metodologia e protocolo: `../paper_revisado/` (Cap. 3 e 4, Apêndice A).

## O que há aqui

| Caminho | Papel |
|---|---|
| `src/pfc_busca/schema.py` | fonte única dos 12 campos, enums e da ferramenta `buscar_catalogo` (schema JSON) |
| `src/pfc_busca/prompts.py` | prompt de sistema (data injetada; sem few-shot, sem dicionário) |
| `src/pfc_busca/agent.py` | `Tradutor`: `ChatOllama.bind_tools()` → tool call; thinking desativado; falhas viram métrica |
| `src/pfc_busca/tools.py` | `buscar_catalogo`: SQL parametrizada portada do protótipo (PostGIS) |
| `src/pfc_busca/pipeline.py` | ponta a ponta: tradução → SQL → (resposta final) |
| `src/pfc_busca/api.py` | FastAPI `POST /api/search` (RF1–RF5) |
| `src/pfc_busca/evaluation/` | dataset (`dataset_builder.py`, `manual_cases.py`, `relative_time.py`), `metrics.py`, `run_evaluation.py` |
| `data/dataset.json` | as 310 consultas com gabarito estruturado (gerado; confere com o Apêndice A) |
| `db/` | schema do protótipo + semente **sintética** rotulada |
| `results/<modelo>/` | execuções (`.jsonl`), manifesto de reprodutibilidade, resumos |
| `scripts/` | cópia do gerador do paper (mesma semente 42) e gerador da semente |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

Ollama ≥ 0.34 aberto, com os modelos:

```bash
ollama pull qwen3:4b
ollama pull gemma4:e4b-it-qat
ollama pull gemma4:e2b-it-qat
ollama pull mistral-nemo:12b
```

PostGIS (opcional — só para a execução ponta a ponta; nenhuma métrica depende dele):

```bash
docker compose up -d
```

## Uso

```bash
pfc-dataset --verificar ../paper_revisado/apendice_dataset_gerado.tex   # (re)gera data/dataset.json
pfc-avaliar --modelo qwen3:4b --origem P,N --limite 20                    # rodada-fumaça
pfc-avaliar --modelo qwen3:4b --repeticoes 3                              # protocolo completo (F6)
uvicorn pfc_busca.api:app --port 8000                                     # API
pytest
```

`pfc-avaliar` é retomável: interrompeu, roda o mesmo comando de novo.

## Decisões que valem saber

- **Enums seguem o paper**, não o protótipo ("SCN Carta Topográfica Matricial", "MDT — RAM", 9 tipos).
  A recuperação em nível de produto está fora do escopo; a referência é o Apêndice A.
- **Tempo relativo** é resolvido em tempo de execução pela mesma data injetada no prompt
  (`relative_time.py` documenta cada convenção).
- **Casos observacionais** (fronteira N36–N40, GF*, e N34) ficam fora das métricas principais
  e são reportados à parte.
- **Sem retry, sem fallback**: uma tool call malformada, um campo inventado ou um timeout
  são registrados e contados. É a decisão de projeto do Cap. 4 (limitação 5).
- **Semente do banco é sintética** (retângulos numa grade). Serve para provar que a
  arquitetura fecha, não para medir nada.
- **LangChain 1.x**: usa-se `bind_tools()` direto, sem `AgentExecutor` (removido na 1.x);
  a tradução é uma única decisão do modelo, que é exatamente o objeto da avaliação.
