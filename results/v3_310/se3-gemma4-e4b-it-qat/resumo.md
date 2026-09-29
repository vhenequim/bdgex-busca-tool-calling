# gemma4:e4b-it-qat [saida-estruturada-v3] — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-29T22:30:01

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 94.1% |
| Precisão ponderada | 0.984 |
| Recall ponderado | 0.966 |
| F1 ponderado | 0.974 |
| F1 macro | 0.978 |
| Micro P / R / F1 | 0.983 / 0.966 / 0.974 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 305 | 772 | 969 | 2673 | 5177 | 695 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 62 | 59 | 6 | 0 | 0.908 | 1.000 | 0.952 |
| scale | 84 | 82 | 1 | 1 | 0.988 | 0.988 | 0.988 |
| productType | 44 | 42 | 0 | 2 | 1.000 | 0.955 | 0.977 |
| state | 130 | 121 | 0 | 9 | 1.000 | 0.931 | 0.964 |
| city | 27 | 27 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 40 | 40 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 49 | 48 | 0 | 1 | 1.000 | 0.980 | 0.990 |
| creationPeriod | 12 | 12 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortField | 29 | 27 | 1 | 2 | 0.964 | 0.931 | 0.947 |
| sortDirection | 29 | 27 | 1 | 2 | 0.964 | 0.931 | 0.947 |
| limit | 19 | 18 | 0 | 1 | 1.000 | 0.947 | 0.973 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 93.0% | 0.963 |
| Compostas | 180 | 95.0% | 0.979 |
| Código MI/INOM | 57 | 94.7% | 0.985 |
| Tempo relativo | 60 | 95.0% | 0.984 |
| Ordenação | 29 | 93.1% | 0.967 |
| Ambíguas/informais | 197 | 92.4% | 0.971 |
| Fora do domínio | 8 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 86.4% |
| N | 37 | 81.1% |
| G | 247 | 96.8% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 4, 'nao_chamou': 10, 'campo_inventado': 1, 'misto': 3}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 10

## Observacionais (fora das métricas principais)

4 casos · acurácia 50.0% · chamou sem dever: 0
