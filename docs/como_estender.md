# Como acrescentar uma versão de Tool Calling ou de Saída Estruturada

Este é o caminho que a v3 percorreu, escrito para a próxima versão: do módulo novo ao número no
texto. Os exemplos usam uma hipotética `tool_calling_v4`, com o seu controle `saida_estruturada_v4`;
o mesmo vale para uma versão só de SE. O desenho e o teste da v3 estão em `docs/v3.md` e o registro
dos ciclos, em `docs/v3_desenvolvimento.md`; eles são o modelo a seguir.

Resumo:

| # | Passo | Onde |
|---|---|---|
| 0 | Escolher a pergunta, o controle e os conjuntos (desenvolvimento e teste) | este documento, seção 0 |
| 1 | Escrever o módulo da versão | `src/pfc_busca/v4.py` |
| 2 | Registrar a abordagem | `src/pfc_busca/abordagens.py` |
| 3 | Testes | `tests/test_v4.py`, `tests/test_abordagens.py`, `tests/test_regressao_abordagens.py` |
| 4 | Ciclos de desenvolvimento, só nos conjuntos de desenvolvimento | `scripts/v3/ciclo_dev.py` e vizinhos |
| 5 | Congelar | `v4.texto_hash`, `tests/test_regressao_abordagens.py` |
| 6 | Checar contaminação | `scripts/v3/checar_contaminacao.py` |
| 7 | Pré-registrar o plano e o código da análise | `docs/v4.md`, `src/pfc_busca/evaluation/` |
| 8 | Gerar o caderno e o pacote do Colab | `scripts/v3/gerar_notebook_lote2.py`, `scripts/empacotar_colab.py` |
| 9 | Rodar | Colab, GPU T4 |
| 10 | Conferir | `pfc conferir` |
| 11 | Analisar | um módulo no molde de `lote2.py`, `pfc ab` |
| 12 | Levar ao texto | `--paper`, `\carregarnumeros`, `\res`, `\tabelagerada` |

As regras que valem em todos os passos estão na seção "Cuidados que a tese aprendeu", no fim.

## 0. Antes de começar

- **A pergunta.** Uma versão nova testa uma hipótese sobre o mecanismo ou sobre a especificação. A v3
  perguntava o que o Tool Calling ganha quando usa o que tem de próprio: chamar funções no meio da
  resposta e receber o retorno delas.
- **O controle.** Toda versão de TC tem um controle com SE que recebe o mesmo código sem o mecanismo
  (na v3: as mesmas descrições, a mesma validação e a mesma recusa contestada, como nova tentativa).
  Sem ele, um ganho não se atribui ao Tool Calling. Se a versão acrescenta várias peças, divida-a em
  degraus que acrescentam uma de cada vez (`tool_calling_v3d` → `tool_calling_v3a` → `tool_calling_v3`).
- **Os conjuntos.** Desenvolvimento é onde se olham os erros; teste é onde se mede, uma vez. A v3 foi
  desenvolvida nas 310 consultas e no lote 1 e testada no lote 2, cujos erros foram lidos depois do
  teste. **Um conjunto de teste testa uma vez**: uma v4 desenhada depois disso não pode ser testada no
  lote 2, que passa a ser desenvolvimento. O teste dela precisa de um lote 3, construído com a mesma
  receita (`docs/lote_validacao.md` e `scripts/lote_validacao/`). Hoje, `config_lote.py` usa as
  sementes e o prefixo de identificador do lote 2 (`B`) para qualquer `PFC_LOTE` diferente de 1: antes
  de construir o lote 3, acrescente um ramo com sementes novas, prefixo próprio e os lotes 1 e 2 em
  `OUTROS_DATASETS` (deduplicação). A redação e a anotação são feitas por agentes de linguagem, com a
  instrução de não abrir nenhum outro arquivo do repositório (`docs/lote_validacao.md`, seções 5 e 7).

## 1. Escrever o módulo

