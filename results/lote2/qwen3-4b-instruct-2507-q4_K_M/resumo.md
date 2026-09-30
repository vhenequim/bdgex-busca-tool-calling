# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-30T14:12:58

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 56.6% |
| Precisão ponderada | 0.653 |
| Recall ponderado | 0.762 |
| F1 ponderado | 0.664 |
| F1 macro | 0.626 |
| Micro P / R / F1 | 0.607 / 0.758 / 0.674 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 216 | 1048 | 1169 | 2220 | 6445 | 681 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 239 | 206 | 103 | 12 | 0.667 | 0.945 | 0.782 |
| scale | 197 | 73 | 12 | 115 | 0.859 | 0.388 | 0.535 |
| productType | 192 | 134 | 114 | 51 | 0.540 | 0.724 | 0.619 |
| state | 139 | 110 | 71 | 26 | 0.608 | 0.809 | 0.694 |
| city | 102 | 24 | 16 | 78 | 0.600 | 0.235 | 0.338 |
| supplyArea | 175 | 155 | 5 | 20 | 0.969 | 0.886 | 0.925 |
| project | 96 | 90 | 26 | 4 | 0.776 | 0.957 | 0.857 |
| publicationPeriod | 105 | 69 | 97 | 2 | 0.416 | 0.972 | 0.582 |
| creationPeriod | 34 | 8 | 11 | 22 | 0.421 | 0.267 | 0.327 |
| sortField | 99 | 86 | 88 | 10 | 0.494 | 0.896 | 0.637 |
| sortDirection | 99 | 89 | 85 | 10 | 0.511 | 0.899 | 0.652 |
| limit | 56 | 55 | 83 | 1 | 0.399 | 0.982 | 0.567 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 70.3% | 0.758 |
| Compostas | 466 | 35.2% | 0.669 |
| Código MI/INOM | 130 | 79.2% | 0.914 |
| Tempo relativo | 139 | 28.8% | 0.565 |
| Ordenação | 99 | 52.5% | 0.851 |
| Ambíguas/informais | 457 | 42.5% | 0.663 |
| Fora do domínio | 163 | 100.0% | 0.000 |
| Subespecificadas | 65 | 60.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'misto': 232, 'nao_chamou': 35, 'valor_errado': 42, 'campo_inventado': 70, 'campo_omitido': 31}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.814, 'creationPeriod': 0.791}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 35

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
