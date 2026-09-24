# Comparativo entre modelos

| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |
|---|---|---|---|---|---|---|---|---|---|---|
| GPT-OSS 20B (Groq) | 71 | 81.7% | 71.2–89.0% | 0.927 | 0.934 | 0.925 | 0.927 | 589 | 1496 | 0 |
| GPT-OSS 120B (Groq) | 71 | 77.5% | 66.5–85.6% | 0.940 | 0.882 | 0.899 | 0.902 | 696 | 1274 | 0 |

## F1 ponderado por categoria

| Categoria | GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) |
|---|---|---|
| Simples | 0.953 | 0.939 |
| Compostas | 0.917 | 0.891 |
| Com código MI/INOM | 0.971 | 0.972 |
| Com referência temporal relativa | 0.959 | 0.915 |
| Com ordenação | 0.875 | 0.798 |
| Ambíguas / variações ortográficas | 0.888 | 0.856 |

## Acurácia por categoria

| Categoria | GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) |
|---|---|---|
| Simples | 90.9% | 90.9% |
| Compostas | 75.0% | 70.5% |
| Com código MI/INOM | 86.7% | 86.7% |
| Com referência temporal relativa | 80.0% | 66.7% |
| Com ordenação | 50.0% | 50.0% |
| Ambíguas / variações ortográficas | 73.2% | 65.9% |
| Fora do domínio (recusa) | 100.0% | 100.0% |

## F1 por campo

| Campo | Ocorr. | GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) |
|---|---|---|---|
| `keyword` | 19 | 0.919 | 0.919 |
| `scale` | 17 | 0.938 | 0.903 |
| `productType` | 14 | 1.000 | 0.929 |
| `state` | 18 | 0.895 | 0.947 |
| `city` | 7 | 0.875 | 1.000 |
| `supplyArea` | 17 | 1.000 | 1.000 |
| `project` | 5 | 1.000 | 1.000 |
| `publicationPeriod` | 14 | 0.923 | 0.880 |
| `creationPeriod` | 2 | 1.000 | 1.000 |
| `sortField` | 10 | 0.824 | 0.667 |
| `sortDirection` | 10 | 0.824 | 0.667 |
| `limit` | 6 | 0.923 | 0.909 |

## Acurácia por origem do caso

| Origem | GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) |
|---|---|---|
| P | 77.3% | 68.2% |
| N | 83.8% | 81.1% |
| G | 83.3% | 83.3% |

## Diagnósticos

### GPT-OSS 20B (Groq)

- tipos de erro: {'misto': 1, 'valor_errado': 4, 'campo_omitido': 3, 'nao_chamou': 1, 'campo_inventado': 4}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.913, 'creationPeriod': 1.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 1
- observacionais: 4 casos, acurácia 50.0%, chamou sem dever 1
- thinking desativado: False · Ollama None · repetições [1]

### GPT-OSS 120B (Groq)

- tipos de erro: {'campo_omitido': 4, 'valor_errado': 5, 'campo_inventado': 3, 'nao_chamou': 4}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.837, 'creationPeriod': 1.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 4
- observacionais: 4 casos, acurácia 25.0%, chamou sem dever 1
- thinking desativado: False · Ollama None · repetições [1]

