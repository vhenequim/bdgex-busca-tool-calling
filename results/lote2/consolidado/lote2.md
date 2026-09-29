# Lote 2 — teste da v3 (Gemma 4 E4B)

Gerado por `python -m pfc_busca.evaluation.lote2`. Plano de análise: `docs/v3.md`, seção 3 (fixado antes da rodada). Regras da decomposição: `pfc_busca/evaluation/lote2.py`.

- Conjunto: `data/lote_validacao_2.json` (945 consultas, fora as observacionais).
- Rodadas: `results/lote2` — presentes: tc1, tc2, tc3d, tc3a, tc3, se3, se1, se2; ausentes: nenhuma.
- Melhor configuração v1/v2 isolada (maior acurácia): Saída Estruturada v2 (se2).

| Rodada | Pasta | Consultas | Cobertura | Descartadas na repontuação |
|---|---|---|---|---|
| tc1 | `results/lote2/gemma4-e4b-it-qat` | 945 | 100.0% | 0 |
| tc2 | `results/lote2/tc2-gemma4-e4b-it-qat` | 945 | 100.0% | 0 |
| tc3d | `results/lote2/tc3d-gemma4-e4b-it-qat` | 945 | 100.0% | 0 |
| tc3a | `results/lote2/tc3a-gemma4-e4b-it-qat` | 945 | 100.0% | 0 |
| tc3 | `results/lote2/tc3-gemma4-e4b-it-qat` | 945 | 100.0% | 0 |
| se3 | `results/lote2/se3-gemma4-e4b-it-qat` | 945 | 100.0% | 0 |
| se1 | `results/lote2/se-gemma4-e4b-it-qat` | 945 | 100.0% | 0 |
| se2 | `results/lote2/se2-gemma4-e4b-it-qat` | 945 | 100.0% | 0 |

## Medidas por configuração

| Medida | TC v1 | TC v2 | TC v3d | TC v3a | TC v3 | SE v3 | SE v1 | SE v2 | Duas etapas |
|---|---|---|---|---|---|---|---|---|---|
| Consultas | 945 | 945 | 945 | 945 | 945 | 945 | 945 | 945 | 945 |
| Acurácia [IC 95%] | 58.6% [55.5%–61.7%] | 62.1% [59.0%–65.2%] | 75.2% [72.4%–77.9%] | 83.1% [80.5%–85.3%] | 94.4% [92.7%–95.7%] | 87.8% [85.6%–89.8%] | 61.3% [58.1%–64.3%] | 73.8% [70.9%–76.5%] | 78.6% [75.9%–81.1%] |
| Acurácia no domínio (fora de F e E) | 45.9% | 53.3% | 70.3% | 79.8% | 94.4% | 84.4% | 74.8% | 65.4% | 74.6% |
| Recusa em F: precisão / recall / F1 | 39.1% / 100.0% / 0.562 | 98.2% / 100.0% / 0.991 | 97.0% / 100.0% / 0.985 | 92.4% / 96.3% / 0.943 | 98.7% / 95.1% / 0.969 | 81.9% / 100.0% / 0.901 | 0.0% / 0.0% / 0.000 | 58.4% / 100.0% / 0.738 | 98.2% / 100.0% / 0.991 |
| Falsa recusa (domínio) | 35.4% | 0.4% | 0.7% | 1.8% | 0.3% | 5.0% | 0.0% | 16.2% | 0.4% |
| E: acurácia (buscou sem filtros / não buscou / com filtro) | 95.4% (0 / 62 / 3) | 64.6% (33 / 9 / 23) | 67.7% (37 / 7 / 21) | 86.2% (37 / 19 / 9) | 92.3% (41 / 19 / 5) | 95.4% (1 / 61 / 3) | 66.2% (43 / 0 / 22) | 100.0% (0 / 65 / 0) | 69.2% (36 / 9 / 20) |
| F1 ponderado dos campos | 0.731 | 0.842 | 0.896 | 0.929 | 0.981 | 0.946 | 0.895 | 0.857 | 0.900 |
| Efeito: sigla em state | 0.0% (0/90) | 36.8% (46/125) | 0.0% (0/112) | 0.0% (0/97) | 0.0% (0/127) | 0.0% (0/139) | 0.0% (0/125) | 13.8% (13/94) | 0.0% (0/125) |
| Efeito: prefixo no código | 4.2% (2/48) | 89.8% (44/49) | 2.0% (1/49) | 4.1% (2/49) | 2.0% (1/49) | 0.0% (0/49) | 4.1% (2/49) | 16.3% (8/49) | 4.1% (2/49) |
| Efeito: limit sem pedido | 0.9% (4/429) | 9.2% (60/650) | 6.5% (42/648) | 1.4% (9/640) | 0.3% (2/651) | 0.2% (1/621) | 0.5% (3/653) | 0.7% (4/544) | 0.5% (3/650) |
| Efeito: productType sem pedido | 12.2% (41/336) | 22.6% (118/523) | 5.2% (27/521) | 0.6% (3/516) | 0.0% (0/523) | 0.0% (0/504) | 0.4% (2/525) | 0.7% (3/432) | 0.4% (2/523) |
| Latência mediana / p95 (s) | 0.85 / 1.41 | 0.91 / 1.40 | 0.90 / 1.38 | 1.37 / 3.35 | 1.47 / 4.96 | 0.78 / 2.55 | 0.72 / 1.44 | 0.61 / 1.47 | 1.45 / 2.79 |
| Chamadas ao modelo por consulta | 1.00 | 1.00 | 1.01 | 1.82 | 2.06 | 1.23 | 1.00 | 1.00 | 1.81 |
| Consultas com pergunta | — | — | 0 | 96 | 133 | — | — | — | — |
| Consultas com pergunta em texto | — | — | 0 | 49 | 81 | — | — | — | — |
| Recusas contestadas | — | — | 0 | 0 | 20 | 67 | — | — | — |
| Consultas com chamada escrita como texto (v3: interpretada) | 0 (não interpretada) | 12 (não interpretada) | 7 | 235 | 236 | — | — | — | — |
| Respostas fora do schema / erros de infraestrutura | 0 / 0 | 1 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

