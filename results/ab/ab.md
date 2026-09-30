# Teste A/B — Tool Calling (A) × Saída Estruturada (B)

Gerado por `python -m pfc_busca.evaluation.ab`, com as funções de `lote.py`, `lote2.py` e `comparacao.py` (nenhuma medida calculada à parte). Um par = o mesmo modelo, as mesmas consultas, a mesma especificação e o mesmo ambiente. † = desenvolvimento (dentro da amostra que orientou o desenho da especificação); * = rodadas com consultas diferentes (o par usa só as comuns).

| Par (macro) | Conjunto | Modelo | Espec. | Amb. | n | Acurácia TC / SE | SE − TC [IC 95%] | Só TC / Só SE | p | Domínio TC / SE | F1 recusa TC / SE | Latência med. TC / SE (s) | p95 TC / SE (s) | Chamadas TC / SE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `basee2bv1` | 310 | Gemma 4 E2B | v1 | T4 | 306 | 56,5% / 53,9% | -2,6 [-8,8 a +4,2] | 55 / 47 | 0,488 | 56,4% / 55,4% | 0,238 / 0,000 | 0,40 / 0,47 | 0,70 / 0,86 | 1,00 / 1,00 |
| `baseqwenv1` | 310 | Qwen 3 4B | v1 | T4 | 306 | 54,2% / 60,1% | +5,9 [+0,7 a +10,8] | 25 / 43 | 0,038 | 53,0% / 61,7% | 0,552 / 0,000 | 0,83 / 0,69 | 1,40 / 1,97 | 1,00 / 1,00 |
| `basee4bv1` | 310 | Gemma 4 E4B | v1 | T4 | 306 | 60,1% / 75,2% | +15,0 [+9,8 a +20,6] | 16 / 62 | < 0,001 | 59,1% / 77,2% | 0,222 / 0,000 | 0,72 / 0,76 | 1,23 / 1,60 | 1,00 / 1,00 |
| `basemistralv1` | 310 | Mistral Nemo 12B | v1 | T4 | 306 | 26,8% / 52,0% | +25,2 [+18,3 a +32,0] | 32 / 109 | < 0,001 | 24,8% / 53,4% | 0,079 / 0,000 | 2,39 / 1,00 | 5,86 / 3,39 | 1,00 / 1,00 |
| `baseestacaoe2bv1` | 310 (P e N) | Gemma 4 E2B | v1 | Estação | 59 | 47,5% / 45,8% | -1,7 [-15,3 a +11,9] | 10 / 9 | 1,000 | 45,6% / 47,4% | 0,333 / 0,000 | 0,71 / 0,76 | 1,20 / 1,55 | 1,00 / 1,00 |
| `baseestacaoqwenv1` | 310 (P e N) | Qwen 3 4B | v1 | Estação | 59 | 49,2% / 50,8% | +1,7 [-13,6 a +16,9] | 9 / 10 | 1,000 | 47,4% / 52,6% | 0,400 / 0,000 | 2,60 / 1,97 | 5,70 / 5,12 | 1,00 / 1,00 |
| `basegroqgptoss20v1` | 310 | GPT-OSS 20B | v1 | Groq | 306 | 89,2% / 77,5% | -11,8 [-16,7 a -7,2] | 50 / 14 | < 0,001 | 88,9% / 79,5% | 0,889 / 0,000 | — / — | — / — | 1,00 / 1,00 |
| `basegroqqwen38v1` | 310 | Qwen 3.8 27B | v1 | Groq | 285* | 94,7% / 94,4% | -0,4 [-2,8 a +2,1] | 6 / 5 | 1,000 | 95,1% / 95,1% | 0,667 / 0,000 | — / — | — / — | 1,00 / 1,00 |
| `basegroqgptoss120v1` | 310 | GPT-OSS 120B | v1 | Groq | 306 | 89,9% / 87,3% | -2,6 [-6,5 a +1,3] | 24 / 16 | 0,268 | 89,6% / 89,6% | 0,727 / 0,000 | — / — | — / — | 1,00 / 1,00 |
| `basee4bv2` | 310 | Gemma 4 E4B | v2† | T4 | 306 | 47,4% / 68,0% | +20,6 [+14,1 a +27,1] | 30 / 93 | < 0,001 | 46,0% / 67,1% | 1,000 / 0,271 | 0,81 / 0,71 | 1,31 / 1,47 | 1,00 / 1,00 |
| `basee4bv3` | 310 | Gemma 4 E4B | v3† | T4 | 306 | 97,7% / 94,1% | -3,6 [-6,5 a -1,0] | 15 / 4 | 0,019 | 98,3% / 94,0% | 0,857 / 0,615 | 1,38 / 0,77 | 2,66 / 2,67 | 2,14 / 1,21 |
| `lotee4bv1` | Lote 1 | Gemma 4 E4B | v1 | T4 | 1929 | 61,5% / 62,2% | +0,7 [-2,4 a +3,8] | 419 / 433 | 0,656 | 48,9% / 75,5% | 0,592 / 0,000 | 0,86 / 0,72 | 1,48 / 1,45 | 1,00 / 1,00 |
| `lotee4bv2` | Lote 1 | Gemma 4 E4B | v2 | T4 | 1929 | 62,8% / 72,4% | +9,6 [+7,4 a +11,8] | 153 / 338 | < 0,001 | 53,4% / 63,2% | 0,980 / 0,723 | 0,94 / 0,61 | 1,45 / 1,48 | 1,00 / 1,00 |
| `lote2e4bv1` | Lote 2 | Gemma 4 E4B | v1 | T4 | 945 | 58,6% / 61,3% | +2,6 [-1,6 a +6,9] | 210 / 235 | 0,255 | 45,9% / 74,8% | 0,562 / 0,000 | 0,85 / 0,72 | 1,41 / 1,44 | 1,00 / 1,00 |
| `lote2e4bv2` | Lote 2 | Gemma 4 E4B | v2 | T4 | 945 | 62,1% / 73,8% | +11,6 [+7,9 a +14,9] | 83 / 193 | < 0,001 | 53,3% / 65,4% | 0,991 / 0,738 | 0,91 / 0,61 | 1,40 / 1,47 | 1,00 / 1,00 |
| `lote2e4bv3` | Lote 2 | Gemma 4 E4B | v3 | T4 | 945 | 94,4% / 87,8% | -6,6 [-8,9 a -4,2] | 95 / 33 | < 0,001 | 94,4% / 84,4% | 0,969 / 0,901 | 1,47 / 0,78 | 4,96 / 2,55 | 2,06 / 1,23 |

