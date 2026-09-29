# gemma4:e4b-it-qat [saida-estruturada-v2] — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-29T03:14:10

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 68.0% |
| Precisão ponderada | 0.896 |
| Recall ponderado | 0.847 |
| F1 ponderado | 0.859 |
| F1 macro | 0.862 |
| Micro P / R / F1 | 0.893 / 0.850 / 0.871 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 227 | 715 | 752 | 1470 | 2789 | 387 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 62 | 61 | 11 | 0 | 0.847 | 1.000 | 0.917 |
| scale | 84 | 77 | 1 | 6 | 0.987 | 0.928 | 0.957 |
| productType | 44 | 36 | 0 | 8 | 1.000 | 0.818 | 0.900 |
| state | 130 | 80 | 27 | 24 | 0.748 | 0.769 | 0.758 |
| city | 27 | 8 | 0 | 19 | 1.000 | 0.296 | 0.457 |
| supplyArea | 40 | 40 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 9 | 0 | 2 | 1.000 | 0.818 | 0.900 |
| publicationPeriod | 51 | 40 | 8 | 3 | 0.833 | 0.930 | 0.879 |
| creationPeriod | 10 | 8 | 1 | 1 | 0.889 | 0.889 | 0.889 |
| sortField | 29 | 24 | 0 | 5 | 1.000 | 0.828 | 0.906 |
| sortDirection | 29 | 24 | 0 | 5 | 1.000 | 0.828 | 0.906 |
| limit | 19 | 17 | 3 | 2 | 0.850 | 0.895 | 0.872 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 60.0% | 0.673 |
| Compostas | 180 | 70.0% | 0.892 |
| Código MI/INOM | 57 | 94.7% | 0.981 |
| Tempo relativo | 60 | 73.3% | 0.916 |
| Ordenação | 29 | 44.8% | 0.841 |
| Ambíguas/informais | 197 | 65.5% | 0.860 |
| Fora do domínio | 8 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 63.6% |
| N | 37 | 64.9% |
| G | 247 | 68.8% |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 3, 'valor_errado': 34, 'nao_chamou': 43, 'campo_inventado': 8, 'misto': 7, 'campo_fora_do_schema': 3}
- Campos fora do schema: {'Cartas Temáticas Não SCN': 3}
- IoU médio de períodos: {'publicationPeriod': 0.794, 'creationPeriod': 0.889}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 43

## Observacionais (fora das métricas principais)

4 casos · acurácia 50.0% · chamou sem dever: 0
