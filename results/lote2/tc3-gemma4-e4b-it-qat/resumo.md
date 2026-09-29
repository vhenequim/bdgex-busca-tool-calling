# gemma4:e4b-it-qat — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-29T20:26:51

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 94.4% |
| Precisão ponderada | 0.974 |
| Recall ponderado | 0.989 |
| F1 ponderado | 0.981 |
| F1 macro | 0.980 |
| Micro P / R / F1 | 0.974 / 0.989 / 0.981 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 309 | 1474 | 2050 | 4962 | 17273 | 1808 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 235 | 226 | 16 | 4 | 0.934 | 0.983 | 0.958 |
| scale | 197 | 194 | 1 | 2 | 0.995 | 0.990 | 0.992 |
| productType | 192 | 191 | 1 | 1 | 0.995 | 0.995 | 0.995 |
| state | 131 | 126 | 3 | 5 | 0.977 | 0.962 | 0.969 |
| city | 114 | 111 | 4 | 3 | 0.965 | 0.974 | 0.969 |
| supplyArea | 175 | 175 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 100 | 97 | 3 | 0 | 0.970 | 1.000 | 0.985 |
| publicationPeriod | 102 | 96 | 6 | 1 | 0.941 | 0.990 | 0.965 |
| creationPeriod | 37 | 36 | 3 | 1 | 0.923 | 0.973 | 0.947 |
| sortField | 99 | 98 | 1 | 0 | 0.990 | 1.000 | 0.995 |
| sortDirection | 99 | 99 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| limit | 59 | 59 | 2 | 0 | 0.967 | 1.000 | 0.983 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 97.4% | 0.987 |
| Compostas | 466 | 93.6% | 0.985 |
| Código MI/INOM | 130 | 98.5% | 0.996 |
| Tempo relativo | 139 | 91.4% | 0.976 |
| Ordenação | 99 | 97.0% | 0.993 |
| Ambíguas/informais | 457 | 93.7% | 0.982 |
| Fora do domínio | 163 | 95.1% | 0.000 |
| Subespecificadas | 65 | 92.3% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 14, 'campo_omitido': 7, 'campo_inventado': 16, 'misto': 6, 'nao_chamou': 2, 'chamou_sem_dever': 8}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 2

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
