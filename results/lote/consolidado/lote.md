# Lote de validação e especificação v2 — Gemma 4 E4B

Gerado por `python -m pfc_busca.evaluation.lote`. Metodologia: `docs/lote_validacao.md`.

## Lote de validação

| Medida | Tool Calling v1 | Saída Estruturada v1 | Tool Calling v2 | Saída Estruturada v2 |
|---|---|---|---|---|
| Consultas | 1929 | 1929 | 1929 | 1929 |
| Acurácia [IC 95%] | 61.5% [59.3%–63.6%] | 62.2% [60.0%–64.3%] | 62.8% [60.7%–65.0%] | 72.4% [70.4%–74.4%] |
| Acurácia no domínio (fora de F e E) | 48.9% | 75.5% | 53.4% | 63.2% |
| F1 ponderado / macro / micro | 0.761 / 0.732 / 0.772 | 0.892 / 0.872 / 0.895 | 0.840 / 0.846 / 0.839 | 0.860 / 0.857 / 0.873 |
| Recusa: recall (recusa F) | 100.0% | 0.0% | 99.7% | 100.0% |
| Recusa: precisão | 42.0% | 0.0% | 96.3% | 56.7% |
| Recusa: F1 | 0.592 | 0.000 | 0.980 | 0.723 |
| Falsa recusa (domínio) | 32.1% | 0.0% | 0.9% | 17.8% |
| E: buscou sem filtros / não buscou / buscou com filtro (erro) | 0 / 142 / 4 | 108 / 0 / 38 | 95 / 10 / 41 | 0 / 146 / 0 |
| Acurácia, uma leitura | 55.8% | 77.2% | 56.7% | 64.2% |
| Acurácia, múltiplas leituras | 34.6% | 72.0% | 46.5% | 61.1% |
| Latência mediana (s) | 0.86 | 0.72 | 0.94 | 0.61 |
| Respostas fora do schema | 0 | 0 | 1 | 0 |

| Categoria | Tool Calling v1 | Saída Estruturada v1 | Tool Calling v2 | Saída Estruturada v2 |
|---|---|---|---|---|
| Simples (n=389) | 53.0% | 79.2% | 60.2% | 55.5% |
| Compostas (n=955) | 52.4% | 73.7% | 49.9% | 65.4% |
| Com código MI/INOM (n=281) | 77.9% | 78.3% | 50.5% | 76.5% |
| Com referência temporal relativa (n=278) | 22.7% | 65.8% | 37.4% | 61.2% |
| Com ordenação (n=199) | 39.2% | 77.4% | 52.8% | 73.4% |
| Ambíguas / variações ortográficas (n=927) | 48.1% | 72.9% | 50.3% | 61.1% |
| Subespecificadas (buscar ou esclarecer) (n=146) | 97.3% | 74.0% | 71.9% | 100.0% |
| Fora do domínio (recusa) (n=336) | 100.0% | 0.0% | 99.7% | 100.0% |

