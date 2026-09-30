# Lote 2 — teste da v3 (Gemma 4 E4B)

Gerado por `python -m pfc_busca.evaluation.lote2`. Plano de análise: `docs/v3.md`, seção 3 (fixado antes da rodada). Regras da decomposição: `pfc_busca/evaluation/lote2.py`.

- Conjunto: `data/lote_validacao_2.json` (945 consultas, fora as observacionais).
- Rodadas: `results/lote2` — presentes: tc1, tc3, se3, se1; ausentes: tc2, tc3d, tc3a, se2.
- Melhor configuração v1/v2 isolada (maior acurácia): —.

| Rodada | Pasta | Consultas | Cobertura | Descartadas na repontuação |
|---|---|---|---|---|
| tc1 | `results/lote2/qwen3-4b-instruct-2507-q4_K_M` | 945 | 100.0% | 0 |
| tc3 | `results/lote2/tc3-qwen3-4b-instruct-2507-q4_K_M` | 945 | 100.0% | 0 |
| se3 | `results/lote2/se3-qwen3-4b-instruct-2507-q4_K_M` | 945 | 100.0% | 0 |
| se1 | `results/lote2/se-qwen3-4b-instruct-2507-q4_K_M` | 945 | 100.0% | 0 |

Avisos:

- tc2: sem rodada em results/lote2/tc2-qwen3-4b-instruct-2507-q4_K_M (fora da análise)
- tc3d: sem rodada em results/lote2/tc3d-qwen3-4b-instruct-2507-q4_K_M (fora da análise)
- tc3a: sem rodada em results/lote2/tc3a-qwen3-4b-instruct-2507-q4_K_M (fora da análise)
- se2: sem rodada em results/lote2/se2-qwen3-4b-instruct-2507-q4_K_M (fora da análise)

## Medidas por configuração

| Medida | TC v1 | TC v3 | SE v3 | SE v1 |
|---|---|---|---|---|
| Consultas | 945 | 945 | 945 | 945 |
| Acurácia [IC 95%] | 56.6% [53.4%–59.7%] | 73.5% [70.6%–76.3%] | 88.3% [86.0%–90.2%] | 51.4% [48.2%–54.6%] |
| Acurácia no domínio (fora de F e E) | 46.4% | 67.2% | 84.8% | 62.5% |
| Recusa em F: precisão / recall / F1 | 82.3% / 100.0% / 0.903 | 77.6% / 97.5% / 0.864 | 76.7% / 98.8% / 0.863 | 0.0% / 0.0% / 0.000 |
| Falsa recusa (domínio) | 4.9% | 6.4% | 6.8% | 0.0% |
| E: acurácia (buscou sem filtros / não buscou / com filtro) | 60.0% (0 / 39 / 26) | 83.1% (27 / 27 / 11) | 100.0% (5 / 60 / 0) | 58.5% (38 / 0 / 27) |
| F1 ponderado dos campos | 0.664 | 0.789 | 0.941 | 0.828 |
| Efeito: sigla em state | 0.0% (0/166) | 0.0% (0/115) | 0.0% (0/125) | 0.0% (0/156) |
| Efeito: prefixo no código | 6.1% (3/49) | 0.0% (0/49) | 0.0% (0/49) | 6.1% (3/49) |
| Efeito: limit sem pedido | 13.1% (81/619) | 5.1% (31/608) | 0.3% (2/604) | 0.8% (5/653) |
| Efeito: productType sem pedido | 17.7% (91/514) | 0.0% (0/499) | 0.0% (0/490) | 12.8% (67/525) |
| Latência mediana / p95 (s) | 1.05 / 2.22 | 3.15 / 11.63 | 0.65 / 2.51 | 0.89 / 1.53 |
| Chamadas ao modelo por consulta | 1.00 | 2.86 | 1.33 | 1.00 |
| Consultas com pergunta | — | 257 | — | — |
| Consultas com pergunta em texto | — | 87 | — | — |
| Recusas contestadas | — | 44 | 67 | — |
| Consultas com chamada escrita como texto (v3: interpretada) | 0 (não interpretada) | 88 | — | — |
| Respostas fora do schema / erros de infraestrutura | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

## Pares (só as consultas presentes nas duas configurações)

| Grupo | Par (A × B) | n | Só A | Só B | p (McNemar) | B − A, acurácia [IC] | B − A, F1 [IC] |
|---|---|---|---|---|---|---|---|
| principal | TC v3 × SE v3 | 945 | 46 | 185 | 6.066e-21 | +14.7 p.p. [+11.7, +18.0] | +0.153 [+0.129, +0.176] |
| extensao | TC v1 × TC v3 | 945 | 75 | 235 | 2.295e-20 | +16.9 p.p. [+13.5, +20.5] | +0.125 [+0.096, +0.156] |
| extensao | TC v1 × SE v1 | 945 | 216 | 167 | 0.01407 | -5.2 p.p. [-9.4, -1.3] | +0.164 [+0.138, +0.189] |

## Decomposição do acerto

| Contagem | TC v3 | SE v3 |
|---|---|---|
| n (com traço) | 945 | 945 |
| sem traço | 0 | 0 |
| primeira decisão certa | 580 | 645 |
| final certa | 695 | 834 |
| consertadas | 116 | 190 |
|   dando o valor | 33 | 104 |
|   mandando remover | 33 | 46 |
|   corrigindo a forma | 0 | 0 |
|   apontando o campo | 31 | 28 |
|   recusa contestada | 19 | 12 |
|   remover ou forma (o agregado do plano) | 33 | 46 |
|   sem mensagem | 0 | 0 |
| estragadas | 1 | 1 |
|   por erro de infraestrutura (não pelo retorno) | 0 | 0 |
| execuções com erro de infraestrutura | 0 | 0 |
| consertadas que receberam valor | 34 | 108 |
| consertadas que receberam remover | 38 | 58 |
| consertadas que receberam forma | 0 | 2 |
| consertadas que receberam aponta | 56 | 48 |
| consultas com algum retorno | 327 | 276 |
| recusas contestadas | 44 | 67 |
| mensagens do traço refeitas pelo validador | 357 | 0 |
| mensagens do traço truncadas sem reconstrução | 0 | 0 |
| acurácia: primeira → final | 61.4% → 73.5% | 68.3% → 88.3% |
