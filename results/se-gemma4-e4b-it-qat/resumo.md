# gemma4:e4b-it-qat [saida-estruturada] — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-28T17:08:27

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 75.2% |
| Precisão ponderada | 0.891 |
| Recall ponderado | 0.934 |
| F1 ponderado | 0.902 |
| F1 macro | 0.893 |
| Micro P / R / F1 | 0.879 / 0.931 / 0.904 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 111 | 762 | 901 | 1605 | 5870 | 745 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 62 | 52 | 20 | 0 | 0.722 | 1.000 | 0.839 |
| scale | 84 | 76 | 7 | 1 | 0.916 | 0.987 | 0.950 |
| productType | 44 | 44 | 1 | 0 | 0.978 | 1.000 | 0.989 |
| state | 130 | 112 | 4 | 16 | 0.966 | 0.875 | 0.918 |
| city | 27 | 25 | 0 | 2 | 1.000 | 0.926 | 0.962 |
| supplyArea | 40 | 40 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 11 | 7 | 0 | 0.611 | 1.000 | 0.759 |
| publicationPeriod | 51 | 29 | 23 | 1 | 0.558 | 0.967 | 0.707 |
| creationPeriod | 10 | 7 | 1 | 2 | 0.875 | 0.778 | 0.824 |
| sortField | 29 | 23 | 0 | 6 | 1.000 | 0.793 | 0.885 |
| sortDirection | 29 | 23 | 0 | 6 | 1.000 | 0.793 | 0.885 |
| limit | 16 | 16 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 88.0% | 0.917 |
| Compostas | 180 | 71.7% | 0.904 |
| Código MI/INOM | 57 | 75.4% | 0.921 |
| Tempo relativo | 60 | 53.3% | 0.846 |
| Ordenação | 29 | 62.1% | 0.901 |
| Ambíguas/informais | 197 | 76.6% | 0.899 |
| Fora do domínio | 8 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 54.5% |
| N | 37 | 67.6% |
| G | 247 | 78.1% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 39, 'campo_omitido': 8, 'misto': 19, 'campo_inventado': 2, 'chamou_sem_dever': 8}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.665, 'creationPeriod': 0.875}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 0.0% · chamou sem dever: 2