| Campo | Tool Calling v1 | Saída Estruturada v1 | Tool Calling v2 | Saída Estruturada v2 |
|---|---|---|---|---|
| `keyword` | 0.869 (P 0.83, R 0.92) | 0.773 (P 0.63, R 1.00) | 0.743 (P 0.60, R 0.98) | 0.850 (P 0.74, R 1.00) |
| `scale` | 0.821 (P 0.98, R 0.71) | 0.969 (P 0.97, R 0.97) | 0.963 (P 0.97, R 0.95) | 0.925 (P 0.98, R 0.87) |
| `productType` | 0.689 (P 0.71, R 0.67) | 0.962 (P 0.95, R 0.97) | 0.733 (P 0.60, R 0.96) | 0.882 (P 0.97, R 0.81) |
| `state` | 0.794 (P 0.98, R 0.67) | 0.865 (P 0.89, R 0.84) | 0.651 (P 0.54, R 0.83) | 0.709 (P 0.74, R 0.68) |
| `city` | 0.601 (P 0.98, R 0.43) | 0.649 (P 0.93, R 0.50) | 0.803 (P 0.82, R 0.79) | 0.437 (P 0.94, R 0.29) |
| `supplyArea` | 0.882 (P 1.00, R 0.79) | 0.999 (P 1.00, R 1.00) | 0.999 (P 1.00, R 1.00) | 0.979 (P 1.00, R 0.96) |
| `project` | 0.925 (P 0.98, R 0.88) | 0.978 (P 0.96, R 1.00) | 0.964 (P 0.98, R 0.95) | 0.943 (P 0.99, R 0.90) |
| `publicationPeriod` | 0.415 (P 0.62, R 0.31) | 0.839 (P 0.73, R 0.99) | 0.829 (P 0.75, R 0.92) | 0.830 (P 0.89, R 0.77) |
| `creationPeriod` | 0.538 (P 0.76, R 0.42) | 0.545 (P 0.73, R 0.44) | 0.829 (P 0.76, R 0.91) | 0.845 (P 0.91, R 0.79) |
| `sortField` | 0.699 (P 0.91, R 0.57) | 0.941 (P 0.93, R 0.95) | 0.959 (P 0.92, R 1.00) | 0.977 (P 0.99, R 0.96) |
| `sortDirection` | 0.748 (P 1.00, R 0.60) | 0.977 (P 1.00, R 0.95) | 0.959 (P 0.92, R 1.00) | 0.980 (P 0.99, R 0.96) |
| `limit` | 0.800 (P 0.97, R 0.68) | 0.972 (P 0.95, R 1.00) | 0.721 (P 0.56, R 1.00) | 0.924 (P 0.88, R 0.97) |

| Registro | Tool Calling v1 | Saída Estruturada v1 | Tool Calling v2 | Saída Estruturada v2 |
|---|---|---|---|---|
| coloquial (n=306) | 65.7% | 61.4% | 64.1% | 76.8% |
| contexto (n=154) | 37.7% | 75.3% | 53.9% | 66.2% |
| direto (n=389) | 69.7% | 59.4% | 64.5% | 71.0% |
| erro_digitacao (n=80) | 51.2% | 76.2% | 51.2% | 60.0% |
| formal (n=323) | 63.2% | 64.4% | 67.5% | 79.9% |
| pergunta (n=291) | 66.3% | 61.9% | 67.7% | 76.3% |
| sem_acento (n=228) | 60.1% | 48.2% | 64.5% | 70.6% |
| telegrafico (n=158) | 51.3% | 67.1% | 50.0% | 60.1% |

| Subtipo | Tool Calling v1 | Saída Estruturada v1 | Tool Calling v2 | Saída Estruturada v2 |
|---|---|---|---|---|
| VA·dois_codigos (n=12) | 100.0% | 83.3% | 100.0% | 100.0% |
| VA·duas_escalas (n=15) | 13.3% | 73.3% | 40.0% | 80.0% |
| VA·escala_qualitativa (n=32) | 0.0% | 43.8% | 18.8% | 0.0% |
| VA·estado_ou_capital (n=39) | 74.4% | 94.9% | 59.0% | 53.8% |
| VA·folha_municipio (n=33) | 63.6% | 90.9% | 87.9% | 97.0% |
| VA·periodo_sem_verbo (n=19) | 21.1% | 68.4% | 47.4% | 57.9% |
| VA·projeto_termo (n=18) | 61.1% | 50.0% | 5.6% | 11.1% |
| VA·regiao_com_criterio (n=25) | 4.0% | 60.0% | 32.0% | 0.0% |
| VE·finalidade (n=33) | 100.0% | 84.8% | 90.9% | 100.0% |
| VE·generica (n=69) | 100.0% | 100.0% | 100.0% | 100.0% |
| VE·regiao (n=44) | 90.9% | 25.0% | 13.6% | 100.0% |
| VF·armadilha_lexical (n=65) | 100.0% | 0.0% | 100.0% | 100.0% |
| VF·conceitual (n=31) | 100.0% | 0.0% | 100.0% | 100.0% |
| VF·conversa (n=14) | 100.0% | 0.0% | 92.9% | 100.0% |
| VF·cotidiano (n=51) | 100.0% | 0.0% | 100.0% | 100.0% |
| VF·dados (n=26) | 100.0% | 0.0% | 100.0% | 100.0% |
| VF·exterior (n=49) | 100.0% | 0.0% | 100.0% | 100.0% |
| VF·ficcao (n=20) | 100.0% | 0.0% | 100.0% | 100.0% |
| VF·producao (n=18) | 100.0% | 0.0% | 100.0% | 100.0% |
| VF·rotas (n=23) | 100.0% | 0.0% | 100.0% | 100.0% |
| VF·servicos (n=39) | 100.0% | 0.0% | 100.0% | 100.0% |