Resumo (McNemar, p < 0,05): 16 pares — SE melhor em 6, TC melhor em 3, empate em 7; fora do desenvolvimento, 14 pares — SE melhor em 5, TC melhor em 2, empate em 7.

## Rodadas de cada par

| Par | Rodada TC | Rodada SE | Consultas TC / SE | Repetições TC / SE | Latência: hardware |
|---|---|---|---|---|---|
| `basee2bv1` | `results/gemma4-e2b-it-qat` | `results/se-gemma4-e2b-it-qat` | 306 / 306 | 3 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; sessões (máquinas) diferentes |
| `baseqwenv1` | `results/qwen3-4b-instruct-2507-q4_K_M` | `results/se-qwen3-4b-instruct-2507-q4_K_M` | 306 / 306 | 3 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; sessões (máquinas) diferentes |
| `basee4bv1` | `results/gemma4-e4b-it-qat` | `results/se-gemma4-e4b-it-qat` | 306 / 306 | 3 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; sessões (máquinas) diferentes |
| `basemistralv1` | `results/mistral-nemo-12b` | `results/se-mistral-nemo-12b` | 306 / 306 | 3 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; sessões (máquinas) diferentes |
| `baseestacaoe2bv1` | `results/estacao/gemma4-e2b-it-qat` | `results/estacao/se-gemma4-e2b-it-qat` | 59 / 59 | 1 / 1 | RTX 3050 Laptop, 4096 MiB; Ollama 0.34.0; 38% na GPU; mesma máquina |
| `baseestacaoqwenv1` | `results/estacao/qwen3-4b-instruct-2507-q4_K_M` | `results/estacao/se-qwen3-4b-instruct-2507-q4_K_M` | 59 / 59 | 1 / 1 | RTX 3050 Laptop, 4096 MiB; Ollama 0.34.0; 66% na GPU; mesma máquina |
| `basegroqgptoss20v1` | `results/groq-openai-gpt-oss-20b` | `results/groq-se-openai-gpt-oss-20b` | 306 / 306 | 1 / 1 | não comparável (nuvem: hardware do provedor, não controlado); medida: 0,53 / 0,46 s |
| `basegroqqwen38v1` | `results/groq-qwen-qwen3.8-27b` | `results/groq-se-qwen-qwen3.8-27b` | 306 / 285 | 1 / 1 | não comparável (nuvem: hardware do provedor, não controlado); medida: 0,70 / 0,48 s |
| `basegroqgptoss120v1` | `results/groq-openai-gpt-oss-120b` | `results/groq-se-openai-gpt-oss-120b` | 306 / 306 | 1 / 1 | não comparável (nuvem: hardware do provedor, não controlado); medida: 0,66 / 0,60 s |
| `basee4bv2` | `results/v2_310/tc2-gemma4-e4b-it-qat` | `results/v2_310/se2-gemma4-e4b-it-qat` | 306 / 306 | 1 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; mesma máquina |
| `basee4bv3` | `results/v3_310/tc3-gemma4-e4b-it-qat` | `results/v3_310/se3-gemma4-e4b-it-qat` | 306 / 306 | 1 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; mesma máquina |
| `lotee4bv1` | `results/lote/gemma4-e4b-it-qat` | `results/lote/se-gemma4-e4b-it-qat` | 1929 / 1929 | 1 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; mesma máquina |
| `lotee4bv2` | `results/lote/tc2-gemma4-e4b-it-qat` | `results/lote/se2-gemma4-e4b-it-qat` | 1929 / 1929 | 1 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; mesma máquina |
| `lote2e4bv1` | `results/lote2/gemma4-e4b-it-qat` | `results/lote2/se-gemma4-e4b-it-qat` | 945 / 945 | 1 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; mesma máquina |
| `lote2e4bv2` | `results/lote2/tc2-gemma4-e4b-it-qat` | `results/lote2/se2-gemma4-e4b-it-qat` | 945 / 945 | 1 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; mesma máquina |
| `lote2e4bv3` | `results/lote2/tc3-gemma4-e4b-it-qat` | `results/lote2/se3-gemma4-e4b-it-qat` | 945 / 945 | 1 / 1 | Tesla T4, 15360 MiB; Ollama 0.34.4; 100% na GPU; mesma máquina |

