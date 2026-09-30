# Lote 2 — teste da v3 (gemma4-e2b-it-qat)

Gerado por `python -m pfc_busca.evaluation.lote2`. Plano de análise: `docs/v3.md`, seção 3 (fixado antes da rodada). Regras da decomposição: `pfc_busca/evaluation/lote2.py`.

- Conjunto: `data/lote_validacao_2.json` (945 consultas, fora as observacionais).
- Rodadas: `results/lote2` — presentes: tc1, tc3, se3, se1; ausentes: tc2, tc3d, tc3a, se2.
- Melhor configuração v1/v2 isolada (maior acurácia): —.

| Rodada | Pasta | Consultas | Cobertura | Descartadas na repontuação |
|---|---|---|---|---|
| tc1 | `results/lote2/gemma4-e2b-it-qat` | 945 | 100.0% | 0 |
| tc3 | `results/lote2/tc3-gemma4-e2b-it-qat` | 945 | 100.0% | 0 |
| se3 | `results/lote2/se3-gemma4-e2b-it-qat` | 945 | 100.0% | 0 |
| se1 | `results/lote2/se-gemma4-e2b-it-qat` | 945 | 100.0% | 0 |

Avisos:

- tc2: sem rodada em results/lote2/tc2-gemma4-e2b-it-qat (fora da análise)
- tc3d: sem rodada em results/lote2/tc3d-gemma4-e2b-it-qat (fora da análise)
- tc3a: sem rodada em results/lote2/tc3a-gemma4-e2b-it-qat (fora da análise)
- se2: sem rodada em results/lote2/se2-gemma4-e2b-it-qat (fora da análise)

## Medidas por configuração

| Medida | TC v1 | TC v3 | SE v3 | SE v1 |
|---|---|---|---|---|
| Consultas | 945 | 945 | 945 | 945 |
| Acurácia [IC 95%] | 58.1% [54.9%–61.2%] | 80.4% [77.8%–82.8%] | 65.4% [62.3%–68.4%] | 36.5% [33.5%–39.6%] |
| Acurácia no domínio (fora de F e E) | 47.8% | 79.4% | 55.4% | 44.2% |
| Recusa em F: precisão / recall / F1 | 68.9% / 93.9% / 0.795 | 82.8% / 91.4% / 0.869 | 62.6% / 98.8% / 0.767 | 0.0% / 0.0% / 0.000 |
| Falsa recusa (domínio) | 9.6% | 4.3% | 13.4% | 0.0% |
| E: acurácia (buscou sem filtros / não buscou / com filtro) | 81.5% (1 / 52 / 12) | 64.6% (27 / 15 / 23) | 92.3% (11 / 49 / 5) | 43.1% (28 / 0 / 37) |
| F1 ponderado dos campos | 0.759 | 0.920 | 0.786 | 0.683 |
| Efeito: sigla em state | 0.0% (0/99) | 0.0% (0/131) | 0.0% (0/90) | 0.0% (0/143) |
| Efeito: prefixo no código | 0.0% (0/49) | 0.0% (0/48) | 0.0% (0/48) | 0.0% (0/49) |
| Efeito: limit sem pedido | 2.2% (13/591) | 1.1% (7/622) | 0.0% (0/564) | 1.1% (7/653) |
| Efeito: productType sem pedido | 4.0% (19/473) | 0.6% (3/505) | 0.0% (0/470) | 4.0% (21/525) |
| Latência mediana / p95 (s) | 0.50 / 0.88 | 1.00 / 2.98 | 0.44 / 1.53 | 0.44 / 0.91 |
| Chamadas ao modelo por consulta | 1.00 | 2.37 | 1.62 | 1.00 |
| Consultas com pergunta | — | 167 | — | — |
| Consultas com pergunta em texto | — | 32 | — | — |
| Recusas contestadas | — | 17 | 134 | — |
| Consultas com chamada escrita como texto (v3: interpretada) | 0 (não interpretada) | 89 | — | — |
| Respostas fora do schema / erros de infraestrutura | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

## Pares (só as consultas presentes nas duas configurações)

| Grupo | Par (A × B) | n | Só A | Só B | p (McNemar) | B − A, acurácia [IC] | B − A, F1 [IC] |
|---|---|---|---|---|---|---|---|
| principal | TC v3 × SE v3 | 945 | 211 | 69 | 6.671e-18 | -15.0 p.p. [-18.3, -11.9] | -0.134 [-0.161, -0.111] |
| extensao | TC v1 × TC v3 | 945 | 57 | 268 | 7.419e-34 | +22.3 p.p. [+19.0, +25.6] | +0.161 [+0.136, +0.184] |
| extensao | TC v1 × SE v1 | 945 | 294 | 90 | 2.244e-26 | -21.6 p.p. [-25.3, -17.8] | -0.076 [-0.102, -0.052] |

## Decomposição do acerto

| Contagem | TC v3 | SE v3 |
|---|---|---|
| n (com traço) | 945 | 945 |
| sem traço | 0 | 0 |
| primeira decisão certa | 606 | 503 |
| final certa | 760 | 618 |
| consertadas | 159 | 115 |
|   dando o valor | 87 | 60 |
|   mandando remover | 27 | 5 |
|   corrigindo a forma | 12 | 9 |
|   apontando o campo | 33 | 21 |
|   recusa contestada | 0 | 20 |
|   remover ou forma (o agregado do plano) | 39 | 14 |
|   sem mensagem | 0 | 0 |
| estragadas | 5 | 0 |
|   por erro de infraestrutura (não pelo retorno) | 0 | 0 |
| execuções com erro de infraestrutura | 0 | 0 |
| consertadas que receberam valor | 87 | 69 |
| consertadas que receberam remover | 47 | 20 |
| consertadas que receberam forma | 19 | 10 |
| consertadas que receberam aponta | 48 | 32 |
| consultas com algum retorno | 283 | 388 |
| recusas contestadas | 17 | 134 |
| mensagens do traço refeitas pelo validador | 132 | 0 |
| mensagens do traço truncadas sem reconstrução | 0 | 0 |
| acurácia: primeira → final | 64.1% → 80.4% | 53.2% → 65.4% |
