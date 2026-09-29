# Desenvolvimento da v3: ciclos, decisões e o que foi descartado

Registro do que mudou em cada ciclo de desenvolvimento da v3 (docs/v3.md) e por quê. Tudo aqui vem dos
conjuntos de DESENVOLVIMENTO: as 310 consultas e o lote 1 (1.929 consultas), com a amostra estratificada de
160 consultas do lote 1 em `data/lote_validacao/dev_v3_ids.txt` (semente 2030). O lote 2 (teste) não é lido.

> **Atenção à leitura dos números.** Todos os números deste documento são de dentro da amostra: cada ciclo
> corrige erros observados nessas mesmas 160 consultas, e o resultado do ciclo seguinte nelas é otimista por
> construção. Eles registram o processo; o resultado da v3 é o do lote 2 (docs/v3.md, plano de análise).

## Protocolo de cada ciclo

1. Rodar as configurações no desenvolvimento: `python scripts/v3/ciclo_dev.py --ciclo N --rodar ...`
   (Gemma 4 E4B local, mesmo arquivo de modelo da T4, data de referência 2026-09-24, sem SQL). O resumo
   compara com as rodadas v1/v2 da T4 e com a arquitetura em duas etapas simulada, nas mesmas 160 consultas.
2. Listar os erros: `python scripts/v3/erros_ciclo.py --ciclo N --config tc3- --comparar t4:se-`.
3. Agrupar os erros grosseiros e decidir onde a correção mora: no **código** (validador, ferramentas
   auxiliares, laço), quando a regra é determinística e verificável na consulta; no **prompt**, só para o
   uso das ferramentas (quando chamar qual).
4. Antes de rodar o ciclo seguinte, duas checagens baratas:
   - autoteste do validador contra as respostas certas (`scripts/v3/validador_no_gabarito.py`): o
     validador não pode reclamar de nenhuma leitura preferencial do gabarito do lote 1 nem das 310;
   - reaplicação do validador novo às respostas do ciclo anterior (`scripts/v3/replay_validador.py`):
     quantos erros ele pegaria e quantas respostas certas ele alarmaria (tem de ser zero).
5. Medir de onde vem o acerto (`scripts/v3/decompor_ganho.py`): primeira decisão do modelo × resposta final
   depois do retorno.

## Ciclo 0 — referências (rodadas da T4 restritas às 160 consultas)

| Configuração | Acurácia | Domínio | Falsa recusa | Recusa F |
|---|---|---|---|---|
| tc1 | 58,1% | 50,4% | 31,9% | 100% |
| se1 | 69,4% | 75,6% | 0,0% | 0% |
| tc2 | 58,1% | 51,9% | 2,2% | 100% |
| se2 | 72,5% | 67,4% | 14,1% | 100% |
| duas etapas (tc2 decide, se1 extrai) | 78,1% | 74,8% | 2,2% | 100% |

## Ciclo 1 — ferramentas auxiliares, validação e orientações

Configuração: descrições v3, ferramentas auxiliares, validação com retorno, `pedir_esclarecimento` e 13
"orientações" — regras curtas escritas a partir dos erros das rodadas v1/v2 do lote 1, em markdowns com
frontmatter, injetadas no prompt quando um gatilho casava com a consulta (arquivadas em
`experimentos/orientacoes/`).

Autoteste do validador: a primeira versão alarmava 51 das 1.593 respostas certas do lote 1 ("carta 1:25.000"
lida como código, ", se possível" lido como Sergipe, "1:2000" lido como ano, singular sem artigo, sigla
minúscula, nome de folha com nome de UF, INOM "sc-20", sufixo do MI); depois das correções, 0 de 1.593 e 0 de 298.

Resultado: **87,5%** de acurácia (primeira decisão do modelo 78,8%; o retorno consertou 14 e não estragou
nenhuma), 85,2% no domínio, falsa recusa 3,7%, recusa F 100%.

Erros (20 de 160), em grupos:

