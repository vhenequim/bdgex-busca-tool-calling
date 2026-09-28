# mistral-nemo:12b [saida-estruturada] — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-28T17:08:27

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 52.0% |
| Precisão ponderada | 0.701 |
| Recall ponderado | 0.782 |
| F1 ponderado | 0.727 |
| F1 macro | 0.677 |
| Micro P / R / F1 | 0.704 / 0.784 / 0.742 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 558 | 998 | 1549 | 3386 | 10838 | 1491 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 62 | 61 | 15 | 0 | 0.803 | 1.000 | 0.891 |
| scale | 84 | 35 | 19 | 39 | 0.648 | 0.473 | 0.547 |
| productType | 44 | 31 | 12 | 10 | 0.721 | 0.756 | 0.738 |
| state | 130 | 114 | 19 | 11 | 0.857 | 0.912 | 0.884 |
| city | 27 | 24 | 10 | 3 | 0.706 | 0.889 | 0.787 |
| supplyArea | 40 | 33 | 10 | 7 | 0.767 | 0.825 | 0.795 |
| project | 10 | 8 | 8 | 2 | 0.500 | 0.800 | 0.615 |
| publicationPeriod | 51 | 31 | 30 | 0 | 0.508 | 1.000 | 0.674 |
| creationPeriod | 10 | 4 | 4 | 4 | 0.500 | 0.500 | 0.500 |
| sortField | 29 | 15 | 8 | 14 | 0.652 | 0.517 | 0.577 |
| sortDirection | 29 | 9 | 14 | 14 | 0.391 | 0.391 | 0.391 |
| limit | 13 | 13 | 10 | 0 | 0.565 | 1.000 | 0.722 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 85.0% | 0.803 |
| Compostas | 180 | 36.1% | 0.767 |
| Código MI/INOM | 57 | 64.9% | 0.877 |
| Tempo relativo | 60 | 43.3% | 0.753 |
| Ordenação | 29 | 27.6% | 0.717 |
| Ambíguas/informais | 197 | 43.7% | 0.696 |
| Fora do domínio | 8 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 40.9% |
| N | 37 | 56.8% |
| G | 247 | 52.2% |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 76, 'valor_errado': 35, 'campo_inventado': 16, 'misto': 12, 'chamou_sem_dever': 8}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.898, 'creationPeriod': 0.8}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 25.0% · chamou sem dever: 2
