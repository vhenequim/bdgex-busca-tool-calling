# gemma4:e2b-it-qat — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-28T15:07:09

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 47.5% |
| Precisão ponderada | 0.795 |
| Recall ponderado | 0.722 |
| F1 ponderado | 0.719 |
| F1 macro | 0.666 |
| Micro P / R / F1 | 0.790 / 0.735 / 0.761 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 372 | 709 | 777 | 1198 | 1439 | 252 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 19 | 17 | 8 | 0 | 0.680 | 1.000 | 0.810 |
| scale | 14 | 10 | 2 | 2 | 0.833 | 0.833 | 0.833 |
| productType | 14 | 12 | 0 | 2 | 1.000 | 0.857 | 0.923 |
| state | 15 | 11 | 2 | 4 | 0.846 | 0.733 | 0.786 |
| city | 6 | 6 | 1 | 0 | 0.857 | 1.000 | 0.923 |
| supplyArea | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 5 | 4 | 1 | 1 | 0.800 | 0.800 | 0.800 |
| publicationPeriod | 14 | 5 | 5 | 4 | 0.500 | 0.556 | 0.526 |
| creationPeriod | 2 | 0 | 1 | 1 | 0.000 | 0.000 | 0.000 |
| sortField | 10 | 1 | 0 | 9 | 1.000 | 0.100 | 0.182 |
| sortDirection | 10 | 3 | 2 | 5 | 0.600 | 0.375 | 0.462 |
| limit | 5 | 3 | 0 | 2 | 1.000 | 0.600 | 0.750 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 81.8% | 0.887 |
| Compostas | 43 | 39.5% | 0.716 |
| Código MI/INOM | 15 | 60.0% | 0.867 |
| Tempo relativo | 15 | 13.3% | 0.655 |
| Ordenação | 10 | 0.0% | 0.541 |
| Ambíguas/informais | 35 | 40.0% | 0.693 |
| Fora do domínio | 2 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 45.5% |
| N | 37 | 48.6% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 4, 'valor_errado': 9, 'campo_inventado': 3, 'misto': 7, 'nao_chamou': 8}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.671}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 8

## Observacionais (fora das métricas principais)

3 casos · acurácia 66.7% · chamou sem dever: 0