Avisos:

- basegroqqwen38v1: rodadas com consultas diferentes (TC 306, SE 285); o par usa só as 285 presentes nas duas

## Conferência com as macros já existentes

Referências: `../paper_revisado/tabelas`.

- verificações: 299 — iguais: 268; divergentes explicadas: 8; divergentes não explicadas: 0; sem macro correspondente: 23.

| Par | Medida | Macro existente | A/B | Existente | Situação e causa |
|---|---|---|---|---|---|
| `basee4bv1` | acurácia TC | `res@abordagens@e4b@acuraciatc` | 60,1% | 60,2% | explicada: a fonte pontua a média das execuções (TC com 3 repetições); a A/B, uma observação por consulta, pela maioria das repetições |
| `basee4bv1` | IC TC | `res@abordagens@e4b@ictc` | 54,6% a 65,5% | 54,7% a 65,6% | explicada: a fonte pontua a média das execuções (TC com 3 repetições); a A/B, uma observação por consulta, pela maioria das repetições |
| `basee4bv1` | domínio (sem F) TC | `res@abordagens@e4b@accsemftc` | 59,1% | 59,2% | explicada: a fonte pontua a média das execuções (TC com 3 repetições); a A/B, uma observação por consulta, pela maioria das repetições |
| `basee4bv1` | TC − SE | `res@abordagens@e4b@difpp` | -15,0 | -14,9 | explicada: a fonte pontua a média das execuções (TC com 3 repetições); a A/B, uma observação por consulta, pela maioria das repetições |
| `basee4bv1` | acurácia TC | `res@principal@e4b@acuracia` | 60,1% | 60,2% | explicada: a fonte pontua a média das execuções (TC com 3 repetições); a A/B, uma observação por consulta, pela maioria das repetições |
| `basee4bv1` | IC TC | `res@principal@e4b@ic` | 54,6% a 65,5% | 54,7% a 65,6% | explicada: a fonte pontua a média das execuções (TC com 3 repetições); a A/B, uma observação por consulta, pela maioria das repetições |
| `basegroqqwen38v1` | acurácia TC | `res@groq@qwen38@acuracia` | 94,7% | 95,1% | explicada: a fonte usa todas as consultas de cada rodada (TC 306, SE 285); a A/B, só as 285 presentes nas duas |
| `basegroqqwen38v1` | IC TC | `res@groq@qwen38@ic` | 91,5% a 96,8% | 92,1% a 97,0% | explicada: a fonte usa todas as consultas de cada rodada (TC 306, SE 285); a A/B, só as 285 presentes nas duas |

