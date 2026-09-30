# gemma4:e4b-it-qat [saida-estruturada] — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-30T00:18:22

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 61.0% |
| Precisão ponderada | 0.875 |
| Recall ponderado | 0.907 |
| F1 ponderado | 0.875 |
| F1 macro | 0.900 |
| Micro P / R / F1 | 0.866 / 0.904 / 0.884 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 516 | 3288 | 3654 | 7129 | 9802 | 1893 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 14 | 8 | 0 | 0.636 | 1.000 | 0.778 |
| scale | 14 | 13 | 0 | 1 | 1.000 | 0.929 | 0.963 |
| productType | 14 | 14 | 1 | 0 | 0.933 | 1.000 | 0.966 |
| state | 15 | 13 | 1 | 2 | 0.929 | 0.867 | 0.897 |
| city | 5 | 4 | 0 | 1 | 1.000 | 0.800 | 0.889 |
| supplyArea | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 5 | 5 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 14 | 7 | 6 | 1 | 0.538 | 0.875 | 0.667 |
| creationPeriod | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortField | 10 | 7 | 0 | 3 | 1.000 | 0.700 | 0.824 |
| sortDirection | 10 | 7 | 0 | 3 | 1.000 | 0.700 | 0.824 |
| limit | 6 | 6 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 100.0% | 1.000 |
| Compostas | 43 | 51.2% | 0.855 |
| Código MI/INOM | 15 | 33.3% | 0.836 |
| Tempo relativo | 15 | 46.7% | 0.873 |
| Ordenação | 10 | 40.0% | 0.874 |
| Ambíguas/informais | 35 | 60.0% | 0.842 |
| Fora do domínio | 2 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 50.0% |
| N | 37 | 67.6% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 12, 'campo_omitido': 6, 'misto': 2, 'campo_inventado': 1, 'chamou_sem_dever': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.596, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 1
