# gemma4:e2b-it-qat [saida-estruturada-v3] — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-30T12:12:22

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 65.4% |
| Precisão ponderada | 0.901 |
| Recall ponderado | 0.715 |
| F1 ponderado | 0.786 |
| F1 macro | 0.777 |
| Micro P / R / F1 | 0.883 / 0.715 / 0.790 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 145 | 441 | 593 | 1526 | 2274 | 437 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 241 | 193 | 85 | 30 | 0.694 | 0.865 | 0.770 |
| scale | 197 | 107 | 22 | 68 | 0.829 | 0.611 | 0.704 |
| productType | 192 | 124 | 0 | 68 | 1.000 | 0.646 | 0.785 |
| state | 139 | 86 | 4 | 53 | 0.956 | 0.619 | 0.751 |
| city | 100 | 53 | 2 | 46 | 0.964 | 0.535 | 0.688 |
| supplyArea | 175 | 132 | 3 | 40 | 0.978 | 0.767 | 0.860 |
| project | 93 | 71 | 5 | 17 | 0.934 | 0.807 | 0.866 |
| publicationPeriod | 103 | 64 | 7 | 34 | 0.901 | 0.653 | 0.757 |
| creationPeriod | 36 | 19 | 4 | 13 | 0.826 | 0.594 | 0.691 |
| sortField | 99 | 84 | 4 | 11 | 0.955 | 0.884 | 0.918 |
| sortDirection | 99 | 87 | 1 | 11 | 0.989 | 0.888 | 0.935 |
| limit | 40 | 17 | 0 | 23 | 1.000 | 0.425 | 0.596 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 78.6% | 0.864 |
| Compostas | 466 | 42.7% | 0.763 |
| Código MI/INOM | 130 | 83.8% | 0.923 |
| Tempo relativo | 139 | 46.8% | 0.749 |
| Ordenação | 99 | 43.4% | 0.776 |
| Ambíguas/informais | 457 | 50.5% | 0.767 |
| Fora do domínio | 163 | 98.8% | 0.000 |
| Subespecificadas | 65 | 92.3% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 96, 'valor_errado': 29, 'campo_omitido': 106, 'campo_inventado': 40, 'misto': 54, 'chamou_sem_dever': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.966, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 96

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