| Par (A × B) | Só A | Só B | p (McNemar) | B − A, acurácia [IC] | B − A, F1 [IC] |
|---|---|---|---|---|---|
| tc1se1 | 419 | 433 | 0.6561 | +0.7 p.p. [-2.4, +3.8] | +0.131 [+0.114, +0.148] |
| tc2se2 | 153 | 338 | 4.286e-17 | +9.6 p.p. [+7.4, +11.8] | +0.020 [+0.006, +0.033] |
| tc1tc2 | 251 | 277 | 0.2766 | +1.3 p.p. [-0.8, +3.7] | +0.079 [+0.061, +0.098] |
| se1se2 | 271 | 468 | 4.091e-13 | +10.2 p.p. [+7.5, +13.0] | -0.032 [-0.044, -0.020] |
| tc1se2 | 146 | 357 | 1.959e-21 | +10.9 p.p. [+8.9, +13.2] | +0.099 [+0.081, +0.119] |

## 310 consultas

| Medida | Tool Calling v1 | Saída Estruturada v1 | Tool Calling v2 | Saída Estruturada v2 |
|---|---|---|---|---|
| Consultas | 306 | 306 | 306 | 306 |
| Acurácia [IC 95%] | 60.1% [54.6%–65.5%] | 75.2% [70.0%–79.7%] | 47.4% [41.9%–53.0%] | 68.0% [62.6%–73.0%] |
| Acurácia no domínio (fora de F e E) | 59.1% | 77.2% | 46.0% | 67.1% |
| F1 ponderado / macro / micro | 0.793 / 0.741 / 0.808 | 0.902 / 0.893 / 0.904 | 0.796 / 0.826 / 0.798 | 0.859 / 0.862 / 0.871 |
| Recusa: recall (recusa F) | 100.0% | 0.0% | 100.0% | 100.0% |
| Recusa: precisão | 12.5% | 0.0% | 100.0% | 15.7% |
| Recusa: F1 | 0.222 | 0.000 | 1.000 | 0.271 |
| Falsa recusa (domínio) | 18.8% | 0.0% | 0.0% | 14.4% |
| E: buscou sem filtros / não buscou / buscou com filtro (erro) | — | — | — | — |
| Acurácia, uma leitura | 68.4% | 84.4% | 47.6% | 71.0% |
| Acurácia, múltiplas leituras | 26.9% | 52.2% | 40.3% | 53.7% |
| Latência mediana (s) | 0.72 | 0.76 | 0.81 | 0.71 |
| Respostas fora do schema | 0 | 0 | 0 | 0 |

| Categoria | Tool Calling v1 | Saída Estruturada v1 | Tool Calling v2 | Saída Estruturada v2 |
|---|---|---|---|---|
| Simples (n=100) | 78.0% | 88.0% | 58.0% | 60.0% |
| Compostas (n=180) | 52.8% | 71.7% | 36.7% | 70.0% |
| Com código MI/INOM (n=57) | 77.2% | 75.4% | 40.4% | 94.7% |
| Com referência temporal relativa (n=60) | 23.3% | 53.3% | 55.0% | 73.3% |
| Com ordenação (n=29) | 34.5% | 62.1% | 34.5% | 44.8% |
| Ambíguas / variações ortográficas (n=197) | 56.9% | 76.6% | 41.1% | 65.5% |
| Fora do domínio (recusa) (n=8) | 100.0% | 0.0% | 100.0% | 100.0% |

