# Estatística

## Acurácia com IC 95% (Wilson)

| Modelo | acertos / n | acurácia | IC 95% |
|---|---|---|---|
| Qwen 3 4B | 29 / 59 | 49.2% | 36.8–61.6% |
| Gemma 4 E2B | 28 / 59 | 47.5% | 35.3–60.0% |

IC com n = número de consultas (as repetições de uma consulta não são independentes).

## McNemar pareado (uma observação por consulta: maioria das repetições)

| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |
|---|---|---|---|---|
| Qwen 3 4B | Gemma 4 E2B | 8 | 7 | 1.0000 |

Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as mesmas consultas, dificilmente é obra do acaso. Cada consulta entra uma vez, com o resultado da maioria das suas repetições.