Um módulo novo, `src/pfc_busca/v4.py`. **Não edite os módulos das versões avaliadas** (`agent`,
`agent_estruturado`, `v2`, `v3`, `ferramentas`, `schema`, `prompts`): os *hashes* das rodadas da tese
dependem do texto deles, e o de `v3.texto_hash` depende dos **bytes** de `v3.py` e de
`ferramentas.py`. Importe e envolva; se o validador ou uma ferramenta precisar mudar, a versão nova vai
num módulo novo (por exemplo, `ferramentas_v4.py`).

O que o módulo expõe, no molde de `v3.py`:

- as classes dos tradutores, com `traduzir(consulta: str, hoje: date) -> agent.Traducao`, e, para o
  manifesto de `pfc avaliar`, os atributos `modelo`, `base_url` e `thinking_desativado` e o método
  `descricao()`. O que for próprio da versão (tentativas, chamadas ao modelo, perguntas, avisos
  recebidos, o traço das mensagens) vai em `Traducao.extras`, que as análises leem;
- `ABORDAGENS_V4` (os nomes) e `PREFIXOS` (nome → prefixo da pasta, por exemplo `tc4-` e `se4-`);
- `criar(modelo, abordagem, base_url)`, a fábrica;
- `ferramentas_da(abordagem)`, as definições das ferramentas (o que entra em `ferramenta_sha256`);
- `texto_hash(abordagem)`: **tudo** o que define o comportamento, e só isso. Na v3: os *prompts*, as
  definições das ferramentas (JSON com `sort_keys`), os SHA-256 dos arquivos de código que
  implementam as ferramentas e o laço, os SHA-256 dos dados que elas consultam e o nome da
  abordagem. Um arquivo de dados ausente entra como `"ausente"`, e o *hash* muda: a configuração deixa
  de coincidir com a das rodadas avaliadas, e a API, que confere os arquivos listados em `dados` no
  registro, sobe em modo degradado, com aviso.

Os tradutores só consultam o Ollama no construtor (`agent.capacidades`); o resto é preguiçoso, o que
permite testá-los sem servidor.

## 2. Registrar

Em `src/pfc_busca/abordagens.py`, importe o módulo, escreva a fábrica e acrescente uma entrada por
abordagem em `_ENTRADAS`, com nome e prefixo novos:

```python
def _v4(abordagem: str, modelo: str, base_url: str) -> Any:
    return v4.criar(modelo, abordagem, base_url=base_url)

Abordagem("tool_calling_v4", "TC", "v4", v4.PREFIXOS["tool_calling_v4"],
          "o que a v4 acrescenta à v3, numa frase",
          partial(_v4, "tool_calling_v4"), partial(v4.texto_hash, "tool_calling_v4"),
          partial(v4.ferramentas_da, "tool_calling_v4"), dados=DADOS_V3),
```

- `familia` é `"TC"` ou `"SE"`; `versao`, a da especificação.
- `criar_groq` fica vazio (a versão roda só no Ollama) a menos que exista um tradutor para o Groq.
- `dados` lista os arquivos de `src/pfc_busca/dados/` de que a abordagem depende; `avisos()` e
  `estado_dos_dados()` os conferem para a API e para `pfc abordagens --hashes`. Um arquivo de dados
  novo também precisa de uma mensagem em `avisos()`.
- `RECOMENDADA` e `MODELO_RECOMENDADO` só mudam depois do teste, e só se a comparação pré-registrada
  sustentar a troca.

A partir daí, sem mais nada: `pfc abordagens` lista a entrada; `pfc avaliar --abordagem tool_calling_v4`
roda e grava em `<saída>/tc4-<modelo>/` (a saída padrão é `results/`); `pfc conferir` confere os
*hashes* dela; `PFC_ABORDAGEM=tool_calling_v4 pfc api` a põe no ar, e o `/api/health` mostra as rodadas
feitas com a mesma configuração.

## 3. Testes

- **Da versão** (`tests/test_v4.py`, no molde de `tests/test_v3.py`): as ferramentas e o validador em
  casos conhecidos, e o laço com um LLM falso que devolve respostas programadas (`_LLMFalso`), num
  tradutor montado com `object.__new__` para não chamar o Ollama. Nenhum teste pode depender do Ollama,
  do Groq, do banco ou do índice de folhas: o que precisar do índice é pulado sem ele (`pytest.skip`),
  como em `tests/test_regressao_abordagens.py`.
