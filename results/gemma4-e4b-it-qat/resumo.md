# gemma4:e4b-it-qat — resumo da avaliação

930 execuções · repetições [1, 2, 3] · gerado em 2026-09-26T14:50:40

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 918 |
| Acurácia por consulta | 60.2% |
| Precisão ponderada | 0.853 |
| Recall ponderado | 0.763 |
| F1 ponderado | 0.793 |
| F1 macro | 0.741 |
| Micro P / R / F1 | 0.849 / 0.771 / 0.808 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 918 | 405 | 725 | 813 | 1230 | 4849 | 500 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 183 | 151 | 35 | 5 | 0.812 | 0.968 | 0.883 |
| scale | 252 | 196 | 24 | 32 | 0.891 | 0.860 | 0.875 |
| productType | 132 | 95 | 72 | 37 | 0.569 | 0.720 | 0.635 |
| state | 390 | 332 | 3 | 55 | 0.991 | 0.858 | 0.920 |
| city | 84 | 84 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 120 | 100 | 3 | 20 | 0.971 | 0.833 | 0.897 |
| project | 33 | 27 | 7 | 6 | 0.794 | 0.818 | 0.806 |
| publicationPeriod | 153 | 42 | 48 | 66 | 0.467 | 0.389 | 0.424 |
| creationPeriod | 30 | 7 | 9 | 14 | 0.438 | 0.333 | 0.378 |
| sortField | 87 | 41 | 0 | 46 | 1.000 | 0.471 | 0.641 |
| sortDirection | 87 | 41 | 0 | 46 | 1.000 | 0.471 | 0.641 |
| limit | 36 | 25 | 2 | 11 | 0.926 | 0.694 | 0.794 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 300 | 77.3% | 0.874 |
| Compostas | 540 | 53.1% | 0.794 |
| Código MI/INOM | 171 | 77.2% | 0.878 |
| Tempo relativo | 180 | 25.6% | 0.547 |
| Ordenação | 87 | 35.6% | 0.650 |
| Ambíguas/informais | 591 | 56.9% | 0.825 |
| Fora do domínio | 24 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 37.9% |
| N | 111 | 55.9% |
| G | 741 | 62.9% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 96, 'misto': 22, 'campo_omitido': 7, 'campo_inventado': 79, 'nao_chamou': 161}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.667, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 161

## Observacionais (fora das métricas principais)

12 casos · acurácia 50.0% · chamou sem dever: 0

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 60.1% | 0.795 | 736 |
| 2 | 61.1% | 0.795 | 720 |
| 3 | 59.5% | 0.789 | 724 |
