# gemma4:e2b-it-qat [saida-estruturada] — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-28T17:08:27

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 53.9% |
| Precisão ponderada | 0.790 |
| Recall ponderado | 0.847 |
| F1 ponderado | 0.792 |
| F1 macro | 0.818 |
| Micro P / R / F1 | 0.724 / 0.843 / 0.779 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 215 | 466 | 495 | 864 | 1509 | 200 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 62 | 50 | 86 | 0 | 0.368 | 1.000 | 0.538 |
| scale | 84 | 72 | 11 | 2 | 0.867 | 0.973 | 0.917 |
| productType | 44 | 21 | 15 | 10 | 0.583 | 0.677 | 0.627 |
| state | 130 | 86 | 10 | 40 | 0.896 | 0.683 | 0.775 |
| city | 27 | 18 | 0 | 9 | 1.000 | 0.667 | 0.800 |
| supplyArea | 40 | 37 | 2 | 1 | 0.949 | 0.974 | 0.961 |
| project | 10 | 10 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 49 | 38 | 16 | 0 | 0.704 | 1.000 | 0.826 |
| creationPeriod | 12 | 6 | 3 | 3 | 0.667 | 0.667 | 0.667 |
| sortField | 29 | 25 | 1 | 4 | 0.962 | 0.862 | 0.909 |
| sortDirection | 29 | 20 | 6 | 4 | 0.769 | 0.833 | 0.800 |
| limit | 10 | 10 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 80.0% | 0.852 |
| Compostas | 180 | 39.4% | 0.776 |
| Código MI/INOM | 57 | 68.4% | 0.887 |
| Tempo relativo | 60 | 60.0% | 0.836 |
| Ordenação | 29 | 27.6% | 0.779 |
| Ambíguas/informais | 197 | 44.7% | 0.766 |
| Fora do domínio | 8 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 40.9% |
| N | 37 | 48.6% |
| G | 247 | 55.9% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 46, 'campo_inventado': 22, 'misto': 57, 'chamou_sem_dever': 8, 'campo_omitido': 8}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.917, 'creationPeriod': 0.868}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 25.0% · chamou sem dever: 2
