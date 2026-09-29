# gemma4:e4b-it-qat [saida-estruturada-v3] — resumo da avaliação

160 execuções · repetições [1] · gerado em 2026-09-29T10:54:29

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 160 |
| Acurácia por consulta | 93.1% |
| Precisão ponderada | 0.973 |
| Recall ponderado | 0.986 |
| F1 ponderado | 0.979 |
| F1 macro | 0.979 |
| Micro P / R / F1 | 0.973 / 0.986 / 0.979 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 160 | 1403 | 5069 | 5303 | 10605 | 16357 | 2950 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 50 | 45 | 4 | 1 | 0.918 | 0.978 | 0.947 |
| scale | 37 | 37 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| productType | 34 | 32 | 0 | 2 | 1.000 | 0.941 | 0.970 |
| state | 28 | 28 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| city | 20 | 19 | 2 | 0 | 0.905 | 1.000 | 0.950 |
| supplyArea | 31 | 31 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 14 | 14 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 18 | 16 | 2 | 0 | 0.889 | 1.000 | 0.941 |
| creationPeriod | 9 | 8 | 0 | 1 | 1.000 | 0.889 | 0.941 |
| sortField | 20 | 20 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortDirection | 20 | 20 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| limit | 13 | 13 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 33 | 87.9% | 0.931 |
| Compostas | 93 | 93.5% | 0.985 |
| Código MI/INOM | 30 | 86.7% | 0.967 |
| Tempo relativo | 27 | 88.9% | 0.971 |
| Ordenação | 20 | 100.0% | 1.000 |
| Ambíguas/informais | 87 | 90.8% | 0.976 |
| Fora do domínio | 15 | 100.0% | 0.000 |
| Subespecificadas | 10 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 7, 'misto': 1, 'nao_chamou': 3}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.889, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 3

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