| Grupo | n | Exemplo (padrão) | Correção para o ciclo 2 |
|---|---|---|---|
| período com data errada (conta de cabeça, sem `resolver_periodo`) | 6 | "últimos 3 anos" → começo um ano adiante | validador: confere o período com a tabela do manual; prompt: "chame resolver_periodo, sem conta de cabeça" |
| campo do período trocado ou duplicado pelo verbo | 5 | "feitas antes de 2010" → publicationPeriod | validador: aviso de verbo de criação/publicação |
| recusa com critério do catálogo na consulta | 3 | "ortoimagens … pra uma obra"; município pequeno tomado por estrangeiro | recusa contestada uma vez quando há critério forte; prompt: "nome que você não reconhece não é motivo de recusa" |
| resposta sem chamada | 2 | pergunta escrita em texto; resposta vazia duas vezes | pergunta em texto recebe a resposta do usuário simulado |
| UF ou município citado e ausente | 3 | "mapa de Sergipe" → {}; "folha X, de Tesouro (MT)" sem city | validador: UF por nome, "município (UF)", município depois de de/em |
| sigla como keyword | 1 | "PB" em keyword | validador: erro "keyword é UF" |

Também foram revistas três orientações (período com exemplos em data fictícia; duas novas sobre finalidade
declarada e lugar desconhecido). Reaplicação do validador do ciclo 2 às respostas do ciclo 1: pegaria 15 das
15 buscas erradas, com 0 alarmes nas certas.

## Ciclo 2 — com e sem orientações, e o controle

| Configuração | Acurácia | 1ª decisão | Retorno consertou / estragou | Falsa recusa | Recusa F |
|---|---|---|---|---|---|
| TC v3 com orientações | 96,9% | 82,5% | 23 / 0 | 0,0% | 100% |
| **TC v3 sem orientações** (configuração congelada) | **96,9%** | **85,6%** | 18 / 0 | 0,7% | 100% |
| SE v3 com orientações (controle da época) | 93,1% | 78,8% | 23 / 0 | 2,2% | 100% |

- Com × sem orientações: 4 × 4 consultas discordantes (McNemar p = 1,0). **As orientações não mudaram o
  resultado**, e a primeira decisão do modelo foi melhor sem elas.
- TC v3 sem orientações × SE v3: 10 × 4 (p = 0,18).
- Quase todo o ganho do ciclo 1 para o 2 veio do retorno do validador (primeira decisão +3,7 pp; final
  +9,4 pp). Das 23 consultas consertadas pelo retorno na configuração com orientações, cerca de 8 o validador
  resolveu dando o valor (UF, município, datas), cerca de 11 mandando remover um campo sem evidência (tipo de
  produto a partir de "cartas", limite sem número, estado não citado) e cerca de 4 corrigindo a forma.

**Decisão: retirar as orientações.** Não acrescentaram nada mensurável e são a parte do desenho mais exposta
a sobreajuste (regras escritas por rodadas sobre os erros do desenvolvimento). A v3 congelada é a
configuração sem orientações do ciclo 2, com o mesmo prompt e as mesmas ferramentas (conferido byte a byte),
reorganizada em degraus (`tool_calling_v3d` → `tool_calling_v3a` → `tool_calling_v3`) com o controle
`saida_estruturada_v3` também sem orientações. Não houve ciclo 3: os 5 erros restantes da configuração congelada
(escala qualitativa "maior que 100k" → 1:250.000; folha com nome de município preenchida também como city;
duas perguntas ao usuário e nenhuma busca; `limit = 1` num plural; três chamadas malformadas) ficaram como
estão, para não ajustar mais a v3 a estas 160 consultas. Em três deles o validador não emitiu aviso: são
lacunas conhecidas do código, e o lote 2 mostrará quanto pesam.

Correspondência das pastas de desenvolvimento com os nomes atuais: `ciclo1/tc3-` e `ciclo2/tc3-` = TC v3 com
orientações; `ciclo2/tc3f-` = a `tool_calling_v3` congelada; `ciclo2/se3-` = controle com orientações.
