# gemma4:e4b-it-qat [saida-estruturada-v2] — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-29T22:16:36

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 73.8% |
| Precisão ponderada | 0.918 |
| Recall ponderado | 0.833 |
| F1 ponderado | 0.857 |
| F1 macro | 0.854 |
| Micro P / R / F1 | 0.908 / 0.833 / 0.869 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 282 | 611 | 731 | 1472 | 2873 | 415 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 241 | 215 | 78 | 3 | 0.734 | 0.986 | 0.841 |
| scale | 197 | 166 | 2 | 29 | 0.988 | 0.851 | 0.915 |
| productType | 192 | 154 | 5 | 36 | 0.969 | 0.811 | 0.883 |
| state | 137 | 77 | 17 | 49 | 0.819 | 0.611 | 0.700 |
| city | 102 | 28 | 2 | 72 | 0.933 | 0.280 | 0.431 |
| supplyArea | 175 | 169 | 0 | 6 | 1.000 | 0.966 | 0.983 |
| project | 99 | 86 | 3 | 11 | 0.966 | 0.887 | 0.925 |
| publicationPeriod | 105 | 87 | 11 | 10 | 0.888 | 0.897 | 0.892 |
| creationPeriod | 34 | 26 | 1 | 7 | 0.963 | 0.788 | 0.867 |
| sortField | 99 | 88 | 1 | 11 | 0.989 | 0.889 | 0.936 |
| sortDirection | 99 | 88 | 1 | 11 | 0.989 | 0.889 | 0.936 |
| limit | 61 | 57 | 4 | 4 | 0.934 | 0.934 | 0.934 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 61.5% | 0.703 |
| Compostas | 466 | 65.9% | 0.876 |
| Código MI/INOM | 130 | 80.0% | 0.941 |
| Tempo relativo | 139 | 69.8% | 0.897 |
| Ordenação | 99 | 73.7% | 0.904 |
| Ambíguas/informais | 457 | 62.6% | 0.852 |
| Fora do domínio | 163 | 100.0% | 0.000 |
| Subespecificadas | 65 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 116, 'valor_errado': 41, 'campo_inventado': 36, 'misto': 39, 'campo_omitido': 16}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.898, 'creationPeriod': 0.975}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 116

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
