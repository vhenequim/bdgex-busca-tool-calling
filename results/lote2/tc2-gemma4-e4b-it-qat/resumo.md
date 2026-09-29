# gemma4:e4b-it-qat — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-29T20:56:52

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 62.1% |
| Precisão ponderada | 0.782 |
| Recall ponderado | 0.937 |
| F1 ponderado | 0.842 |
| F1 macro | 0.842 |
| Micro P / R / F1 | 0.754 / 0.940 / 0.837 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 285 | 913 | 911 | 1396 | 2580 | 307 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 239 | 170 | 103 | 8 | 0.623 | 0.955 | 0.754 |
| scale | 197 | 176 | 7 | 14 | 0.962 | 0.926 | 0.944 |
| productType | 192 | 182 | 134 | 8 | 0.576 | 0.958 | 0.719 |
| state | 135 | 77 | 54 | 16 | 0.588 | 0.828 | 0.688 |
| city | 106 | 80 | 19 | 20 | 0.808 | 0.800 | 0.804 |
| supplyArea | 175 | 175 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 98 | 88 | 5 | 7 | 0.946 | 0.926 | 0.936 |
| publicationPeriod | 93 | 72 | 24 | 5 | 0.750 | 0.935 | 0.832 |
| creationPeriod | 46 | 33 | 8 | 5 | 0.805 | 0.868 | 0.835 |
| sortField | 99 | 99 | 7 | 0 | 0.934 | 1.000 | 0.966 |
| sortDirection | 99 | 99 | 7 | 0 | 0.934 | 1.000 | 0.966 |
| limit | 59 | 59 | 60 | 0 | 0.496 | 1.000 | 0.663 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 67.7% | 0.800 |
| Compostas | 466 | 46.6% | 0.860 |
| Código MI/INOM | 130 | 49.2% | 0.827 |
| Tempo relativo | 139 | 40.3% | 0.855 |
| Ordenação | 99 | 56.6% | 0.921 |
| Ambíguas/informais | 457 | 49.9% | 0.840 |
| Fora do domínio | 163 | 100.0% | 0.000 |
| Subespecificadas | 65 | 64.6% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 109, 'misto': 57, 'campo_inventado': 167, 'nao_chamou': 3, 'campo_omitido': 22}
- Campos fora do schema: {}
- IoU médio de períodos: {'creationPeriod': 0.884, 'publicationPeriod': 0.975}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 1 {'args_invalidos': 1}
- Não chamou a ferramenta quando devia: 3

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
