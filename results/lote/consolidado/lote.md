# Lote de validação e especificação v2 — Gemma 4 E4B

Gerado por `python -m pfc_busca.evaluation.lote`. Metodologia: `docs/lote_validacao.md`.

## 310 consultas

| Medida | Tool Calling v1 | Saída Estruturada v1 |
|---|---|---|
| Consultas | 306 | 306 |
| Acurácia [IC 95%] | 60.1% [54.6%–65.5%] | 75.2% [70.0%–79.7%] |
| Acurácia no domínio (fora de F e E) | 59.1% | 77.2% |
| F1 ponderado / macro / micro | 0.793 / 0.741 / 0.808 | 0.902 / 0.893 / 0.904 |
| Recusa: recall (recusa F) | 100.0% | 0.0% |
| Recusa: precisão | 12.5% | 0.0% |
| Recusa: F1 | 0.222 | 0.000 |
| Falsa recusa (domínio) | 18.8% | 0.0% |
| E: buscou sem filtros / não buscou / buscou com filtro (erro) | — | — |
| Acurácia, uma leitura | 68.4% | 84.4% |
| Acurácia, múltiplas leituras | 26.9% | 52.2% |
| Latência mediana (s) | 0.72 | 0.76 |
| Respostas fora do schema | 0 | 0 |

| Categoria | Tool Calling v1 | Saída Estruturada v1 |
|---|---|---|
| Simples (n=100) | 78.0% | 88.0% |
| Compostas (n=180) | 52.8% | 71.7% |
| Com código MI/INOM (n=57) | 77.2% | 75.4% |
| Com referência temporal relativa (n=60) | 23.3% | 53.3% |
| Com ordenação (n=29) | 34.5% | 62.1% |
| Ambíguas / variações ortográficas (n=197) | 56.9% | 76.6% |
| Fora do domínio (recusa) (n=8) | 100.0% | 0.0% |

| Campo | Tool Calling v1 | Saída Estruturada v1 |
|---|---|---|
| `keyword` | 0.883 (P 0.81, R 0.97) | 0.839 (P 0.72, R 1.00) |
| `scale` | 0.875 (P 0.89, R 0.86) | 0.950 (P 0.92, R 0.99) |
| `productType` | 0.635 (P 0.57, R 0.72) | 0.989 (P 0.98, R 1.00) |
| `state` | 0.920 (P 0.99, R 0.86) | 0.918 (P 0.97, R 0.88) |
| `city` | 1.000 (P 1.00, R 1.00) | 0.962 (P 1.00, R 0.93) |
| `supplyArea` | 0.897 (P 0.97, R 0.83) | 1.000 (P 1.00, R 1.00) |
| `project` | 0.806 (P 0.79, R 0.82) | 0.759 (P 0.61, R 1.00) |
| `publicationPeriod` | 0.424 (P 0.47, R 0.39) | 0.707 (P 0.56, R 0.97) |
| `creationPeriod` | 0.378 (P 0.44, R 0.33) | 0.824 (P 0.88, R 0.78) |
| `sortField` | 0.641 (P 1.00, R 0.47) | 0.885 (P 1.00, R 0.79) |
| `sortDirection` | 0.641 (P 1.00, R 0.47) | 0.885 (P 1.00, R 0.79) |
| `limit` | 0.794 (P 0.93, R 0.69) | 1.000 (P 1.00, R 1.00) |

| Par (A × B) | Só A | Só B | p (McNemar) | B − A, acurácia [IC] | B − A, F1 [IC] |
|---|---|---|---|---|---|
| tc1se1 | 16 | 62 | 1.513e-07 | +15.0 p.p. [+9.8, +20.6] | +0.106 [+0.072, +0.147] |