Verificações sem a macro correspondente na referência (o par ou a medida não existem nas análises existentes): `basegroqqwen38v1` 11; `lote2e4bv1` 6; `lote2e4bv2` 6.

Números da tabela sem equivalente em nenhuma macro existente (novos da A/B; os demais foram conferidos): `basee2bv1`: icdif, recusaftc, recusafse, latmedse, latp95se, chamadastc, chamadasse; `baseqwenv1`: icdif, recusaftc, recusafse, latmedse, latp95se, chamadastc, chamadasse; `basee4bv1`: chamadastc, chamadasse; `basemistralv1`: icdif, recusaftc, recusafse, latmedse, latp95se, chamadastc, chamadasse; `baseestacaoe2bv1`: icdif, recusaftc, recusafse, latmedse, latp95se, chamadastc, chamadasse; `baseestacaoqwenv1`: icdif, recusaftc, recusafse, latmedse, latp95se, chamadastc, chamadasse; `basegroqgptoss20v1`: icdif, recusaftc, recusafse, chamadastc, chamadasse; `basegroqqwen38v1`: n, accse, dif, icdif, p, domtc, domse, recusaftc, recusafse, chamadastc, chamadasse; `basegroqgptoss120v1`: icdif, recusaftc, recusafse, chamadastc, chamadasse; `basee4bv2`: chamadastc, chamadasse; `lotee4bv1`: chamadastc, chamadasse; `lotee4bv2`: chamadastc, chamadasse; `lote2e4bv1`: dif, icdif, p; `lote2e4bv2`: dif, icdif, p.

Iguais por par: `basee2bv1` 16; `baseqwenv1` 16; `basee4bv1` 29; `basemistralv1` 16; `baseestacaoe2bv1` 16; `baseestacaoqwenv1` 16; `basegroqgptoss20v1` 13; `basegroqgptoss120v1` 13; `basee4bv2` 19; `basee4bv3` 22; `lotee4bv1` 19; `lotee4bv2` 19; `lote2e4bv1` 16; `lote2e4bv2` 16; `lote2e4bv3` 22.
