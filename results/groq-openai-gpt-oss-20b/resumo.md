# openai/gpt-oss-20b — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-24T10:04:29

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 89.2% |
| Precisão ponderada | 0.959 |
| Recall ponderado | 0.945 |
| F1 ponderado | 0.946 |
| F1 macro | 0.933 |
| Micro P / R / F1 | 0.957 / 0.944 / 0.951 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 276 | 530 | 679 | 1496 | 3418 | 453 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 61 | 58 | 3 | 1 | 0.951 | 0.983 | 0.967 |
| scale | 84 | 78 | 5 | 1 | 0.940 | 0.987 | 0.963 |
| productType | 44 | 44 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| state | 127 | 125 | 3 | 2 | 0.977 | 0.984 | 0.980 |
| city | 31 | 31 | 3 | 0 | 0.912 | 1.000 | 0.954 |
| supplyArea | 40 | 40 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 10 | 0 | 1 | 1.000 | 0.909 | 0.952 |
| publicationPeriod | 51 | 45 | 7 | 0 | 0.865 | 1.000 | 0.928 |
| creationPeriod | 10 | 10 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortField | 29 | 17 | 0 | 12 | 1.000 | 0.586 | 0.739 |
| sortDirection | 29 | 17 | 0 | 12 | 1.000 | 0.586 | 0.739 |
| limit | 15 | 15 | 1 | 0 | 0.938 | 1.000 | 0.968 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 97.0% | 0.985 |
| Compostas | 180 | 84.4% | 0.937 |
| Código MI/INOM | 57 | 94.7% | 0.985 |
| Tempo relativo | 60 | 83.3% | 0.938 |
| Ordenação | 29 | 48.3% | 0.837 |
| Ambíguas/informais | 197 | 88.8% | 0.952 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 77.3% |
| N | 37 | 83.8% |
| G | 247 | 91.1% |

## Diagnósticos

- Tipos de erro: {'misto': 2, 'valor_errado': 13, 'campo_omitido': 11, 'nao_chamou': 2, 'campo_inventado': 5}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.946, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 2

## Observacionais (fora das métricas principais)

4 casos · acurácia 50.0% · chamou sem dever: 1