- **Do registro** (`tests/test_abordagens.py`): acrescente `*v4.ABORDAGENS_V4` ao conjunto de
  `test_toda_abordagem_dos_modulos_esta_no_registro` e as classes novas a `CLASSES`, que testa a
  fábrica com o Ollama simulado.
- **De regressão** (`tests/test_regressao_abordagens.py`): o teste acusa a entrada nova de propósito,
  porque a lista de nomes, prefixos e *hashes* está escrita nele. Enquanto a versão estiver em
  desenvolvimento, é esperado; ao congelar (passo 5), grave em `ESPERADO` o prefixo e os *hashes* de
  `pfc abordagens --json --hashes`, os nomes em `SO_OLLAMA` e, se o *hash* incluir o índice de folhas,
  no conjunto `V3` do teste (as abordagens cujo *hash* depende dele). A partir daí, qualquer mudança
  acidental na versão congelada, ou em algo de que ela dependa, quebra o teste.
- `pytest -q tests/` e `ruff check src tests scripts`, localmente e na integração contínua
  (`.github/workflows/testes.yml`), que também constrói a imagem da API.

## 4. Ciclos de desenvolvimento (só nos conjuntos de desenvolvimento)

Os *scripts* de `scripts/v3/` foram escritos para a v3 (Gemma 4 E4B, amostra de 160 consultas do lote 1
em `data/lote_validacao/dev_v3_ids.txt`, data de referência 2026-09-24, saída em
`results/dev_v3/ciclo<N>/`). Para outra versão, copie-os para `scripts/v4/`, com outra pasta
(`results/dev_v4/`) e, se o conjunto de desenvolvimento mudar, outra amostra fixada por semente. As
guardas que recusam o lote 2 (`erros_ciclo.py` e `validador_no_gabarito.py` conferem o caminho) passam
a recusar o lote de teste novo. O protocolo de cada ciclo:

1. **Rodar e resumir:** `python scripts/v3/ciclo_dev.py --ciclo N --rodar tool_calling_v4 saida_estruturada_v4`.
   O resumo (`resumo_ciclo.md`) põe lado a lado as referências da T4 restritas às mesmas consultas, a
   arquitetura em duas etapas simulada e toda abordagem do registro que tiver rodada na pasta do ciclo.
   O *script* chama `.venv\Scripts\pfc-avaliar.exe` (Windows); em Linux ou macOS, troque pelo
   `pfc-avaliar` da `.venv`.
2. **Listar os erros:** `python scripts/v3/erros_ciclo.py --ciclo N --config tc4- --comparar t4:se-`
   (grava `erros_tc4.md`; com `--comparar`, marca regressões e consertos contra outra configuração).
   O *script* recusa o lote 2.
3. **Decidir onde mora cada correção:** no **código** (validador, ferramentas, laço), quando a regra é
   determinística e verificável na consulta; no ***prompt***, só o uso das ferramentas. Regras escritas
   por rodadas sobre os erros do desenvolvimento são as mais expostas a sobreajuste: na v3, as
   "orientações" injetadas no *prompt* não mudaram o acerto (4 × 4 discordantes em 160) e foram
   retiradas (`experimentos/orientacoes/`).
4. **Antes do ciclo seguinte, duas checagens baratas:**
   - autoteste do validador: `python scripts/v3/validador_no_gabarito.py [--dataset data/lote_validacao.json]`.
     O validador não pode reclamar de nenhuma resposta **certa** (a leitura preferencial do gabarito);
     cada aviso nela é um falso alarme, que custaria uma rodada ao modelo ou o empurraria para o erro. A
     v3 congelada: 0 das 1.593 do lote 1 e 0 das 298 das 310;
   - reaplicação: `python scripts/v3/replay_validador.py --ciclo N --config tc4-` mostra quantas buscas
     erradas o validador novo pegaria e quantos alarmes daria nas certas (tem de ser zero). Não
     reproduz o que o modelo faria com o retorno.
