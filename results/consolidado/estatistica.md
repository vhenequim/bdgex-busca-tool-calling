# Estatística

## Acurácia com IC 95% (Wilson)

| Modelo | acertos / n | acurácia | IC 95% |
|---|---|---|---|
| Qwen 3 4B | 498 / 918 | 54.2% | 48.6–59.7% |
| Gemma 4 E4B | 553 / 918 | 60.2% | 54.7–65.6% |
| Gemma 4 E2B | 519 / 918 | 56.5% | 50.9–62.0% |
| Mistral Nemo 12B | 246 / 918 | 26.8% | 22.1–32.0% |

IC com n = número de consultas (as repetições de uma consulta não são independentes).

## McNemar pareado (uma observação por consulta: maioria das repetições)

| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |
|---|---|---|---|---|
| Qwen 3 4B | Gemma 4 E4B | 45 | 63 | 0.1014 |
| Qwen 3 4B | Gemma 4 E2B | 52 | 59 | 0.5692 |
| Qwen 3 4B | Mistral Nemo 12B | 108 | 24 | 0.0000 |
| Gemma 4 E4B | Gemma 4 E2B | 53 | 42 | 0.3049 |
| Gemma 4 E4B | Mistral Nemo 12B | 125 | 23 | 0.0000 |
| Gemma 4 E2B | Mistral Nemo 12B | 118 | 27 | 0.0000 |

Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as mesmas consultas, dificilmente é obra do acaso. Cada consulta entra uma vez, com o resultado da maioria das suas repetições.
