# Busca de geoinformação em linguagem natural com *Tool Calling*

Código, *datasets*, auditoria, rodadas e análises do Projeto Final de Curso (PFC) de Engenharia
Cartográfica do Instituto Militar de Engenharia (IME), de Vinicius Henequim Corrêa e
Daniel Santana, com orientação do Prof. Ivanildo Barbosa (DSc).

O trabalho aprimora a **camada de tradução linguística** do
[protótipo de busca do 1º CGEO](https://github.com/1cgeo/prototipo_busca_llm) sobre o
acervo cartográfico da Diretoria de Serviço Geográfico (DSG): a etapa em que uma consulta
livre, como *"mapas do rio em 25k publicados em 2023"*, é convertida nos parâmetros
estruturados de busca do catálogo. Duas formas de fazer essa tradução são comparadas, com
modelos abertos executados localmente pelo Ollama:

- **Tool Calling (TC)**: o modelo chama a ferramenta `buscar_catalogo`; na v3, também
  ferramentas auxiliares, e a busca devolve ao modelo erros e avisos de uma validação;
- **Saída Estruturada (SE)**: o modelo responde um JSON com os mesmos parâmetros, como no
  protótipo.

Cada uma é avaliada em três especificações (v1, a solução do Cap. 4; v2; v3) e em três
conjuntos: as 310 consultas auditadas, o lote 1 (1.929 consultas) e o lote 2 (945 consultas,
o conjunto de teste da v3).

> Trabalho acadêmico: não é um produto oficial do BDGEx nem da DSG, e não contém dados do
> acervo real. A busca ponta a ponta roda sobre uma semente sintética do banco.

## Resultados principais

Teste A/B com o Gemma 4 E4B (`gemma4:e4b-it-qat`) na T4, uma observação por consulta
(`results/ab/ab.md`, gerado por `pfc ab`; McNemar exato e IC por *bootstrap* pareado):

| Conjunto | Especificação | Tool Calling | Saída Estruturada | SE − TC (p.p.) [IC 95%] | p |
|---|---|---|---|---|---|
| 310 consultas | v1 | 60,1% | 75,2% | +15,0 [+9,8 a +20,6] | < 0,001 |
| Lote 1 | v1 | 61,5% | 62,2% | +0,7 [−2,4 a +3,8] | 0,656 |
| Lote 1 | v2 | 62,8% | 72,4% | +9,6 [+7,4 a +11,8] | < 0,001 |
| Lote 2 (teste) | v1 | 58,6% | 61,3% | +2,6 [−1,6 a +6,9] | 0,255 |
| Lote 2 (teste) | v2 | 62,1% | 73,8% | +11,6 [+7,9 a +14,9] | < 0,001 |
| **Lote 2 (teste)** | **v3** | **94,4%** | **87,8%** | **−6,6 [−8,9 a −4,2]** | **< 0,001** |
| 310 consultas (desenvolvimento) | v3 | 97,7% | 94,1% | −3,6 [−6,5 a −1,0] | 0,019 |

- Com a especificação de uma chamada (v1 e v2), a Saída Estruturada do Gemma 4 E4B empata com o
  Tool Calling ou o supera. Com a v3, o Tool Calling supera o controle com Saída Estruturada, que
  recebe as mesmas descrições e o mesmo retorno da validação, mas sem as ferramentas auxiliares.
- Nas 310, com a v1, a Saída Estruturada também foi melhor no Qwen 3 4B e no Mistral Nemo 12B e
  empatou no Gemma 4 E2B; na nuvem (Groq), o Tool Calling foi melhor no GPT-OSS 20B e empatou no
  GPT-OSS 120B e no Qwen 3.8 27B, cuja rodada de SE ainda está incompleta (16 pares em
  `results/ab/ab.md`).
- A A/B pontua uma observação por consulta, pela maioria das três repetições do TC v1 nas 310; o
  relatório das 310 (`results/consolidado/comparativo.md`) pontua a média das execuções, e por isso
  dá 60,2% ao mesmo TC v1 do Gemma 4 E4B.
- Degraus do Tool Calling no lote 2 (`results/lote2/consolidado/lote2.md`): v1 58,6% → v2 62,1% →
  descrições v3 75,2% → + ferramentas auxiliares 83,1% → + retorno da validação (v3) 94,4%.
- Custo na T4, no lote 2: latência mediana de 1,47 s (p95 4,96 s) no TC v3, contra 0,78 s
  (2,55 s) na SE v3, com 2,06 contra 1,23 chamadas ao modelo por consulta.
- A v3 foi desenvolvida sobre as 310 consultas e o lote 1: os números dela nesses conjuntos são de
  dentro da amostra. O resultado é o do lote 2, com plano de análise fixado antes da rodada
  (`docs/v3.md`).

Os números do texto do PFC vêm das macros geradas pelas análises (seção "Relatórios e tabelas
do texto"), nunca desta tabela.

## O que há aqui

| Caminho | Conteúdo |
|---|---|
| `src/pfc_busca/schema.py`, `prompts.py`, `agent.py` | v1 do Tool Calling (Cap. 4): a ferramenta `buscar_catalogo` (12 campos), o *prompt* com a data de referência e a tradução por `ChatOllama.bind_tools()` |
| `src/pfc_busca/agent_estruturado.py` | linhas de base com Saída Estruturada (mesmo modelo e *prompt*) e o método do protótipo |
| `src/pfc_busca/agent_groq.py` | a mesma tradução pelo Groq (referência em nuvem) |
| `src/pfc_busca/v2.py`, `v3.py`, `ferramentas.py` | especificações v2 e v3 (degraus da v3, ferramentas auxiliares, validador e o controle com Saída Estruturada) |
| `src/pfc_busca/abordagens.py` | **registro único das abordagens**: nome, família (TC/SE), versão, prefixo das pastas, fábrica do tradutor e *hashes* do manifesto |
| `src/pfc_busca/tools.py`, `db.py` | busca no PostgreSQL/PostGIS, com a lógica SQL portada do protótipo |
| `src/pfc_busca/pipeline.py`, `api.py` | ciclo completo e API FastAPI (`POST /api/search`, `GET /api/health`) |
| `src/pfc_busca/cli.py` | comando único `pfc` |
| `src/pfc_busca/evaluation/` | *dataset*, gabarito, auditoria, execução (`run_evaluation.py`), métricas, relatório das 310 (`report.py`, `comparacao.py`), lotes (`lote.py`, `lote2.py`) e teste A/B (`ab.py`) |
| `scripts/` | geração do *dataset* e das tabelas do texto, pacote do Colab; `lote_validacao/` (construção dos lotes) e `v3/` (ciclo de desenvolvimento da v3) |
| `docs/` | manual de anotação, metodologia dos lotes, desenho e desenvolvimento da v3 e `como_estender.md` (como acrescentar uma versão) |
| `data/` | as 310 consultas (`dataset.json`), os lotes 1 e 2 e a auditoria |
| `results/` | registros e manifestos de todas as rodadas e as análises consolidadas |
| `notebooks/` | cadernos do Google Colab (GPU T4) |
| `db/` | esquema do banco do protótipo e semente **sintética**, que não entra em nenhuma métrica |
| `Dockerfile`, `docker-compose.yml` | imagem da API e os serviços `postgis` e `api` |
| `tests/`, `.github/workflows/testes.yml` | testes automatizados e integração contínua |
| `texto/` | fontes LaTeX (abnTeX2) e PDF do texto do PFC |

## Instalação

Requer Python 3.12 ou superior; para as rodadas locais e a API, o [Ollama](https://ollama.com);
para o banco e a API em contêiner, o Docker.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; em Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
copy .env.example .env          # em Linux/macOS: cp .env.example .env
```

Modelos avaliados (o primeiro é o da API):

```bash
ollama pull gemma4:e4b-it-qat
ollama pull gemma4:e2b-it-qat
ollama pull qwen3:4b-instruct-2507-q4_K_M
ollama pull mistral-nemo:12b
```

Depois de atualizar o código, `pip install -e .` recria os atalhos (`pfc`, `pfc-avaliar`,
`pfc-conferir`, `pfc-ab`...); sem reinstalar, `python -m pfc_busca.cli <subcomando>` faz o mesmo.

**Índice de folhas do BDGEx.** As ferramentas da v3 consultam `src/pfc_busca/dados/indice_folhas.json`,
que não é versionado (é derivado dos metadados públicos do BDGEx, cuja política não trata de
redistribuição). Ele é gerado por `python scripts/v3/gerar_dados_ferramentas.py` a partir da coleta
(`scripts/lote_validacao/coletar_bdgex.py`) ou copiado do pacote do Colab. Sem ele, a v3 funciona em
modo degradado: as ferramentas deixam de reconhecer nomes de folha e de conferir códigos no acervo, e o
*hash* da configuração deixa de coincidir com o das rodadas avaliadas (o arquivo entra nele).

## Testes

```bash
pytest -q tests/
ruff check src tests scripts
```

Nenhum teste chama o Ollama, o Groq ou o banco: a API é testada com o `TestClient` e tradutores
falsos, e os construtores com o Ollama simulado. Sem o índice de folhas, os 4 testes que conferem os
*hashes* das rodadas da v3 (`tests/test_regressao_abordagens.py`) são pulados. O teste de regressão
confere que o código atual reproduz os nomes, os prefixos e os *hashes* de *prompt* e de ferramenta
de todas as rodadas válidas em `results/`.

A integração contínua (`.github/workflows/testes.yml`) roda, a cada *push* e *pull request*, o
`ruff` e o `pytest` em Python 3.12 e constrói a imagem da API, que precisa subir e responder o
`/api/health` sem Ollama e sem banco.

## Subir a API

A API recebe `{"query": "..."}` em `POST /api/search` e devolve os parâmetros extraídos, as chamadas
de ferramenta, os produtos encontrados (na semente sintética) e as latências de cada etapa. A
configuração vem de variáveis de ambiente (ou do `.env`):

| Variável | Padrão | O que define |
|---|---|---|
| `PFC_ABORDAGEM` | `tool_calling_v3` | a abordagem do registro (`pfc abordagens` lista todas) |
| `PFC_MODELO_PADRAO` | `gemma4:e4b-it-qat` | a *tag* do Ollama |
| `PFC_PERMITIR_MODELO` | `0` | `1` aceita `model` na requisição (só em desenvolvimento) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | o servidor do Ollama |
| `PFC_DB_DSN` | `postgresql://postgres:pfc@localhost:5433/geospatial_search` | o banco; sem banco, a API só traduz |

O padrão é a configuração que a tese recomenda, avaliada no lote 2 e nas 310 com esse modelo. As
abordagens do registro:

| Abordagem | Família | Especificação | Pasta das rodadas |
|---|---|---|---|
| `tool_calling` | TC | v1, a solução do Cap. 4 | `results/<modelo>/` |
| `saida_estruturada` | SE | v1 (linha de base) | `se-` |
| `prototipo` | SE | método do protótipo (linha de base) | `prototipo-` |
| `tool_calling_v2`, `saida_estruturada_v2` | TC, SE | v2 | `tc2-`, `se2-` |
| `tool_calling_v3d`, `tool_calling_v3a` | TC | degraus da v3 (descrições; + ferramentas auxiliares) | `tc3d-`, `tc3a-` |
| `tool_calling_v3` | TC | v3 completa (**recomendada**) | `tc3-` |
| `saida_estruturada_v3` | SE | controle da v3 | `se3-` |

**Local:**

```bash
docker compose up -d postgis     # opcional: o banco com a semente sintética
pfc api                          # = uvicorn pfc_busca.api:app --port 8000 (a recomendada)
pfc api --abordagem tool_calling --modelo qwen3:4b-instruct-2507-q4_K_M   # a v1 do Cap. 4
curl http://127.0.0.1:8000/api/health
curl -X POST http://127.0.0.1:8000/api/search -H "Content-Type: application/json" \
     -d '{"query": "cartas de São Paulo em 25k"}'
```

No PowerShell: `Invoke-RestMethod http://127.0.0.1:8000/api/search -Method Post -ContentType
"application/json; charset=utf-8" -Body '{"query": "cartas de São Paulo em 25k"}'`.

**Com o Docker Compose** (serviços `postgis` e `api`; o Ollama continua no host):

```bash
docker compose up -d --build
docker compose logs -f api
PFC_ABORDAGEM=tool_calling PFC_MODELO_PADRAO=qwen3:4b-instruct-2507-q4_K_M docker compose up -d api
```

- A abordagem e o modelo vêm de `PFC_ABORDAGEM` e `PFC_MODELO_PADRAO`, do *shell* ou do `.env` da
  pasta do projeto, que o Compose lê.
- `PFC_OLLAMA_URL_DOCKER` é a URL do Ollama do host vista de dentro do contêiner; o padrão é
  `http://host.docker.internal:11434`. No Linux, o Ollama precisa escutar fora do *loopback*
  (`OLLAMA_HOST=0.0.0.0:11434` no serviço do Ollama); o `OLLAMA_HOST` do *shell* não interfere no
  Compose, que só lê `PFC_OLLAMA_URL_DOCKER`.
- A imagem não leva o `.env` nem o índice de folhas; o Compose monta, só para leitura,
  `src/pfc_busca/dados/` (com o índice, se ele existir no disco) e `results/`.

**Qual configuração está no ar.** `GET /api/health` informa a abordagem, a família, a versão, o
modelo, os *hashes* de *prompt* e de ferramenta (os mesmos do manifesto de cada rodada) e as rodadas
de `results/` feitas com essa mesma configuração. Uma lista vazia quer dizer que a combinação nunca
foi avaliada (por exemplo, a v3 com um modelo em que ela não rodou, ou sem o índice de folhas). Um
nome de abordagem fora do registro impede a subida; um dado ausente põe a API em modo degradado, com
aviso no *log*, no `/api/health` e em cada resposta.

## Avaliar um modelo ou uma abordagem

`pfc avaliar` (o mesmo que `pfc-avaliar`) roda uma abordagem com um modelo sobre um conjunto e grava
em `<saída>/<prefixo><modelo>/`:

```bash
pfc avaliar --modelo gemma4:e2b-it-qat --repeticoes 3 --hoje 2026-09-14 --sem-sql      # TC v1 nas 310
pfc avaliar --modelo gemma4:e4b-it-qat --abordagem saida_estruturada_v3 \
            --hoje 2026-09-14 --sem-sql --saida results/v3_310                          # SE v3 nas 310
pfc avaliar --modelo gemma4:e4b-it-qat --abordagem tool_calling_v3 --origem P,N --limite 20 \
            --sem-sql --saida results/_fumaca                                            # fumaça
pfc avaliar --provedor groq --modelo openai/gpt-oss-20b --sem-sql                        # nuvem (GROQ_API_KEY)
pfc conferir results/v3_310/*                                                            # antes de consolidar
```

- Pastas de `results/` cujo nome começa com `_` (descartadas, fumaça) ou `dev_` (ciclos de
  desenvolvimento) ficam fora da conferência de *hashes* dos testes e das rodadas listadas pelo
  `/api/health`; `results/_fumaca/` não é versionada.
- `--abordagem` tem padrão `tool_calling` (a v1), ao contrário da API; `--dataset` troca o conjunto
  (por exemplo, `data/lote_validacao.json`); `--ids`, `--origem`, `--familias` e `--limite` restringem
  as consultas; `--hoje` fixa a data de referência, injetada no *prompt* e usada no gabarito.
- Cada execução vira uma linha de `execucoes.jsonl`; o `manifesto.json` guarda *tag* e *digest* do
  modelo, versões, *hardware*, VRAM livre, parcela do modelo na GPU e os *hashes* do *dataset*, do
  *prompt* e da ferramenta. A rodada é retomável com o mesmo comando, e o avaliador se recusa a retomar
  uma rodada feita com outro *prompt*, outra ferramenta, outro texto de consulta ou outra data.
- O resumo é sempre recalculado contra o gabarito vigente (`--so-resumir` só recalcula).
- `pfc conferir` (`pfc-conferir`) confere *hashes*, completude, duplicatas, erros de infraestrutura
  e a data de referência de cada rodada, e sai com código 1 se houver problema bloqueante.
- No Groq só rodam `tool_calling` e `saida_estruturada`; esses resultados são sempre rotulados como
  execução em nuvem e ficam fora do requisito de execução local.
- O lote 2 é o conjunto de teste: não o use para desenvolver uma versão (`docs/como_estender.md`).

## Relatórios e tabelas do texto

Cada análise lê as rodadas de `results/`, grava a sua consolidação ao lado delas e, com `--paper DIR`,
copia as tabelas e as macros para `DIR/tabelas/`. Para regenerar tudo o que o texto usa:

```bash
python scripts/gerar_tabelas_texto.py --texto ../paper_revisado   # Apêndice A, auditoria, 310, estação, nuvem, TC × SE
pfc lote  --paper ../paper_revisado       # lote 1 e v2          -> results/lote/consolidado/
pfc lote2 --paper ../paper_revisado       # lote 2 e v3          -> results/lote2/consolidado/
pfc ab    --paper ../paper_revisado       # teste A/B TC × SE    -> results/ab/
python scripts/v3/validador_no_gabarito.py --tex                  # autoteste do validador (numeros_v3)
python scripts/sincronizar_texto.py       # copia fontes, tabelas e PDF para texto/
```

- `scripts/gerar_tabelas_texto.py` chama `pfc dataset --apendice`, `pfc auditar --paper`,
  `pfc relatorio` (rodadas das 310, estação, reexecução e nuvem com rodada completa) e
  `pfc comparacao`, mas não `lote`, `lote2` nem `ab`, que vêm em seguida. O destino padrão é
  `../paper_revisado`, a pasta de trabalho do texto; num clone só do repositório, use `texto`.
- `pfc relatorio` também roda sozinho: `pfc relatorio --modelos qwen3:4b-instruct-2507-q4_K_M,gemma4:e4b-it-qat`
  gera tabelas, figuras e estatísticas (IC de Wilson, McNemar exato) em `results/consolidado/`.
- `pfc ab --estrito` sai com código 1 se algum número divergir, sem causa conhecida, da macro que o
  texto já usa para o mesmo par.
- As macros de dados dos lotes (`numeros_lote_dados`, `numeros_lote2_dados`) vêm de
  `scripts/lote_validacao/montar_lote.py`, que só roda quando um lote é reconstruído.

Nenhum número de resultado é digitado à mão no texto: cada valor é uma macro
`\res{conjunto}{configuração}{medida}` de um `numeros_*.tex`, carregado no `main.tex` por
`\carregarnumeros{...}`, e cada tabela gerada entra por `\tabelagerada{nome}{descrição}`.

## Conjuntos

| Conjunto | Arquivo | Consultas | Papel | Data de referência |
|---|---|---|---|---|
| 310 consultas | `data/dataset.json` | 310 (306 pontuadas; 4 observacionais à parte) | resultado do Cap. 5 (v1); desenvolvimento da v2 e da v3 | 2026-09-14 |
| Lote 1 | `data/lote_validacao.json` | 1.929 | validação independente da v1; teste da v2; desenvolvimento da v3 (amostra de 160 em `data/lote_validacao/dev_v3_ids.txt`) | 2026-09-24 |
| Lote 2 | `data/lote_validacao_2.json` | 945 | **teste** da v3, com plano de análise fixado antes da rodada; nenhuma consulta dele foi lida no desenvolvimento | 2026-09-24 |

Os lotes têm o gabarito definido antes da consulta (alvos sorteados de catálogos reais do BDGEx e do
IBGE), redação controlada e anotação às cegas com filtro de concordância (`docs/lote_validacao.md`).
O lote 2 segue a mesma receita, com outra semente e outros redatores e anotadores
(`PFC_LOTE=2` nos scripts de `scripts/lote_validacao/`).

## Rodadas em `results/`

| Pasta | Rodada |
|---|---|
| `results/<modelo>/` | TC v1 nas 310 com os quatro modelos locais, três repetições, Ollama numa GPU de nuvem (Google Colab, T4 de 16 GB); só a GPU é alugada, nenhum serviço de LLM é usado |
| `results/se-<modelo>/`, `results/prototipo-phi4-14b/` | linhas de base nas 310: SE v1 e método do protótipo, uma repetição, T4 |
| `results/estacao/` | estação de referência (RTX 3050 Laptop, 4 GB), camadas P e N, TC v1 e SE v1 |
| `results/groq-*/`, `results/groq-se-*/` | referência em nuvem (Groq): GPT-OSS 20B e 120B e Qwen 3.8 27B |
| `results/v2_310/` | TC v2 e SE v2 nas 310 (desenvolvimento) |
| `results/lote/` | lote 1: TC v1, SE v1, TC v2 e SE v2 (Gemma 4 E4B, T4) |
| `results/dev_v3/` | ciclos de desenvolvimento da v3 (160 consultas do lote 1, Gemma 4 E4B local) |
| `results/lote2/` | lote 2: TC v1, v2, v3d, v3a e v3; SE v1, v2 e v3 (Gemma 4 E4B, T4) |
| `results/v3_310/` | TC v3 e SE v3 nas 310 (desenvolvimento) |
| `results/ab/` | teste A/B TC × SE (`pfc ab`) |
| `results/consolidado*/`, `results/*/consolidado/` | tabelas, figuras e estatísticas das análises |
| `results/_descartados/` | rodadas substituídas, mantidas para rastreabilidade |

## Cadernos do Colab

As rodadas na T4 rodam o mesmo `pfc-avaliar` num Colab, com o pacote gerado por
`python scripts/empacotar_colab.py` (`dist/pfc_busca_colab.zip`). Antes de empacotar, o script grava nos
cadernos os *hashes* dos conjuntos vigentes, e o caderno se recusa a rodar com um pacote que não seja
esse. O resultado volta num *zip*, a ser descompactado na pasta que contém `pfc_busca/`.

| Caderno | Rodadas |
|---|---|
| `notebooks/avaliacao_colab.ipynb` | TC v1 nas 310, quatro modelos locais |
| `notebooks/linha_de_base_colab.ipynb` | SE v1 (quatro modelos) e método do protótipo (Phi-4 14B) nas 310 |
| `notebooks/lote_validacao_colab.ipynb` | lote 1 e v2 nas 310 |
| `notebooks/lote2_v3_colab.ipynb` | teste da v3 no lote 2 (degraus, controle e referências) e v3 nas 310; confere o *hash* da v3 pré-registrada (`scripts/v3/gerar_notebook_lote2.py`) |
| `notebooks/lote2_v3_modelos_colab.ipynb` | extensão pré-registrada: a mesma v3 com Gemma 4 E2B e Qwen 3 4B no lote 2 (`gerar_notebook_lote2.py --modelos`) |

## Acrescentar uma versão de TC ou de SE

Uma versão nova entra por um lugar só, o registro `src/pfc_busca/abordagens.py`: escreva o tradutor
num módulo próprio (`traduzir(consulta, hoje) -> Traducao`), acrescente uma entrada `Abordagem(...)`
com nome e prefixo novos e rode os testes. A partir daí, `pfc avaliar --abordagem <nome>` e
`PFC_ABORDAGEM=<nome>` passam a aceitá-la. Os módulos das versões avaliadas (`agent`,
`agent_estruturado`, `v2`, `v3`, `ferramentas`, `schema`, `prompts`) não mudam: os *hashes* das
rodadas dependem do texto deles.

O caminho completo, do desenvolvimento ao texto, com os cuidados que a tese aprendeu (conjunto de
teste intocado, pré-registro, contaminação, efeito de menção), está em
[`docs/como_estender.md`](docs/como_estender.md).

## O *dataset* e a auditoria

As 310 consultas estão em três camadas: as 22 consultas de teste do protótipo (P), 40
consultas redigidas pelos autores (N) e 248 geradas por modelos de frase sobre catálogos
fechados do domínio (G). O gabarito segue um manual de anotação escrito
(`docs/manual_de_anotacao.md`). Quando uma consulta admite mais de uma leitura razoável,
como *"cartas de São Paulo"* (estado ou município) ou *"últimos 3 meses"* (90 dias ou três
meses de calendário), o gabarito lista todas.

A auditoria tem três etapas, e todos os artefatos estão em `data/auditoria/`:

1. **Checagens automáticas** (`pfc auditar`): duplicatas, valores inválidos, datas
   relativas resolvidas em várias datas de referência, rastreabilidade das consultas P até
   a linha do arquivo de origem, um anotador por regras que procura no texto a evidência de
   cada campo, e consistência de convenções entre casos.
2. **Anotação independente às cegas**: as 310 consultas foram anotadas do zero, sem acesso
   ao gabarito, por um modelo de linguagem de propósito geral (Claude, da Anthropic), que
   não integra os modelos avaliados, a partir apenas do manual e da definição da ferramenta.
3. **Adjudicação**: cada divergência recebeu uma decisão registrada, com justificativa e
   com o gabarito anterior à decisão (`adjudicacao.json`).

Por fim, uma amostra estratificada de 40 consultas (`revisao_humana_amostra.csv`, semente 42)
foi conferida manualmente por um dos autores, sem divergência com o gabarito.

```bash
pfc dataset                                   # reconstrói data/dataset.json (mesmo hash em qualquer SO)
pfc auditar --anotacao-independente data/auditoria/anotacao_independente.json
```

## Decisões de projeto

- **Sem nova tentativa e sem *fallback* na v1**: uma chamada malformada, um campo inventado ou uma
  resposta sem chamada é registrada e contada como erro do modelo. Na v3, o retorno da validação é
  parte da especificação avaliada, e o controle com Saída Estruturada recebe o mesmo retorno.
- **Comparação estrita, com leituras múltiplas explícitas**: fora das leituras escritas no
  gabarito, não há tolerância; a resposta é avaliada contra a leitura de melhor casamento.
- **Consultas fora do domínio** têm gabarito "não chamar a ferramenta" e entram nas
  métricas; as poucas consultas cujo comportamento correto não é determinável são
  reportadas à parte.
- **Semente do banco sintética**: prova que a arquitetura fecha ponta a ponta; nenhuma
  métrica depende dela.

## Texto do PFC

`texto/` traz as fontes LaTeX e o PDF (`texto/main.pdf`), copiados da pasta de trabalho do texto por
`python scripts/sincronizar_texto.py`. As tabelas, figuras e valores citados nos resultados são
gerados pelos comandos da seção "Relatórios e tabelas do texto"; nenhum número de resultado é
digitado à mão. Para compilar: `pdflatex main.tex`, `bibtex main` e mais duas passadas de
`pdflatex`, ou `python build.py` (ver `texto/BUILD.md`).

## Licença

Código, *dataset* e artefatos de avaliação: MIT (`LICENSE`). O texto do PFC (`texto/`) segue
os termos de uso do IME impressos no verso da folha de rosto. Partes derivadas do protótipo do 1º CGEO, licenciado sob MIT pelo
Exército Brasileiro - Diretoria de Serviço Geográfico, estão listadas em
`THIRD_PARTY_NOTICES.md`.
