# gemma4:e2b-it-qat [saida-estruturada-v3] — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-30T00:09:27

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 55.9% |
| Precisão ponderada | 0.930 |
| Recall ponderado | 0.664 |
| F1 ponderado | 0.753 |
| F1 macro | 0.745 |
| Micro P / R / F1 | 0.909 / 0.661 / 0.766 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 303 | 805 | 1009 | 2167 | 5223 | 764 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 18 | 4 | 2 | 0.818 | 0.900 | 0.857 |
| scale | 14 | 9 | 2 | 3 | 0.818 | 0.750 | 0.783 |
| productType | 14 | 9 | 0 | 5 | 1.000 | 0.643 | 0.783 |
| state | 14 | 10 | 1 | 4 | 0.909 | 0.714 | 0.800 |
| city | 6 | 4 | 0 | 2 | 1.000 | 0.667 | 0.800 |
| supplyArea | 11 | 8 | 1 | 2 | 0.889 | 0.800 | 0.842 |
| project | 4 | 2 | 0 | 2 | 1.000 | 0.500 | 0.667 |
| publicationPeriod | 13 | 7 | 0 | 6 | 1.000 | 0.538 | 0.700 |
| creationPeriod | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortField | 10 | 4 | 0 | 6 | 1.000 | 0.400 | 0.571 |
| sortDirection | 10 | 4 | 0 | 6 | 1.000 | 0.400 | 0.571 |
| limit | 5 | 2 | 0 | 3 | 1.000 | 0.400 | 0.571 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 72.7% | 0.782 |
| Compostas | 43 | 48.8% | 0.747 |
| Código MI/INOM | 15 | 73.3% | 0.870 |
| Tempo relativo | 15 | 53.3% | 0.790 |
| Ordenação | 10 | 30.0% | 0.666 |
| Ambíguas/informais | 35 | 42.9% | 0.723 |
| Fora do domínio | 2 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 50.0% |
| N | 37 | 59.5% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 14, 'campo_inventado': 4, 'valor_errado': 1, 'campo_omitido': 5, 'misto': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 14

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 0
