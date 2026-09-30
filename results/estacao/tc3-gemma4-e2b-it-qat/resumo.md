# gemma4:e2b-it-qat — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-30T00:07:54

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 78.0% |
| Precisão ponderada | 0.956 |
| Recall ponderado | 0.830 |
| F1 ponderado | 0.879 |
| F1 macro | 0.872 |
| Micro P / R / F1 | 0.944 / 0.829 / 0.883 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 429 | 1753 | 2056 | 4621 | 11235 | 1708 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 18 | 3 | 1 | 0.857 | 0.947 | 0.900 |
| scale | 14 | 11 | 1 | 2 | 0.917 | 0.846 | 0.880 |
| productType | 14 | 13 | 0 | 1 | 1.000 | 0.929 | 0.963 |
| state | 15 | 12 | 0 | 3 | 1.000 | 0.800 | 0.889 |
| city | 5 | 5 | 2 | 0 | 0.714 | 1.000 | 0.833 |
| supplyArea | 11 | 10 | 0 | 1 | 1.000 | 0.909 | 0.952 |
| project | 5 | 5 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 9 | 7 | 0 | 2 | 1.000 | 0.778 | 0.875 |
| creationPeriod | 7 | 6 | 0 | 1 | 1.000 | 0.857 | 0.923 |
| sortField | 10 | 6 | 0 | 4 | 1.000 | 0.600 | 0.750 |
| sortDirection | 10 | 6 | 0 | 4 | 1.000 | 0.600 | 0.750 |
| limit | 5 | 3 | 0 | 2 | 1.000 | 0.600 | 0.750 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 100.0% | 1.000 |
| Compostas | 43 | 74.4% | 0.868 |
| Código MI/INOM | 15 | 86.7% | 0.878 |
| Tempo relativo | 15 | 80.0% | 0.866 |
| Ordenação | 10 | 60.0% | 0.752 |
| Ambíguas/informais | 35 | 80.0% | 0.907 |
| Fora do domínio | 2 | 50.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 77.3% |
| N | 37 | 78.4% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_inventado': 3, 'valor_errado': 1, 'nao_chamou': 5, 'campo_omitido': 2, 'misto': 1, 'chamou_sem_dever': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 5

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 1
