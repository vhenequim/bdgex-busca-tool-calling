# openai/gpt-oss-120b [saida-estruturada] — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-28T16:10:07

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 87.3% |
| Precisão ponderada | 0.970 |
| Recall ponderado | 0.959 |
| F1 ponderado | 0.964 |
| F1 macro | 0.971 |
| Micro P / R / F1 | 0.969 / 0.958 / 0.964 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 309 | 601 | 698 | 1365 | 2477 | 302 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 61 | 60 | 2 | 0 | 0.968 | 1.000 | 0.984 |
| scale | 84 | 81 | 0 | 3 | 1.000 | 0.964 | 0.982 |
| productType | 44 | 42 | 1 | 2 | 0.977 | 0.955 | 0.966 |
| state | 130 | 119 | 8 | 10 | 0.937 | 0.922 | 0.930 |
| city | 28 | 28 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 40 | 40 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 51 | 47 | 5 | 0 | 0.904 | 1.000 | 0.949 |
| creationPeriod | 10 | 9 | 0 | 1 | 1.000 | 0.900 | 0.947 |
| sortField | 29 | 26 | 0 | 3 | 1.000 | 0.897 | 0.945 |
| sortDirection | 29 | 26 | 0 | 3 | 1.000 | 0.897 | 0.945 |
| limit | 19 | 19 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 96.0% | 0.979 |
| Compostas | 180 | 85.6% | 0.959 |
| Código MI/INOM | 57 | 82.5% | 0.934 |
| Tempo relativo | 60 | 90.0% | 0.970 |
| Ordenação | 29 | 89.7% | 0.963 |
| Ambíguas/informais | 197 | 87.8% | 0.959 |
| Fora do domínio | 8 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 68.2% |
| N | 37 | 89.2% |
| G | 247 | 88.7% |

## Diagnósticos

- Tipos de erro: {'campo_inventado': 7, 'valor_errado': 6, 'campo_omitido': 15, 'misto': 3, 'chamou_sem_dever': 8}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.958, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 1 {'args_invalidos': 1}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 50.0% · chamou sem dever: 2
