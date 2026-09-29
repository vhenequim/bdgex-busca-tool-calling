# gemma4:e4b-it-qat — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-29T21:50:07

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 75.2% |
| Precisão ponderada | 0.868 |
| Recall ponderado | 0.933 |
| F1 ponderado | 0.896 |
| F1 macro | 0.885 |
| Micro P / R / F1 | 0.857 / 0.933 / 0.893 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 289 | 902 | 936 | 1381 | 11608 | 650 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 239 | 207 | 58 | 11 | 0.781 | 0.950 | 0.857 |
| scale | 197 | 180 | 4 | 13 | 0.978 | 0.933 | 0.955 |
| productType | 192 | 175 | 30 | 16 | 0.854 | 0.916 | 0.884 |
| state | 138 | 106 | 15 | 32 | 0.876 | 0.768 | 0.819 |
| city | 103 | 82 | 21 | 16 | 0.796 | 0.837 | 0.816 |
| supplyArea | 175 | 175 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 99 | 93 | 3 | 3 | 0.969 | 0.969 | 0.969 |
| publicationPeriod | 93 | 79 | 14 | 5 | 0.849 | 0.940 | 0.893 |
| creationPeriod | 46 | 36 | 10 | 1 | 0.783 | 0.973 | 0.867 |
| sortField | 99 | 98 | 17 | 1 | 0.852 | 0.990 | 0.916 |
| sortDirection | 99 | 98 | 17 | 1 | 0.852 | 0.990 | 0.916 |
| limit | 55 | 55 | 42 | 0 | 0.567 | 1.000 | 0.724 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 84.9% | 0.906 |
| Compostas | 466 | 64.6% | 0.908 |
| Código MI/INOM | 130 | 78.5% | 0.938 |
| Tempo relativo | 139 | 59.0% | 0.919 |
| Ordenação | 99 | 76.8% | 0.965 |
| Ambíguas/informais | 457 | 65.6% | 0.895 |
| Fora do domínio | 163 | 100.0% | 0.000 |
| Subespecificadas | 65 | 67.7% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 38, 'misto': 41, 'campo_omitido': 49, 'campo_inventado': 101, 'nao_chamou': 5}
- Campos fora do schema: {}
- IoU médio de períodos: {'creationPeriod': 0.888, 'publicationPeriod': 0.944}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 5

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
