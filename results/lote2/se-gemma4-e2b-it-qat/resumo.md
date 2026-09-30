# gemma4:e2b-it-qat [saida-estruturada] — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-30T12:28:45

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 36.5% |
| Precisão ponderada | 0.605 |
| Recall ponderado | 0.841 |
| F1 ponderado | 0.683 |
| F1 macro | 0.692 |
| Micro P / R / F1 | 0.580 / 0.853 / 0.691 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 156 | 439 | 481 | 913 | 1455 | 227 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 241 | 190 | 270 | 9 | 0.413 | 0.955 | 0.577 |
| scale | 197 | 130 | 41 | 36 | 0.760 | 0.783 | 0.772 |
| productType | 192 | 53 | 153 | 33 | 0.257 | 0.616 | 0.363 |
| state | 139 | 107 | 69 | 28 | 0.608 | 0.793 | 0.688 |
| city | 100 | 46 | 26 | 51 | 0.639 | 0.474 | 0.544 |
| supplyArea | 175 | 174 | 3 | 0 | 0.983 | 1.000 | 0.991 |
| project | 97 | 56 | 43 | 4 | 0.566 | 0.933 | 0.704 |
| publicationPeriod | 99 | 65 | 59 | 0 | 0.524 | 1.000 | 0.688 |
| creationPeriod | 40 | 11 | 9 | 20 | 0.550 | 0.355 | 0.431 |
| sortField | 99 | 93 | 39 | 0 | 0.705 | 1.000 | 0.827 |
| sortDirection | 99 | 88 | 42 | 0 | 0.677 | 1.000 | 0.807 |
| limit | 41 | 40 | 7 | 1 | 0.851 | 0.976 | 0.909 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 68.8% | 0.771 |
| Compostas | 466 | 32.2% | 0.714 |
| Código MI/INOM | 130 | 66.9% | 0.870 |
| Tempo relativo | 139 | 36.7% | 0.701 |
| Ordenação | 99 | 50.5% | 0.855 |
| Ambíguas/informais | 457 | 37.2% | 0.693 |
| Fora do domínio | 163 | 0.0% | 0.000 |
| Subespecificadas | 65 | 43.1% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_inventado': 122, 'misto': 134, 'valor_errado': 142, 'campo_omitido': 39, 'chamou_sem_dever': 163}
- Campos fora do schema: {}
- IoU médio de períodos: {'creationPeriod': 0.822, 'publicationPeriod': 0.906}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