5. **Medir de onde vem o acerto:** `python scripts/v3/decompor_ganho.py results/dev_v4/cicloN/tc4-gemma4-e4b-it-qat`
   separa a primeira decisão do modelo da resposta final depois do retorno (consertadas e estragadas).
6. **Registrar** o ciclo em `docs/v4_desenvolvimento.md`, como em `docs/v3_desenvolvimento.md`: a
   configuração, o resultado, os erros agrupados, a correção de cada grupo e o que foi descartado, com
   o aviso de que os números são de dentro da amostra.

Pare quando os erros restantes não tiverem correção determinística; os que ficarem são lacunas
conhecidas, que o teste vai medir.

## 5. Congelar

- A versão congelada é o que `v4.texto_hash` resume. Grave o SHA-256 de cada abordagem:
  `python -c "import hashlib; from pfc_busca import v4; print({a: hashlib.sha256(v4.texto_hash(a).encode()).hexdigest() for a in v4.ABORDAGENS_V4})"`.
- Atualize `tests/test_regressao_abordagens.py` (passo 3) e acrescente o módulo à lista de módulos
  congelados (*docstring* de `abordagens.py` e README).
- Faça o *commit*: o manifesto de cada rodada grava a revisão do código (com `+alteracoes` se `src/`
  tiver mudanças não gravadas), e o pacote do Colab grava a revisão em `VERSAO`.
- Se os dados das ferramentas entram no *hash* (na v3, `municipios_ibge.json` e `indice_folhas.json`),
  eles também ficam congelados, e o pacote precisa levá-los.

## 6. Checar contaminação

`python scripts/v3/checar_contaminacao.py` extrai os trechos entre aspas simples das descrições, das
ferramentas e dos *prompts* e os procura, normalizados, nas consultas de cada conjunto. Imprime só
contagens: nenhuma consulta do conjunto de teste aparece na tela. Para a v4, aponte-o para os textos da
v4 e para o lote de teste novo. Um exemplo que coincide com uma consulta de teste dá a resposta ao
modelo: na v2, o exemplo `'sf22yd'` da descrição de `keyword` era a consulta N35 das 310, com o seu
gabarito. Vocabulário do domínio ("100k", "mais recente") pode coincidir; consulta inteira, não.

## 7. Pré-registrar

Antes da rodada de teste, escreva e grave (*commit*) em `docs/v4.md` o plano de análise, como a seção
"Plano de análise do lote 2 (fixado antes da rodada)" de `docs/v3.md`:

- as rodadas: abordagens, conjunto, modelo, GPU, repetições, data de referência, sem SQL;
- a **comparação principal** (TC v4 × controle SE v4: acurácia por consulta, McNemar exato e diferença
  com IC 95% por *bootstrap* pareado de 2.000 reamostragens), os degraus contra o anterior e as
  comparações secundárias;
- as medidas de todas as configurações (acurácia, domínio, recusa em F, falsa recusa, E, F1 ponderado,
  efeitos de forma, latência mediana e p95, chamadas ao modelo por consulta) e a decomposição do
  acerto;
- a frase de que qualquer outra análise é exploratória e de que nada da versão muda a partir do teste
  antes de reportar o plano.

Escreva também, antes da rodada, o código da análise (no molde de `src/pfc_busca/evaluation/lote2.py`,
com as funções de `lote.py`) e teste-o só com dados de desenvolvimento (`tests/test_lote2.py`). Um
acréscimo feito depois do teste é marcado como tal no plano ("Acrescentado depois do teste", em
`docs/v3.md`).

## 8. Caderno e pacote do Colab

- Copie `scripts/v3/gerar_notebook_lote2.py` para `scripts/v4/gerar_notebook_lote3.py` e ajuste: a
  lista `RODADAS` (abordagem e conjunto, a comparação principal primeiro, depois o que as simulações
  precisam e os degraus), o modelo, o dicionário de conjuntos da célula 5 (`'lote3':
  ('data/lote_validacao_3.json', 'results/lote3', HOJE_LOTE)`) e o **pré-registro**: a célula 1 grava o
  SHA-256 da versão congelada (`V4_SHA256`, de `v4.texto_hash`), e a célula 3 recalcula-o a partir do
  pacote e se recusa a rodar se ele for outro.
