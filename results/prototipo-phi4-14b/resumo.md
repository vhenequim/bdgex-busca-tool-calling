# phi4:14b [prototipo] — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-28T17:08:27

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 58.8% |
| Precisão ponderada | 0.855 |
| Recall ponderado | 0.890 |
| F1 ponderado | 0.856 |
| F1 macro | 0.863 |
| Micro P / R / F1 | 0.801 / 0.887 / 0.842 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 6744 | 12586 | 14701 | 27192 | 135422 | 9139 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 61 | 57 | 65 | 4 | 0.467 | 0.934 | 0.623 |
| scale | 84 | 76 | 3 | 5 | 0.962 | 0.938 | 0.950 |
| productType | 44 | 39 | 17 | 3 | 0.696 | 0.929 | 0.796 |
| state | 128 | 98 | 1 | 30 | 0.990 | 0.766 | 0.863 |
| city | 30 | 21 | 2 | 9 | 0.913 | 0.700 | 0.792 |
| supplyArea | 40 | 40 | 3 | 0 | 0.930 | 1.000 | 0.964 |
| project | 10 | 9 | 1 | 1 | 0.900 | 0.900 | 0.900 |
| publicationPeriod | 49 | 37 | 15 | 0 | 0.712 | 1.000 | 0.831 |
| creationPeriod | 12 | 8 | 3 | 2 | 0.727 | 0.800 | 0.762 |
| sortField | 29 | 26 | 2 | 2 | 0.929 | 0.929 | 0.929 |
| sortDirection | 29 | 27 | 1 | 2 | 0.964 | 0.931 | 0.947 |
| limit | 18 | 18 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 57.0% | 0.820 |
| Compostas | 180 | 60.6% | 0.868 |
| Código MI/INOM | 57 | 75.4% | 0.937 |
| Tempo relativo | 60 | 63.3% | 0.865 |
| Ordenação | 29 | 72.4% | 0.937 |
| Ambíguas/informais | 197 | 57.9% | 0.846 |
| Fora do domínio | 8 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 59.1% |
| N | 37 | 59.5% |
| G | 247 | 58.7% |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 16, 'misto': 38, 'valor_errado': 17, 'campo_inventado': 47, 'chamou_sem_dever': 8}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.926, 'creationPeriod': 0.847}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 10 {None: 10}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 50.0% · chamou sem dever: 2