| Campo | Tool Calling v1 | Saída Estruturada v1 | Tool Calling v2 | Saída Estruturada v2 |
|---|---|---|---|---|
| `keyword` | 0.883 (P 0.81, R 0.97) | 0.839 (P 0.72, R 1.00) | 0.505 (P 0.34, R 1.00) | 0.917 (P 0.85, R 1.00) |
| `scale` | 0.875 (P 0.89, R 0.86) | 0.950 (P 0.92, R 0.99) | 0.976 (P 1.00, R 0.95) | 0.957 (P 0.99, R 0.93) |
| `productType` | 0.635 (P 0.57, R 0.72) | 0.989 (P 0.98, R 1.00) | 0.624 (P 0.45, R 1.00) | 0.900 (P 1.00, R 0.82) |
| `state` | 0.920 (P 0.99, R 0.86) | 0.918 (P 0.97, R 0.88) | 0.680 (P 0.53, R 0.94) | 0.758 (P 0.75, R 0.77) |
| `city` | 1.000 (P 1.00, R 1.00) | 0.962 (P 1.00, R 0.93) | 0.982 (P 0.97, R 1.00) | 0.457 (P 1.00, R 0.30) |
| `supplyArea` | 0.897 (P 0.97, R 0.83) | 1.000 (P 1.00, R 1.00) | 1.000 (P 1.00, R 1.00) | 1.000 (P 1.00, R 1.00) |
| `project` | 0.806 (P 0.79, R 0.82) | 0.759 (P 0.61, R 1.00) | 0.957 (P 0.92, R 1.00) | 0.900 (P 1.00, R 0.82) |
| `publicationPeriod` | 0.424 (P 0.47, R 0.39) | 0.707 (P 0.56, R 0.97) | 0.879 (P 0.82, R 0.95) | 0.879 (P 0.83, R 0.93) |
| `creationPeriod` | 0.378 (P 0.44, R 0.33) | 0.824 (P 0.88, R 0.78) | 0.706 (P 0.60, R 0.86) | 0.889 (P 0.89, R 0.89) |
| `sortField` | 0.641 (P 1.00, R 0.47) | 0.885 (P 1.00, R 0.79) | 0.949 (P 0.93, R 0.97) | 0.906 (P 1.00, R 0.83) |
| `sortDirection` | 0.641 (P 1.00, R 0.47) | 0.885 (P 1.00, R 0.79) | 0.949 (P 0.93, R 0.97) | 0.906 (P 1.00, R 0.83) |
| `limit` | 0.794 (P 0.93, R 0.69) | 1.000 (P 1.00, R 1.00) | 0.706 (P 0.55, R 1.00) | 0.872 (P 0.85, R 0.89) |

| Par (A × B) | Só A | Só B | p (McNemar) | B − A, acurácia [IC] | B − A, F1 [IC] |
|---|---|---|---|---|---|
| tc1se1 | 16 | 62 | 1.513e-07 | +15.0 p.p. [+9.8, +20.6] | +0.106 [+0.072, +0.147] |
| tc2se2 | 30 | 93 | 1.084e-08 | +20.6 p.p. [+14.1, +27.1] | +0.063 [+0.024, +0.098] |
| tc1tc2 | 82 | 43 | 0.0006181 | -12.7 p.p. [-19.9, -6.2] | +0.001 [-0.044, +0.052] |
| se1se2 | 66 | 44 | 0.04476 | -7.2 p.p. [-13.4, -0.7] | -0.043 [-0.076, -0.011] |
| tc1se2 | 49 | 73 | 0.03688 | +7.8 p.p. [+1.0, +14.4] | +0.064 [+0.023, +0.110] |
