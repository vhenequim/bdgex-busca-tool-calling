# gemma4:e2b-it-qat — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-30T12:21:02

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 58.1% |
| Precisão ponderada | 0.767 |
| Recall ponderado | 0.781 |
| F1 ponderado | 0.759 |
| F1 macro | 0.732 |
| Micro P / R / F1 | 0.748 / 0.782 / 0.765 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 160 | 500 | 539 | 880 | 3310 | 269 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 241 | 199 | 164 | 6 | 0.548 | 0.971 | 0.701 |
| scale | 197 | 122 | 33 | 42 | 0.787 | 0.744 | 0.765 |
| productType | 192 | 148 | 31 | 32 | 0.827 | 0.822 | 0.825 |
| state | 133 | 89 | 18 | 43 | 0.832 | 0.674 | 0.745 |
| city | 106 | 67 | 21 | 38 | 0.761 | 0.638 | 0.694 |
| supplyArea | 175 | 174 | 0 | 1 | 1.000 | 0.994 | 0.997 |
| project | 98 | 87 | 4 | 8 | 0.956 | 0.916 | 0.935 |
| publicationPeriod | 95 | 49 | 36 | 25 | 0.576 | 0.662 | 0.616 |
| creationPeriod | 44 | 13 | 11 | 22 | 0.542 | 0.371 | 0.441 |
| sortField | 99 | 44 | 9 | 54 | 0.830 | 0.449 | 0.583 |
| sortDirection | 99 | 58 | 25 | 25 | 0.699 | 0.699 | 0.699 |
| limit | 43 | 36 | 13 | 7 | 0.735 | 0.837 | 0.783 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 71.4% | 0.786 |
| Compostas | 466 | 43.1% | 0.787 |
| Código MI/INOM | 130 | 74.6% | 0.909 |
| Tempo relativo | 139 | 28.8% | 0.682 |
| Ordenação | 99 | 28.3% | 0.756 |
| Ambíguas/informais | 457 | 45.3% | 0.760 |
| Fora do domínio | 163 | 93.9% | 0.000 |
| Subespecificadas | 65 | 81.5% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'misto': 130, 'nao_chamou': 69, 'valor_errado': 78, 'campo_inventado': 65, 'campo_omitido': 44, 'chamou_sem_dever': 10}
- Campos fora do schema: {}
- IoU médio de períodos: {'creationPeriod': 0.799, 'publicationPeriod': 0.979}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 69

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
