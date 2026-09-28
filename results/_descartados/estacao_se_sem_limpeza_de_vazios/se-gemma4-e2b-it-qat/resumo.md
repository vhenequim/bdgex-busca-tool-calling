# gemma4:e2b-it-qat [saida-estruturada] — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-28T14:43:26

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 45.8% |
| Precisão ponderada | 0.730 |
| Recall ponderado | 0.879 |
| F1 ponderado | 0.780 |
| F1 macro | 0.798 |
| Micro P / R / F1 | 0.709 / 0.874 / 0.783 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 387 | 816 | 978 | 1792 | 2512 | 476 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 15 | 15 | 0 | 0.500 | 1.000 | 0.667 |
| scale | 14 | 12 | 2 | 0 | 0.857 | 1.000 | 0.923 |
| productType | 14 | 9 | 4 | 1 | 0.692 | 0.900 | 0.783 |
| state | 15 | 10 | 4 | 4 | 0.714 | 0.714 | 0.714 |
| city | 5 | 4 | 0 | 1 | 1.000 | 0.800 | 0.889 |
| supplyArea | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 4 | 3 | 0 | 1 | 1.000 | 0.750 | 0.857 |
| publicationPeriod | 12 | 8 | 5 | 0 | 0.615 | 1.000 | 0.762 |
| creationPeriod | 4 | 2 | 2 | 0 | 0.500 | 1.000 | 0.667 |
| sortField | 10 | 7 | 1 | 3 | 0.875 | 0.700 | 0.778 |
| sortDirection | 10 | 4 | 4 | 3 | 0.500 | 0.571 | 0.533 |
| limit | 5 | 5 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 72.7% | 0.788 |
| Compostas | 43 | 39.5% | 0.777 |
| Código MI/INOM | 15 | 53.3% | 0.876 |
| Tempo relativo | 15 | 40.0% | 0.814 |
| Ordenação | 10 | 30.0% | 0.787 |
| Ambíguas/informais | 35 | 37.1% | 0.702 |
| Fora do domínio | 2 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 40.9% |
| N | 37 | 48.6% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 1, 'valor_errado': 14, 'campo_inventado': 7, 'misto': 8, 'chamou_sem_dever': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.807, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 1
