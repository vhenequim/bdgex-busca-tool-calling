# Busca de geoinformação em linguagem natural com *Tool Calling*

Código, *dataset*, auditoria e resultados do Projeto Final de Curso (PFC) de Engenharia
Cartográfica do Instituto Militar de Engenharia (IME), de Vinicius Henequim Corrêa e
Daniel Santana, com orientação do Prof. Ivanildo Barbosa (DSc).

O trabalho aprimora a **camada de tradução linguística** do
[protótipo de busca do 1º CGEO](https://github.com/1cgeo/prototipo_busca_llm) sobre o
acervo cartográfico da Diretoria de Serviço Geográfico (DSG): a etapa em que uma consulta
livre, como *"mapas do rio em 25k publicados em 2023"*, é convertida nos parâmetros
estruturados de busca do catálogo. A Saída Estruturada do protótipo foi substituída por
*Tool Calling* nativo, com modelos abertos executados localmente pelo Ollama, e a
tradução é avaliada sobre um *dataset* auditado de 310 consultas.

## O que há aqui

| Caminho | Conteúdo |
|---|---|
| `src/pfc_busca/schema.py` | definição da ferramenta `buscar_catalogo`: 12 campos, enumerados e descrições |
| `src/pfc_busca/prompts.py` | *prompt* de sistema, com a data de referência injetada; sem exemplos e sem dicionário |
| `src/pfc_busca/agent.py` | tradução por `ChatOllama.bind_tools()`; *thinking* desativado; falhas classificadas |
| `src/pfc_busca/agent_groq.py` | a mesma tradução via `ChatOpenAI` apontado para o Groq (referência em nuvem) |
| `src/pfc_busca/tools.py`, `db.py` | busca no PostgreSQL/PostGIS, com a lógica SQL portada do protótipo |
| `src/pfc_busca/pipeline.py`, `api.py` | ciclo completo e API FastAPI (`POST /api/search`, `GET /api/health`) |
| `src/pfc_busca/evaluation/` | *dataset*, gabarito com leituras múltiplas, auditoria, execução, métricas e relatório |
| `scripts/generate_dataset_paper.py` | gerador da camada G do *dataset* (semente 42) |
| `docs/manual_de_anotacao.md` | manual que define o gabarito de cada consulta |
| `data/dataset.json` | as 310 consultas com gabarito estruturado |
| `data/auditoria/` | resultado da auditoria, anotação independente, adjudicação e amostra para revisão humana |
| `results/` | registros e manifestos de todas as rodadas (ver abaixo) |
| `notebooks/avaliacao_colab.ipynb` | rodadas completas em GPU de nuvem (Google Colab) |
| `db/` | esquema do banco do protótipo e semente **sintética**, que não entra em nenhuma métrica |
| `tests/` | testes automatizados (`pytest`) |
| `texto/` | fontes LaTeX (abnTeX2) e PDF do texto do PFC |

## O *dataset* e a auditoria

As 310 consultas estão em três camadas: as 22 consultas de teste do protótipo (P), 40
consultas redigidas pelos autores (N) e 248 geradas por modelos de frase sobre catálogos
fechados do domínio (G). O gabarito segue um manual de anotação escrito
(`docs/manual_de_anotacao.md`). Quando uma consulta admite mais de uma leitura razoável,
como *"cartas de São Paulo"* (estado ou município) ou *"últimos 3 meses"* (90 dias ou três
meses de calendário), o gabarito lista todas.

A auditoria tem três etapas, e todos os artefatos estão em `data/auditoria/`:

1. **Checagens automáticas** (`pfc-auditar`): duplicatas, valores inválidos, datas
   relativas resolvidas em várias datas de referência, rastreabilidade das consultas P até
   a linha do arquivo de origem, um anotador por regras que procura no texto a evidência de
   cada campo, e consistência de convenções entre casos.
2. **Anotação independente às cegas**: as 310 consultas foram anotadas do zero, sem acesso
   ao gabarito, por um modelo de linguagem de propósito geral (Claude, da Anthropic), que
   não integra os modelos avaliados, a partir apenas do manual e da definição da ferramenta.
3. **Adjudicação**: cada divergência recebeu uma decisão registrada, com justificativa e
   com o gabarito anterior à decisão (`adjudicacao.json`).

A amostra `revisao_humana_amostra.csv` (40 consultas, semente 42) serve para a conferência
manual do gabarito; quando preenchida, o resultado entra automaticamente no relatório.

## Instalação

Requer Python 3.12 ou superior e, para as rodadas locais, o [Ollama](https://ollama.com).

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; em Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
copy .env.example .env          # em Linux/macOS: cp .env.example .env
```

Modelos avaliados:

```bash
ollama pull qwen3:4b-instruct-2507-q4_K_M
ollama pull gemma4:e4b-it-qat
ollama pull gemma4:e2b-it-qat
ollama pull mistral-nemo:12b
```

O PostGIS é opcional e só serve à execução ponta a ponta da API: `docker compose up -d`.

## Como reproduzir

```bash
pfc-dataset                                   # reconstrói data/dataset.json (mesmo hash em qualquer SO)
pfc-auditar --anotacao-independente data/auditoria/anotacao_independente.json
pfc-avaliar --modelo gemma4:e2b-it-qat --repeticoes 3 --hoje 2026-09-14 --sem-sql
pfc-conferir                                  # confere as rodadas antes de consolidar
pfc-relatorio --modelos qwen3:4b-instruct-2507-q4_K_M,gemma4:e4b-it-qat,gemma4:e2b-it-qat,mistral-nemo:12b
pytest
```

- `pfc-avaliar` grava um registro por consulta e repetição e um manifesto com *tag* e
  *digest* do modelo, versões, *hardware*, VRAM livre, parcela do modelo na GPU e *hashes*
  do *dataset*, do *prompt* e da ferramenta. A rodada é retomável; o comando recusa retomar
  uma rodada feita com outro *prompt*, outra ferramenta ou outro texto de consulta.
- `pfc-relatorio` recalcula a pontuação contra o gabarito vigente, gera as tabelas, figuras
  e estatísticas (intervalo de Wilson, teste de McNemar exato) e, com `--paper DIR`, grava
  os arquivos usados pelo texto do PFC.
- A referência em nuvem usa `pfc-avaliar --provedor groq`, com a variável `GROQ_API_KEY`
  definida no `.env`. Esses resultados são sempre rotulados como execução em nuvem e ficam
  fora do requisito de execução local.
- As rodadas completas em GPU de nuvem usam `notebooks/avaliacao_colab.ipynb` com o pacote
  gerado por `python scripts/empacotar_colab.py`.

## Resultados

| Pasta | Rodada |
|---|---|
| `results/<modelo>/` | rodadas completas dos modelos locais, com Ollama numa GPU NVIDIA T4 |
| `results/estacao/` | validação na estação de referência (RTX 3050 Laptop, 4 GB), camadas P e N |
| `results/groq-*/` | referência em nuvem (Groq) |
| `results/consolidado*/` | tabelas, figuras e estatísticas geradas por `pfc-relatorio` |
| `results/_descartados/` | rodadas substituídas, mantidas para rastreabilidade |

## Decisões de projeto

- **Sem nova tentativa e sem *fallback***: uma chamada malformada, um campo inventado ou uma
  resposta sem chamada é registrada e contada como erro do modelo.
- **Comparação estrita, com leituras múltiplas explícitas**: fora das leituras escritas no
  gabarito, não há tolerância; a resposta é avaliada contra a leitura de melhor casamento.
- **Consultas fora do domínio** têm gabarito "não chamar a ferramenta" e entram nas
  métricas; as poucas consultas cujo comportamento correto não é determinável são
  reportadas à parte.
- **Semente do banco sintética**: prova que a arquitetura fecha ponta a ponta; nenhuma
  métrica depende dela.

## Texto do PFC

`texto/` traz as fontes LaTeX e o PDF (`texto/main.pdf`). As tabelas, figuras e valores
citados no Capítulo 5 são gerados por `pfc-relatorio --paper texto` e `pfc-auditar --paper
texto`; nenhum número de resultado é digitado à mão. Para compilar: `pdflatex main.tex`,
`bibtex main` e mais duas passadas de `pdflatex`, ou `python build.py` (ver `texto/BUILD.md`).

## Licença

MIT (`LICENSE`). Partes derivadas do protótipo do 1º CGEO, licenciado sob MIT pelo
Exército Brasileiro - Diretoria de Serviço Geográfico, estão listadas em
`THIRD_PARTY_NOTICES.md`.
