# gemma4:e4b-it-qat — resumo da avaliação

225 execuções · repetições [1, 2, 3] · gerado em 2026-09-24T10:52:13

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 213 |
| Acurácia por consulta | 55.4% |
| Precisão ponderada | 0.866 |
| Recall ponderado | 0.648 |
| F1 ponderado | 0.713 |
| F1 macro | 0.704 |
| Micro P / R / F1 | 0.858 / 0.651 / 0.741 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 213 | 420 | 820 | 1061 | 3504 | 4936 | 877 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 57 | 40 | 16 | 5 | 0.714 | 0.889 | 0.792 |
| scale | 51 | 32 | 0 | 19 | 1.000 | 0.627 | 0.771 |
| productType | 42 | 29 | 8 | 13 | 0.784 | 0.690 | 0.734 |
| state | 57 | 44 | 0 | 13 | 1.000 | 0.772 | 0.871 |
| city | 18 | 18 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 51 | 40 | 3 | 11 | 0.930 | 0.784 | 0.851 |
| project | 15 | 15 | 3 | 0 | 0.833 | 1.000 | 0.909 |
| publicationPeriod | 42 | 9 | 12 | 21 | 0.429 | 0.300 | 0.353 |
| creationPeriod | 6 | 3 | 0 | 3 | 1.000 | 0.500 | 0.667 |
| sortField | 30 | 9 | 0 | 21 | 1.000 | 0.300 | 0.462 |
| sortDirection | 30 | 9 | 0 | 21 | 1.000 | 0.300 | 0.462 |
| limit | 15 | 6 | 0 | 9 | 1.000 | 0.400 | 0.571 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 66 | 84.8% | 0.903 |
| Compostas | 132 | 42.4% | 0.690 |
| Código MI/INOM | 45 | 46.7% | 0.721 |
| Tempo relativo | 45 | 20.0% | 0.530 |
| Ordenação | 30 | 20.0% | 0.510 |
| Ambíguas/informais | 123 | 44.7% | 0.687 |
| Fora do domínio | 6 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 43.9% |
| N | 111 | 55.9% |
| G | 36 | 75.0% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 21, 'misto': 12, 'campo_omitido': 4, 'campo_inventado': 9, 'nao_chamou': 49}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 49

## Observacionais (fora das métricas principais)

12 casos · acurácia 50.0% · chamou sem dever: 0

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 54.9% | 0.719 | 845 |
| 2 | 54.9% | 0.704 | 823 |
| 3 | 56.3% | 0.714 | 782 |