## Pares (só as consultas presentes nas duas configurações)

| Grupo | Par (A × B) | n | Só A | Só B | p (McNemar) | B − A, acurácia [IC] | B − A, F1 [IC] |
|---|---|---|---|---|---|---|---|
| principal | TC v3 × SE v3 | 945 | 95 | 33 | 3.811e-08 | -6.6 p.p. [-8.9, -4.2] | -0.035 [-0.047, -0.025] |
| degraus | TC v1 × TC v2 | 945 | 126 | 159 | 0.05783 | +3.5 p.p. [+0.0, +7.0] | +0.111 [+0.083, +0.142] |
| degraus | TC v2 × TC v3d | 945 | 26 | 150 | 2.162e-22 | +13.1 p.p. [+10.5, +15.8] | +0.053 [+0.042, +0.066] |
| degraus | TC v3d × TC v3a | 945 | 55 | 129 | 4.925e-08 | +7.8 p.p. [+5.1, +10.5] | +0.033 [+0.018, +0.047] |
| degraus | TC v3a × TC v3 | 945 | 12 | 119 | 2.587e-23 | +11.3 p.p. [+9.1, +13.8] | +0.052 [+0.042, +0.064] |
| secundarios | melhor isolada (SE v2) × TC v3 | 945 | 29 | 224 | 1.657e-38 | +20.6 p.p. [+17.8, +23.7] | +0.124 [+0.107, +0.143] |
| secundarios | Duas etapas × TC v3 | 945 | 25 | 174 | 1.148e-28 | +15.8 p.p. [+13.1, +18.4] | +0.081 [+0.068, +0.096] |
| secundarios | Duas etapas × SE v3 | 945 | 53 | 140 | 3.012e-10 | +9.2 p.p. [+6.6, +12.1] | +0.046 [+0.031, +0.061] |
| secundarios | melhor isolada (SE v2) × SE v3 | 945 | 29 | 162 | 1.316e-23 | +14.1 p.p. [+11.4, +16.9] | +0.089 [+0.072, +0.106] |

## Decomposição do acerto