- Em `scripts/empacotar_colab.py`, acrescente o caderno novo a `NOTEBOOKS`, o conjunto novo a
  `INCLUIR` e a variável do *hash* dele (`LOTE3_SHA256`) a `gravar_hash_no_notebook`, que hoje grava
  `DATASET_SHA256`, `LOTE_SHA256` e `LOTE2_SHA256`.
- `python scripts/empacotar_colab.py` grava os *hashes* nos cadernos e gera `dist/pfc_busca_colab.zip`.
  O *zip* leva `src/` como está no disco: se o *hash* da versão inclui o índice de folhas, confira que
  ele existe antes de empacotar (`pfc abordagens --hashes` avisa quando falta).

## 9. Rodar

No Colab, com GPU T4: envie o *zip* na célula 3 e "Executar tudo". A célula 3 confere os conjuntos e a
versão pré-registrada; se a sessão cair, "Executar tudo" de novo retoma cada rodada, e um *zip* parcial
é gravado ao fim de cada uma. No fim, a célula 6 roda a conferência e baixa o *zip* final, a ser
descompactado na pasta que contém `pfc_busca/`.

## 10. Conferir

`pfc conferir results/lote3/* results/v4_310/*` confere, para cada rodada, os *hashes* de *prompt* e de
ferramenta contra o código atual, a completude (cada consulta × cada repetição, sem duplicatas), as
linhas descartadas na repontuação, os erros de infraestrutura e a data de referência, e sai com código 1
se houver problema bloqueante. Confira também, nos manifestos, a GPU, a versão do Ollama e a parcela do
modelo na GPU: a latência só se compara entre rodadas em que as três coincidem
(`ab.hardware_comparavel`).

## 11. Analisar

- O módulo pré-registrado (passo 7): `python -m pfc_busca.evaluation.lote3 --paper ../paper_revisado`,
  que grava `results/lote3/consolidado/` e, com `--paper`, as macros e as tabelas.
- O teste A/B: acrescente a especificação a `ESPECS` em `src/pfc_busca/evaluation/ab.py`
  (`"v4": ("tc4", "se4", "tool_calling_v4", "saida_estruturada_v4")`) e os pares a `pares()`
  (`desenvolvimento=True` para os conjuntos de desenvolvimento, que a tabela marca com †); depois,
  `pfc ab --estrito --paper ../paper_revisado`.
- `lote2.py` aceita `--modelo` (extensão: comparação principal, ganho sobre a v1 e A/B da v1, gravados
  em `numeros_lote2<modelo>.tex`), e os pares do lote 2 com outros modelos já estão em `ab.pares()`,
  conferidos contra essas macros (`lote2.sufixo_extensao`); o módulo de análise de um lote 3 precisa do
  mesmo parâmetro.

## 12. Levar ao texto

- Cada número do texto é uma macro `\res{conjunto}{configuração}{medida}`, lida de um `numeros_*.tex`
  gerado; nenhum número de resultado é digitado à mão. Acrescente `\carregarnumeros{numeros_lote3}`
  ao `main.tex`, e cada tabela gerada entra por `\tabelagerada{nome}{descrição}`.
- Número de desenvolvimento aparece rotulado como tal (dentro da amostra), nunca como resultado.
- `python scripts/sincronizar_texto.py` copia as fontes, as tabelas e o PDF para `texto/`.

## Cuidados que a tese aprendeu

