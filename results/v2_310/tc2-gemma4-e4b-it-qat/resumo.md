# gemma4:e4b-it-qat — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-29T03:10:07

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 47.4% |
| Precisão ponderada | 0.714 |
| Recall ponderado | 0.968 |
| F1 ponderado | 0.796 |
| F1 macro | 0.826 |
| Micro P / R / F1 | 0.678 / 0.970 / 0.798 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 292 | 811 | 826 | 1307 | 2497 | 295 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 61 | 26 | 51 | 0 | 0.338 | 1.000 | 0.505 |
| scale | 84 | 80 | 0 | 4 | 1.000 | 0.952 | 0.976 |
| productType | 44 | 44 | 53 | 0 | 0.454 | 1.000 | 0.624 |
| state | 130 | 68 | 60 | 4 | 0.531 | 0.944 | 0.680 |
| city | 28 | 28 | 1 | 0 | 0.966 | 1.000 | 0.982 |
| supplyArea | 40 | 40 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 11 | 1 | 0 | 0.917 | 1.000 | 0.957 |
| publicationPeriod | 50 | 40 | 9 | 2 | 0.816 | 0.952 | 0.879 |
| creationPeriod | 11 | 6 | 4 | 1 | 0.600 | 0.857 | 0.706 |
| sortField | 29 | 28 | 2 | 1 | 0.933 | 0.966 | 0.949 |
| sortDirection | 29 | 28 | 2 | 1 | 0.933 | 0.966 | 0.949 |
| limit | 18 | 18 | 15 | 0 | 0.545 | 1.000 | 0.706 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 58.0% | 0.654 |
| Compostas | 180 | 36.7% | 0.824 |
| Código MI/INOM | 57 | 40.4% | 0.737 |
| Tempo relativo | 60 | 55.0% | 0.856 |
| Ordenação | 29 | 34.5% | 0.861 |
| Ambíguas/informais | 197 | 41.1% | 0.783 |
| Fora do domínio | 8 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 50.0% |
| N | 37 | 56.8% |
| G | 247 | 45.7% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 80, 'campo_inventado': 69, 'misto': 8, 'campo_omitido': 4}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.895, 'creationPeriod': 0.886}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 25.0% · chamou sem dever: 2
