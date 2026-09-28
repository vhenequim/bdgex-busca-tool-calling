# qwen/qwen3.8-27b — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-28T17:08:27

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 95.1% |
| Precisão ponderada | 0.974 |
| Recall ponderado | 0.994 |
| F1 ponderado | 0.984 |
| F1 macro | 0.982 |
| Micro P / R / F1 | 0.974 / 0.994 / 0.984 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 512 | 695 | 845 | 1365 | 12717 | 800 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 62 | 62 | 1 | 0 | 0.984 | 1.000 | 0.992 |
| scale | 84 | 83 | 1 | 0 | 0.988 | 1.000 | 0.994 |
| productType | 44 | 44 | 2 | 0 | 0.957 | 1.000 | 0.978 |
| state | 130 | 128 | 3 | 1 | 0.977 | 0.992 | 0.985 |
| city | 27 | 27 | 1 | 0 | 0.964 | 1.000 | 0.982 |
| supplyArea | 40 | 40 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 51 | 47 | 4 | 0 | 0.922 | 1.000 | 0.959 |
| creationPeriod | 10 | 9 | 1 | 0 | 0.900 | 1.000 | 0.947 |
| sortField | 29 | 27 | 1 | 1 | 0.964 | 0.964 | 0.964 |
| sortDirection | 29 | 28 | 0 | 1 | 1.000 | 0.966 | 0.982 |
| limit | 21 | 21 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 98.0% | 0.985 |
| Compostas | 180 | 93.3% | 0.983 |
| Código MI/INOM | 57 | 100.0% | 1.000 |
| Tempo relativo | 60 | 91.7% | 0.979 |
| Ordenação | 29 | 93.1% | 0.982 |
| Ambíguas/informais | 197 | 94.4% | 0.983 |
| Fora do domínio | 8 | 87.5% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 86.4% |
| N | 37 | 86.5% |
| G | 247 | 97.2% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 8, 'misto': 2, 'campo_inventado': 4, 'chamou_sem_dever': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.956, 'creationPeriod': 0.9}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 75.0% · chamou sem dever: 1