- **Efeito de menção: o que a descrição cita, o modelo tende a devolver.** Na v2, a lista de siglas das
  UFs, posta na descrição de `state` para evitar confusões como "AM" com Amapá, virou formato de saída
  (no lote 2, sigla em `state` em 46 das 125 buscas do TC v2 com estado, contra nenhuma do TC v1); a
  instrução de copiar o código "exatamente como aparece" trouxe o prefixo "MI" para a `keyword` (44 de
  49); depois de "palavras genéricas ('carta', 'folha', 'mapa') nunca são keyword", a `keyword`
  genérica apareceu; e o código de exemplo da descrição v1 ("2901-2-NE") voltou como sufixo
  acrescentado a "2901". Essas causas são hipóteses (a associação é correlacional; nenhuma frase foi
  retirada para testá-las), mas a regra prática vale: escreva regras com direção
  ("'MT' → 'Mato Grosso'"), não cite o termo que não quer ver, prefira conferir no código a proibir no
  texto, use exemplos em data fictícia e meça os efeitos de forma (`lote.efeitos_de_forma`) em toda
  rodada. No lote 2 (`results/lote2/consolidado/lote2.md`), as descrições v3 sozinhas (TC v3d) levaram
  a sigla a 0,0% e o prefixo a 2,0%, mas o limite sem pedido (6,5%) e o tipo de produto sem pedido
  (5,2%) só chegaram perto de zero com a validação (TC v3: 0,3% e 0,0%).
- **Número de desenvolvimento é de dentro da amostra.** Cada ciclo corrige erros vistos nas mesmas
  consultas em que é medido. Nas 160 consultas de desenvolvimento, a v3 congelada acertou 96,9%; no
  lote 2, 94,4%. O efeito não tem sinal garantido (a v2, desenhada sobre os erros das 310, foi pior nas
  310 do que a v1), e por isso o número de desenvolvimento não é resultado em nenhum dos dois sentidos:
  é o registro do processo.
- **O lote de teste não se lê.** Durante o desenvolvimento, nenhuma consulta, nenhum gabarito e
  nenhuma rodada do conjunto de teste é aberta; os *scripts* de desenvolvimento só leem os conjuntos de
  desenvolvimento (dois deles recusam o caminho do lote 2) e a checagem de contaminação só imprime
  contagens. Depois do teste, a leitura dos erros é exploratória e não muda a versão congelada. E o
  conjunto testa uma vez (seção 0).
- **O controle recebe o mesmo código.** A diferença entre a v3 e o controle é do mecanismo (o laço de
  chamadas e as ferramentas auxiliares, que só o Tool Calling usa); o ganho dos dois sobre a v1 é, em boa
  parte, do código que implementa o manual. Os degraus e a decomposição (primeira decisão × final) dizem
  quanto é de cada um.
- **O código codifica o manual.** O validador e as ferramentas implementam as convenções que definem o
  gabarito, e o lote 2 sorteou nomes e códigos das mesmas listas que as ferramentas consultam: o teste
  mede o modelo junto com esse código. O autoteste contra as respostas certas é obrigatório, e o alcance
  do código em consultas reais continua não medido.
- **O que o laço faz é parte do sistema medido.** Na v3, a leitura das chamadas escritas como texto e o
  pedido "Responda chamando uma ferramenta" entram no resultado e precisam ir para a produção com ela.
- **Mesmas condições.** Mesma *tag* e mesmo *digest* do modelo, mesma GPU e versão do Ollama, o modelo
  inteiro na GPU, a mesma data de referência em todas as linhas, sem SQL. A latência só se compara com
  *hardware* comparável; no Groq, o *hardware* é do provedor e fica de fora.
- **Uma pergunta por rodada.** Mudar a especificação e o mecanismo ao mesmo tempo impede atribuir o
  efeito; a comparação TC v2 × SE v2 mediu o mecanismo junto com o texto que enquadra a recusa, que
  diferia entre as duas.

## Lista de conferência

- [ ] módulo novo, sem editar os congelados; `texto_hash` cobre *prompts*, ferramentas, código e dados
- [ ] entradas no registro, com prefixos novos; `pfc abordagens --hashes` sem aviso
- [ ] testes da versão, do registro e de regressão; `pytest` e `ruff` passando
- [ ] ciclos só no desenvolvimento, registrados; autoteste do validador sem falso alarme
- [ ] versão congelada e gravada; *hashes* no teste de regressão
- [ ] contaminação checada contra o conjunto de teste
- [ ] plano de análise e código da análise gravados antes da rodada
- [ ] caderno com o pré-registro; pacote gerado com os dados de que o *hash* depende
- [ ] rodadas conferidas (`pfc conferir`), com *hardware* comparável
- [ ] análise pré-registrada, A/B e macros no texto; nada digitado à mão
