# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-30T20:59:26

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 59.3% |
| Precisão ponderada | 0.858 |
| Recall ponderado | 0.699 |
| F1 ponderado | 0.744 |
| F1 macro | 0.746 |
| Micro P / R / F1 | 0.775 / 0.699 / 0.735 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 3570 | 11330 | 18383 | 64927 | 89128 | 18529 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 19 | 14 | 0 | 5 | 1.000 | 0.737 | 0.848 |
| scale | 14 | 6 | 0 | 8 | 1.000 | 0.429 | 0.600 |
| productType | 14 | 8 | 0 | 6 | 1.000 | 0.571 | 0.727 |
| state | 15 | 10 | 0 | 5 | 1.000 | 0.667 | 0.800 |
| city | 6 | 5 | 1 | 1 | 0.833 | 0.833 | 0.833 |
| supplyArea | 11 | 8 | 0 | 3 | 1.000 | 0.727 | 0.842 |
| project | 4 | 4 | 2 | 0 | 0.667 | 1.000 | 0.800 |
| publicationPeriod | 14 | 14 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| creationPeriod | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortField | 10 | 6 | 8 | 4 | 0.429 | 0.600 | 0.500 |
| sortDirection | 10 | 5 | 9 | 4 | 0.357 | 0.556 | 0.435 |
| limit | 6 | 4 | 5 | 1 | 0.444 | 0.800 | 0.571 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 72.7% | 0.818 |
| Compostas | 43 | 51.2% | 0.724 |
| Código MI/INOM | 15 | 80.0% | 0.901 |
| Tempo relativo | 15 | 73.3% | 0.880 |
| Ordenação | 10 | 30.0% | 0.760 |
| Ambíguas/informais | 35 | 54.3% | 0.737 |
| Fora do domínio | 2 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 50.0% |
| N | 37 | 64.9% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 8, 'misto': 11, 'campo_omitido': 4, 'valor_errado': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 8

## Observacionais (fora das métricas principais)

3 casos · acurácia 66.7% · chamou sem dever: 0
