# gemma4:e4b-it-qat — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-29T22:24:50

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 97.7% |
| Precisão ponderada | 0.991 |
| Recall ponderado | 0.994 |
| F1 ponderado | 0.993 |
| F1 macro | 0.993 |
| Micro P / R / F1 | 0.991 / 0.994 / 0.993 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 444 | 1385 | 1548 | 2659 | 9154 | 931 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 61 | 61 | 2 | 0 | 0.968 | 1.000 | 0.984 |
| scale | 84 | 84 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| productType | 44 | 44 | 1 | 0 | 0.978 | 1.000 | 0.989 |
| state | 129 | 126 | 0 | 3 | 1.000 | 0.977 | 0.988 |
| city | 29 | 29 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 40 | 40 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 49 | 49 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| creationPeriod | 12 | 12 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortField | 29 | 29 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortDirection | 29 | 28 | 1 | 0 | 0.966 | 1.000 | 0.982 |
| limit | 17 | 17 | 1 | 0 | 0.944 | 1.000 | 0.971 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 100.0% | 1.000 |
| Compostas | 180 | 97.2% | 0.992 |
| Código MI/INOM | 57 | 98.2% | 0.995 |
| Tempo relativo | 60 | 100.0% | 1.000 |
| Ordenação | 29 | 93.1% | 0.991 |
| Ambíguas/informais | 197 | 98.5% | 0.993 |
| Fora do domínio | 8 | 75.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 100.0% |
| N | 37 | 94.6% |
| G | 247 | 98.0% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 1, 'misto': 2, 'campo_omitido': 1, 'campo_inventado': 1, 'chamou_sem_dever': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 25.0% · chamou sem dever: 2
