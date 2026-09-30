# gemma4:e2b-it-qat [saida-estruturada] — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-30T03:10:38

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 45.8% |
| Precisão ponderada | 0.733 |
| Recall ponderado | 0.879 |
| F1 ponderado | 0.782 |
| F1 macro | 0.799 |
| Micro P / R / F1 | 0.714 / 0.874 / 0.786 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 310 | 760 | 884 | 1554 | 2313 | 440 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 15 | 14 | 0 | 0.517 | 1.000 | 0.682 |
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
| Compostas | 43 | 39.5% | 0.780 |
| Código MI/INOM | 15 | 53.3% | 0.876 |
| Tempo relativo | 15 | 40.0% | 0.814 |
| Ordenação | 10 | 30.0% | 0.787 |
| Ambíguas/informais | 35 | 37.1% | 0.705 |
| Fora do domínio | 2 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 40.9% |
| N | 37 | 48.6% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 1, 'valor_errado': 15, 'campo_inventado': 6, 'misto': 8, 'chamou_sem_dever': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.807, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 1
