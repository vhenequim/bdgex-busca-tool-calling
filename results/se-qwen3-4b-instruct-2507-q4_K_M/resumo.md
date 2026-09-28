# qwen3:4b-instruct-2507-q4_K_M [saida-estruturada] — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-28T17:08:27

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 60.1% |
| Precisão ponderada | 0.800 |
| Recall ponderado | 0.866 |
| F1 ponderado | 0.808 |
| F1 macro | 0.799 |
| Micro P / R / F1 | 0.749 / 0.862 / 0.801 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 231 | 687 | 843 | 1969 | 3115 | 545 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 62 | 57 | 36 | 0 | 0.613 | 1.000 | 0.760 |
| scale | 84 | 66 | 9 | 10 | 0.880 | 0.868 | 0.874 |
| productType | 44 | 42 | 49 | 2 | 0.462 | 0.955 | 0.622 |
| state | 130 | 109 | 19 | 19 | 0.852 | 0.852 | 0.852 |
| city | 27 | 20 | 2 | 7 | 0.909 | 0.741 | 0.816 |
| supplyArea | 40 | 40 | 2 | 0 | 0.952 | 1.000 | 0.976 |
| project | 10 | 10 | 1 | 0 | 0.909 | 1.000 | 0.952 |
| publicationPeriod | 51 | 39 | 21 | 0 | 0.650 | 1.000 | 0.788 |
| creationPeriod | 10 | 6 | 3 | 3 | 0.667 | 0.667 | 0.667 |
| sortField | 29 | 15 | 0 | 14 | 1.000 | 0.517 | 0.682 |
| sortDirection | 29 | 15 | 0 | 14 | 1.000 | 0.517 | 0.682 |
| limit | 11 | 11 | 2 | 0 | 0.846 | 1.000 | 0.917 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 77.0% | 0.820 |
| Compostas | 180 | 51.1% | 0.802 |
| Código MI/INOM | 57 | 82.5% | 0.927 |
| Tempo relativo | 60 | 66.7% | 0.886 |
| Ordenação | 29 | 27.6% | 0.712 |
| Ambíguas/informais | 197 | 58.4% | 0.799 |
| Fora do domínio | 8 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 54.5% |
| N | 37 | 51.4% |
| G | 247 | 61.9% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 20, 'campo_omitido': 12, 'campo_inventado': 44, 'misto': 38, 'chamou_sem_dever': 8}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.804, 'creationPeriod': 0.857}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 25.0% · chamou sem dever: 2