| Contagem | TC v3a | TC v3 | SE v3 |
|---|---|---|---|
| n (com traço) | 945 | 945 | 945 |
| sem traço | 0 | 0 | 0 |
| primeira decisão certa | 784 | 784 | 705 |
| final certa | 785 | 892 | 830 |
| consertadas | 1 | 112 | 125 |
|   dando o valor | 0 | 60 | 54 |
|   mandando remover | 0 | 19 | 20 |
|   corrigindo a forma | 1 | 12 | 4 |
|   apontando o campo | 0 | 11 | 21 |
|   recusa contestada | 0 | 10 | 26 |
|   remover ou forma (o agregado do plano) | 1 | 31 | 24 |
|   sem mensagem | 0 | 0 | 0 |
| estragadas | 0 | 4 | 0 |
|   por erro de infraestrutura (não pelo retorno) | 0 | 0 | 0 |
| execuções com erro de infraestrutura | 0 | 0 | 0 |
| consertadas que receberam valor | 0 | 61 | 55 |
| consertadas que receberam remover | 0 | 22 | 31 |
| consertadas que receberam forma | 1 | 12 | 6 |
| consertadas que receberam aponta | 0 | 15 | 38 |
| consultas com algum retorno | 12 | 141 | 189 |
| recusas contestadas | 0 | 20 | 67 |
| mensagens do traço refeitas pelo validador | 0 | 58 | 0 |
| mensagens do traço truncadas sem reconstrução | 0 | 0 | 0 |
| acurácia: primeira → final | 83.0% → 83.1% | 83.0% → 94.4% | 74.6% → 87.8% |

## 310 consultas — desenvolvimento (dentro da amostra; não é resultado de teste)

- Conjunto: `data/dataset.json` (306 consultas); rodadas: `results/v3_310` (tc3, se3).

| Medida | TC v3 | SE v3 |
|---|---|---|
| Consultas | 306 | 306 |
| Acurácia [IC 95%] | 97.7% [95.4%–98.9%] | 94.1% [90.9%–96.2%] |
| Acurácia no domínio (fora de F e E) | 98.3% | 94.0% |
| Recusa em F: precisão / recall / F1 | 100.0% / 75.0% / 0.857 | 44.4% / 100.0% / 0.615 |
| Falsa recusa (domínio) | 0.0% | 3.4% |
| E: acurácia (buscou sem filtros / não buscou / com filtro) | — | — |
| F1 ponderado dos campos | 0.993 | 0.974 |
| Efeito: sigla em state | 0.0% (0/126) | 0.0% (0/121) |
| Efeito: prefixo no código | 0.0% (0/35) | 0.0% (0/35) |
| Efeito: limit sem pedido | 0.4% (1/277) | 0.0% (0/269) |
| Efeito: productType sem pedido | 0.0% (0/254) | 0.0% (0/246) |
| Latência mediana / p95 (s) | 1.38 / 2.66 | 0.77 / 2.67 |
| Chamadas ao modelo por consulta | 2.14 | 1.21 |
| Consultas com pergunta | 6 | — |
| Consultas com pergunta em texto | 4 | — |
| Recusas contestadas | 2 | 9 |
| Consultas com chamada escrita como texto (v3: interpretada) | 8 | — |
| Respostas fora do schema / erros de infraestrutura | 0 / 0 | 0 / 0 |

| Grupo | Par (A × B) | n | Só A | Só B | p (McNemar) | B − A, acurácia [IC] | B − A, F1 [IC] |
|---|---|---|---|---|---|---|---|
| principal | TC v3 × SE v3 | 306 | 15 | 4 | 0.01921 | -3.6 p.p. [-6.5, -1.0] | -0.018 [-0.031, -0.007] |

| Contagem | TC v3 | SE v3 |
|---|---|---|
| n (com traço) | 306 | 306 |
| sem traço | 0 | 0 |
| primeira decisão certa | 277 | 235 |
| final certa | 299 | 288 |
| consertadas | 23 | 53 |
|   dando o valor | 13 | 35 |
|   mandando remover | 4 | 6 |
|   corrigindo a forma | 3 | 1 |
|   apontando o campo | 3 | 6 |
|   recusa contestada | 0 | 5 |
|   remover ou forma (o agregado do plano) | 7 | 7 |
|   sem mensagem | 0 | 0 |
| estragadas | 1 | 0 |
|   por erro de infraestrutura (não pelo retorno) | 0 | 0 |
| execuções com erro de infraestrutura | 0 | 0 |
| consertadas que receberam valor | 13 | 35 |
| consertadas que receberam remover | 5 | 17 |
| consertadas que receberam forma | 3 | 9 |
| consertadas que receberam aponta | 3 | 9 |
| consultas com algum retorno | 25 | 58 |
| recusas contestadas | 2 | 9 |
| mensagens do traço refeitas pelo validador | 11 | 0 |
| mensagens do traço truncadas sem reconstrução | 0 | 0 |
| acurácia: primeira → final | 90.5% → 97.7% | 76.8% → 94.1% |
