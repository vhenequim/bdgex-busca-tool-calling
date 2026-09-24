# openai/gpt-oss-120b — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-24T10:05:07

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 89.9% |
| Precisão ponderada | 0.965 |
| Recall ponderado | 0.951 |
| F1 ponderado | 0.956 |
| F1 macro | 0.947 |
| Micro P / R / F1 | 0.964 / 0.951 / 0.957 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 366 | 655 | 788 | 1611 | 2736 | 413 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 61 | 58 | 3 | 1 | 0.951 | 0.983 | 0.967 |
| scale | 84 | 78 | 2 | 4 | 0.975 | 0.951 | 0.963 |
| productType | 44 | 43 | 1 | 1 | 0.977 | 0.977 | 0.977 |
| state | 130 | 127 | 7 | 3 | 0.948 | 0.977 | 0.962 |
| city | 28 | 28 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 40 | 40 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 51 | 47 | 6 | 1 | 0.887 | 0.979 | 0.931 |
| creationPeriod | 10 | 7 | 0 | 3 | 1.000 | 0.700 | 0.824 |
| sortField | 29 | 23 | 0 | 6 | 1.000 | 0.793 | 0.885 |
| sortDirection | 29 | 23 | 0 | 6 | 1.000 | 0.793 | 0.885 |
| limit | 19 | 18 | 0 | 1 | 1.000 | 0.947 | 0.973 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 96.0% | 0.979 |
| Compostas | 180 | 85.6% | 0.950 |
| Código MI/INOM | 57 | 94.7% | 0.986 |
| Tempo relativo | 60 | 83.3% | 0.933 |
| Ordenação | 29 | 79.3% | 0.926 |
| Ambíguas/informais | 197 | 86.8% | 0.951 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 68.2% |
| N | 37 | 81.1% |
| G | 247 | 93.1% |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 6, 'valor_errado': 7, 'campo_inventado': 9, 'nao_chamou': 6, 'misto': 3}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.945, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 6

## Observacionais (fora das métricas principais)

4 casos · acurácia 25.0% · chamou sem dever: 1
