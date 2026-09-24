# Comparativo entre modelos

| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |
|---|---|---|---|---|---|---|---|---|---|---|
| GPT-OSS 20B (Groq) | 306 | 89.2% | 85.2–92.2% | 0.959 | 0.945 | 0.946 | 0.933 | 530 | 1496 | 0 |
| GPT-OSS 120B (Groq) | 306 | 89.9% | 86.0–92.8% | 0.965 | 0.951 | 0.956 | 0.947 | 655 | 1611 | 0 |

## F1 ponderado por categoria

| Categoria | GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) |
|---|---|---|
| Simples | 0.985 | 0.979 |
| Compostas | 0.937 | 0.950 |
| Com código MI/INOM | 0.985 | 0.986 |
| Com referência temporal relativa | 0.938 | 0.933 |
| Com ordenação | 0.837 | 0.926 |
| Ambíguas / variações ortográficas | 0.952 | 0.951 |

## Acurácia por categoria

| Categoria | GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) |
|---|---|---|
| Simples | 97.0% | 96.0% |
| Compostas | 84.4% | 85.6% |
| Com código MI/INOM | 94.7% | 94.7% |
| Com referência temporal relativa | 83.3% | 83.3% |
| Com ordenação | 48.3% | 79.3% |
| Ambíguas / variações ortográficas | 88.8% | 86.8% |
| Fora do domínio (recusa) | 100.0% | 100.0% |

## F1 por campo

| Campo | Ocorr. | GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) |
|---|---|---|---|
| `keyword` | 61 | 0.967 | 0.967 |
| `scale` | 84 | 0.963 | 0.963 |
| `productType` | 44 | 1.000 | 0.977 |
| `state` | 127 | 0.980 | 0.962 |
| `city` | 31 | 0.954 | 1.000 |
| `supplyArea` | 40 | 1.000 | 1.000 |
| `project` | 11 | 0.952 | 1.000 |
| `publicationPeriod` | 51 | 0.928 | 0.931 |
| `creationPeriod` | 10 | 1.000 | 0.824 |
| `sortField` | 29 | 0.739 | 0.885 |
| `sortDirection` | 29 | 0.739 | 0.885 |
| `limit` | 15 | 0.968 | 0.973 |

## Acurácia por origem do caso

| Origem | GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) |
|---|---|---|
| P | 77.3% | 68.2% |
| N | 83.8% | 81.1% |
| G | 91.1% | 93.1% |

## Diagnósticos

### GPT-OSS 20B (Groq)

- tipos de erro: {'misto': 2, 'valor_errado': 13, 'campo_omitido': 11, 'nao_chamou': 2, 'campo_inventado': 5}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.946, 'creationPeriod': 1.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 2
- observacionais: 4 casos, acurácia 50.0%, chamou sem dever 1
- thinking desativado: False · Ollama None · repetições [1]

### GPT-OSS 120B (Groq)

- tipos de erro: {'campo_omitido': 6, 'valor_errado': 7, 'campo_inventado': 9, 'nao_chamou': 6, 'misto': 3}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.945, 'creationPeriod': 1.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 6
- observacionais: 4 casos, acurácia 25.0%, chamou sem dever 1
- thinking desativado: False · Ollama None · repetições [1]

