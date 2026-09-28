# gemma4:e2b-it-qat [saida-estruturada] — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-28T14:37:13

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 44.1% |
| Precisão ponderada | 0.702 |
| Recall ponderado | 0.787 |
| F1 ponderado | 0.718 |
| F1 macro | 0.716 |
| Micro P / R / F1 | 0.654 / 0.787 / 0.714 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 364 | 853 | 976 | 1689 | 3000 | 467 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 15 | 19 | 0 | 0.441 | 1.000 | 0.612 |
| scale | 14 | 9 | 2 | 3 | 0.818 | 0.750 | 0.783 |
| productType | 14 | 11 | 0 | 3 | 1.000 | 0.786 | 0.880 |
| state | 15 | 10 | 3 | 4 | 0.769 | 0.714 | 0.741 |
| city | 5 | 3 | 0 | 2 | 1.000 | 0.600 | 0.750 |
| supplyArea | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 4 | 3 | 0 | 1 | 1.000 | 0.750 | 0.857 |
| publicationPeriod | 13 | 8 | 5 | 1 | 0.615 | 0.889 | 0.727 |
| creationPeriod | 3 | 1 | 1 | 1 | 0.500 | 0.500 | 0.500 |
| sortField | 10 | 6 | 5 | 4 | 0.545 | 0.600 | 0.571 |
| sortDirection | 10 | 3 | 8 | 4 | 0.273 | 0.429 | 0.333 |
| limit | 5 | 5 | 2 | 0 | 0.714 | 1.000 | 0.833 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 81.8% | 0.857 |
| Compostas | 43 | 34.9% | 0.704 |
| Código MI/INOM | 15 | 53.3% | 0.819 |
| Tempo relativo | 15 | 33.3% | 0.741 |
| Ordenação | 10 | 20.0% | 0.670 |
| Ambíguas/informais | 35 | 34.3% | 0.674 |
| Fora do domínio | 2 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 40.9% |
| N | 37 | 45.9% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 2, 'valor_errado': 9, 'misto': 14, 'campo_inventado': 6, 'chamou_sem_dever': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.807, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 1
