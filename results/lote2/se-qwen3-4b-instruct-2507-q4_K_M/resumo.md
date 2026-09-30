# qwen3:4b-instruct-2507-q4_K_M [saida-estruturada] — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-30T14:27:26

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 51.4% |
| Precisão ponderada | 0.803 |
| Recall ponderado | 0.875 |
| F1 ponderado | 0.828 |
| F1 macro | 0.813 |
| Micro P / R / F1 | 0.786 / 0.873 / 0.828 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 192 | 885 | 911 | 1530 | 3751 | 481 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 239 | 200 | 76 | 16 | 0.725 | 0.926 | 0.813 |
| scale | 197 | 168 | 23 | 14 | 0.880 | 0.923 | 0.901 |
| productType | 192 | 165 | 100 | 19 | 0.623 | 0.897 | 0.735 |
| state | 139 | 117 | 51 | 20 | 0.696 | 0.854 | 0.767 |
| city | 102 | 60 | 20 | 41 | 0.750 | 0.594 | 0.663 |
| supplyArea | 175 | 174 | 7 | 1 | 0.961 | 0.994 | 0.978 |
| project | 95 | 86 | 2 | 8 | 0.977 | 0.915 | 0.945 |
| publicationPeriod | 105 | 86 | 47 | 1 | 0.647 | 0.989 | 0.782 |
| creationPeriod | 34 | 14 | 6 | 18 | 0.700 | 0.438 | 0.538 |
| sortField | 99 | 74 | 5 | 22 | 0.937 | 0.771 | 0.846 |
| sortDirection | 99 | 77 | 2 | 22 | 0.975 | 0.778 | 0.865 |
| limit | 51 | 49 | 6 | 2 | 0.891 | 0.961 | 0.925 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 80.7% | 0.845 |
| Compostas | 466 | 54.3% | 0.850 |
| Código MI/INOM | 130 | 77.7% | 0.923 |
| Tempo relativo | 139 | 63.3% | 0.837 |
| Ordenação | 99 | 54.5% | 0.872 |
| Ambíguas/informais | 457 | 59.3% | 0.844 |
| Fora do domínio | 163 | 0.0% | 0.000 |
| Subespecificadas | 65 | 58.5% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'misto': 91, 'valor_errado': 48, 'campo_inventado': 96, 'campo_omitido': 61, 'chamou_sem_dever': 163}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.868, 'creationPeriod': 0.9}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
