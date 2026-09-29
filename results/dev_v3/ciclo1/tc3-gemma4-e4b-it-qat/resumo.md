# gemma4:e4b-it-qat — resumo da avaliação

160 execuções · repetições [1] · gerado em 2026-09-29T10:04:07

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 160 |
| Acurácia por consulta | 87.5% |
| Precisão ponderada | 0.953 |
| Recall ponderado | 0.947 |
| F1 ponderado | 0.948 |
| F1 macro | 0.930 |
| Micro P / R / F1 | 0.951 / 0.951 / 0.951 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 160 | 1420 | 5998 | 7475 | 14543 | 38154 | 4427 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 49 | 47 | 2 | 1 | 0.959 | 0.979 | 0.969 |
| scale | 37 | 37 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| productType | 34 | 31 | 0 | 3 | 1.000 | 0.912 | 0.954 |
| state | 30 | 29 | 0 | 1 | 1.000 | 0.967 | 0.983 |
| city | 19 | 16 | 0 | 3 | 1.000 | 0.842 | 0.914 |
| supplyArea | 31 | 30 | 0 | 1 | 1.000 | 0.968 | 0.984 |
| project | 14 | 14 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 17 | 9 | 9 | 3 | 0.500 | 0.750 | 0.600 |
| creationPeriod | 10 | 7 | 2 | 2 | 0.778 | 0.778 | 0.778 |
| sortField | 20 | 20 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortDirection | 20 | 20 | 1 | 0 | 0.952 | 1.000 | 0.976 |
| limit | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 33 | 90.9% | 0.947 |
| Compostas | 93 | 86.0% | 0.952 |
| Código MI/INOM | 30 | 96.7% | 0.984 |
| Tempo relativo | 27 | 51.9% | 0.816 |
| Ordenação | 20 | 95.0% | 0.992 |
| Ambíguas/informais | 87 | 86.2% | 0.948 |
| Fora do domínio | 15 | 100.0% | 0.000 |
| Subespecificadas | 10 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 2, 'nao_chamou': 5, 'campo_inventado': 4, 'misto': 4, 'valor_errado': 5}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.92, 'creationPeriod': 0.887}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 5

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
