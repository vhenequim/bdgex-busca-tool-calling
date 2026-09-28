# Manual de anotação do *dataset* de avaliação

Este manual define como o gabarito (*ground truth*) de cada consulta é construído.
Ele é a referência para: (i) a redação e a revisão das consultas; (ii) a auditoria
automática (`pfc-auditar`); (iii) a anotação independente usada para verificar o
gabarito; (iv) a adjudicação das divergências. Qualquer anotação que contrarie este
manual é um erro do gabarito, não do modelo.

## 1. Princípios

**P1 — Evidência explícita.** O gabarito contém somente parâmetros para os quais existe
um trecho da consulta que os justifica. Não se infere nada que o texto não diga
(ex.: "cartas de Manaus" não implica `state = "Amazonas"`).

**P2 — Forma canônica.** Todo valor é escrito na forma canônica da ferramenta
`buscar_catalogo`: enumerados exatamente como no *schema*; nomes de estados e
municípios por extenso, com acentos; datas em ISO 8601 (AAAA-MM-DD).

**P3 — Leituras múltiplas explícitas.** Quando a consulta admite mais de uma leitura
razoável e nem a consulta nem a descrição da ferramenta desempatam, o gabarito lista
**todas** as leituras aceitas. A primeira é a leitura preferencial; as demais são
alternativas. Uma resposta é correta se coincidir com qualquer leitura aceita.
Três mecanismos:

- **valor alternativo** — o campo é obrigatório, mas aceita mais de um valor
  (ex.: `sortField ∈ {publicationDate, creationDate}`);
- **campo opcional** — o campo pode ser omitido; se aparecer, precisa ter o valor
  indicado (ex.: `limit = 1 (opcional)`);
- **leitura estrutural alternativa** — o mesmo trecho pode ir para campos diferentes
  (ex.: "São Paulo" como `state` ou como `city`).

**P4 — Fora do domínio.** Consultas sem intenção de busca no acervo cartográfico
brasileiro têm gabarito "não chamar a ferramenta".

**P5 — Consistência.** A mesma expressão recebe a mesma anotação em todo o *dataset*.
A auditoria automática verifica isso.

**P6 — Casos observacionais.** Consultas cujo comportamento correto não é determinável
a partir do texto (valor impossível de representar, comportamento esperado discutível)
são executadas e reportadas, mas ficam fora das métricas principais. Consultas fora do
domínio (P4) **não** são observacionais: o comportamento correto é determinado.

## 2. Regras por campo

### `keyword`
- Código MI com seus sufixos (`2965-2-NE`), sem o prefixo "MI"/"folha"/"carta".
- Código INOM na grafia com hífens (`SF-22-Y-D-II-4`); grafias compactadas na consulta
  ("sf22yd") são normalizadas para a forma com hífens.
- Nome próprio de carta quando precedido de "carta"/"folha" e não for apenas o nome
  de um município ou estado já coberto por outro campo (`Passo da Seringueira`).
  Se o nome da carta coincide com um município ("folha Porto Velho"), aceita-se
  também a leitura estrutural `city`.
- Dois códigos na mesma consulta ("MI 530 ou SF-22"): o *schema* só comporta um;
  aceita-se qualquer um dos dois (o primeiro é o preferencial).

### `scale`
- Explícita em qualquer grafia: "1:25.000", "1:25000", "25k", "25 mil".
- Convenções que a própria descrição da ferramenta informa ao modelo:
  "detalhada" → `1:25.000`; "pequena escala" → `1:250.000`.
- Expressões qualitativas não informadas na ferramenta aceitam o conjunto de escalas
  que as satisfazem:
  "grande escala" → {1:25.000, 1:10.000, 1:5.000, 1:2.000, 1:1.000};
  "média escala" → {1:50.000, 1:100.000};
  "maior que 100k" → {1:50.000, 1:25.000, 1:10.000, 1:5.000, 1:2.000, 1:1.000}.
- Duas escalas explícitas ("25k ou 50k"): aceita-se qualquer uma.

### `productType`
- Sinônimos informados na ferramenta: "topo"/"topográfica(s)" → `SCN Carta Topográfica
  Matricial`; "orto"/"ortoimg"/"ortoimagem(ns)" → `SCN Carta Ortoimagem`;
  "mdt"/"modelo digital de terreno" → `MDT — RAM`.
- Demais tipos pelo nome ("vetorial", "banda P HH", "MDS", "CIRC", "temática").
- "cartas", "mapas", "produtos", "folhas" sozinhos **não** definem tipo.

### `state` e `city`
- Estados: nome por extenso, com acentos; siglas ("RS", "rj") e grafias sem acento
  ("goias") são normalizadas.
- Municípios: nome por extenso, com acentos.
- "Rio de Janeiro", "São Paulo" e "rio" sem qualificador ("estado", "cidade",
  "município") são ambíguos entre estado e capital: leituras estruturais `state` e `city`.
  Siglas ("RJ", "SP") são sempre estado.
- Regiões ("sul", "sudeste", "Nordeste", "Amazônia Legal") **não** são estados: o
  *schema* não tem campo de região, e nada é anotado para elas.

### `supplyArea`
- Qualquer menção ao Centro de Geoinformação: "1º CGEO", "1o cgeo", "1 CGEO",
  "primeiro cgeo", "dois cgeo" → `N° Centro de Geoinformação`.
- "produzido pelo 3º CGEO" anota `supplyArea` (não é data).

### `project`
- Pelo nome ou pelos apelidos informados na ferramenta ("olimpiadas", "rio 2016" →
  `Olimpíadas Rio 2016`; "beca" → `NGA-BECA`), com ou sem acento.
- Menção explícita a um projeto por um termo que o identifica sem ambiguidade no
  enumerado também é nome: "projeto rondonia" e "BCD de Rondônia" (sigla de Base
  Cartográfica Digital) → `Base Cartográfica Digital de Rondônia`.
- Expressão que designa o projeto só pelo termo distintivo do nome, sem a palavra
  "projeto", sem sigla do nome e sem apelido informado ("cartografia sistemática" para
  `Mapeamento Sistemático`) → `project` **opcional**: a consulta sustenta a leitura, mas
  a ferramenta não a informa.

### `publicationPeriod` e `creationPeriod`
- **Qual campo.** Verbo de publicação ("publicad-", "lançad-") → `publicationPeriod`.
  Verbo de criação ("criad-", "feit-", "elaborad-", "produzid-") → `creationPeriod`.
  Sem verbo que desempate ("cartas do ano passado", "produtos de hoje",
  "atualizações deste mês") → leitura preferencial `publicationPeriod`, leitura
  estrutural alternativa `creationPeriod`, com o mesmo intervalo.
- **Qual intervalo.** Resolvido com a data de referência da execução (a mesma data
  informada ao modelo no *prompt* de sistema). Ano ou intervalo absoluto
  ("em 2024", "entre 2022 e 2023") tem leitura única. Expressões relativas aceitam as
  leituras da tabela abaixo (a primeira é a preferencial; D = data de referência):

| Expressão | Leituras aceitas |
|---|---|
| esse ano / este ano / deste ano | ano inteiro; 1º de janeiro até D |
| ano passado | ano anterior inteiro |
| 2 anos atrás | o ano de dois anos antes, inteiro; D−2 anos até D |
| mês passado | mês anterior inteiro |
| este mês / deste mês / neste mês | dia 1 até D; mês inteiro |
| semana passada | D−7 até D−1; D−7 até D; semana-calendário anterior (seg–dom) |
| esta semana / nesta semana | segunda-feira até D; segunda a domingo |
| hoje | D até D |
| últimos 3 meses | D−90 dias até D; mesmo dia 3 meses antes até D |
| últimos 6 meses | D−180 dias até D; mesmo dia 6 meses antes até D |
| últimos 5 anos | D−5 anos até D; 1º de janeiro de (ano−5) até D |
| desde AAAA | AAAA-01-01 até D; AAAA-01-01 sem limite final |
| depois de AAAA | início em AAAA-01-01 ou (AAAA+1)-01-01; fim D ou sem limite final |
| antes de AAAA | sem limite inicial até (AAAA−1)-12-31 |
| primeiro trimestre (deste ano) | janeiro a março do ano de D |
| segundo semestre do ano passado | julho a dezembro do ano anterior |
| último trimestre do ano passado | outubro a dezembro do ano anterior |
| trimestre passado | trimestre-calendário anterior ao de D |

### `sortField`, `sortDirection`, `limit`
- **Direção.** "mais recente(s)", "último(s)/última(s)", "da mais nova para a mais
  antiga" → `DESC`; "mais antiga(s)", "primeiro(s)/primeira(s)", "ordem cronológica" → `ASC`.
- **Campo de ordenação.** Pista de criação ligada à ordenação ("primeiro mapeamento
  feito", "última atualização", "criadas mais recentemente", "produzida") →
  `creationDate`. Pista de publicação ligada à ordenação ("últimas publicações",
  "última carta publicada", "ordem cronológica de publicação") → `publicationDate`.
  Sem pista ("as mais recentes", "as 3 mais antigas") → valor alternativo
  {publicationDate, creationDate}; a preferencial é `publicationDate`, exceto nos
  casos herdados do protótipo, em que se mantém a anotação original como preferencial.
- **Limite.** Número explícito ("3 cartas", "as 10 primeiras", "três produtos") →
  `limit` com esse número. Singular sem número ("a carta mais recente", "a última
  atualização") → `limit = 1` opcional. Plural sem número → sem `limit`.
- Ordenação só é anotada quando a consulta pede ordem ou posição; nunca por padrão.

## 3. Consultas fora do domínio

Não chamar a ferramenta quando a consulta: trata de outro assunto (clima, preço,
ficção); pede território fora do Brasil ou fora da Terra; não tem intenção de busca
("me ajuda", "quero um mapa bonito"). Essas consultas formam a categoria **F** e entram
nas métricas principais: a resposta é correta quando a ferramenta não é chamada.

Consultas com valor impossível de representar ("escala 1:10.000.000", "estado 42") ou
cujo comportamento esperado é discutível ("cartas do futuro", "cartas topo no oceano
atlântico") são observacionais (P6).

## 4. Rastreabilidade

Cada caso registra a origem:
- **P** — `prototipo_busca_llm-main/backend/evaluation/test-cases.ts`, com a linha da
  consulta; o gabarito original da equipe do 1º CGEO é mantido como leitura
  preferencial, e as leituras alternativas acrescentadas seguem este manual.
- **N** — redigido pelos autores; a justificativa de cada leitura alternativa fica no
  campo `notas`.
- **G** — gerado por `generate_dataset.py` (semente 42): função geradora, modelo de
  frase e parâmetros sorteados; o gabarito é conhecido por construção.

## 5. Procedimento de auditoria

1. **Checagens automáticas** (`pfc-auditar`): consultas duplicadas ou contraditórias;
   validade de enumerados e campos; resolução de todas as expressões de tempo em datas
   diversas; e um anotador baseado em regras, independente do gabarito, que localiza na
   consulta o trecho que justifica cada campo e aponta (a) campo anotado sem evidência,
   (b) evidência sem campo anotado, (c) valor divergente.
2. **Anotação independente às cegas**: cada consulta é anotada novamente, sem acesso ao
   gabarito, a partir apenas deste manual e da definição da ferramenta; toda divergência
   com o gabarito é listada. A concordância é medida em rigor crescente: decisão
   (chamar / não chamar / observacional, com kappa de Cohen); leituras compatíveis nos
   dois sentidos; leitura preferencial idêntica; presença e valor de cada campo; e
   detecção de ambiguidade (a consulta admite mais de uma leitura? kappa de Cohen).
3. **Adjudicação** (`data/auditoria/adjudicacao.json`): cada consulta com divergência em
   qualquer das medidas recebe uma decisão registrada — gabarito mantido, corrigido ou
   ampliado com leitura alternativa — com justificativa por referência a este manual.
   O gabarito anterior à decisão fica registrado, e a concordância anterior à
   adjudicação é recalculada a partir dele.
4. O processo se repete até não restar divergência sem decisão.
5. **Revisão humana de amostra**: uma amostra estratificada por origem (40 consultas,
   semente 42; `data/auditoria/revisao_humana_amostra.csv`) é conferida por uma pessoa,
   que marca se concorda com as leituras aceitas.

## 6. Extensões para o lote de validação (setembro de 2026)

O lote de validação (`docs/lote_validacao.md`) cobre situações que as 310 consultas não
tinham. As regras abaixo **estendem** o manual sem alterar nenhuma anotação das 310: cada
uma generaliza uma regra existente ou cobre um caso que antes não ocorria.

**6.1 Categoria E — consulta subespecificada.** A consulta pede produtos do acervo
(intenção de busca explícita) mas não traz nenhum critério representável no *schema*:
"quero ver as cartas do acervo", "vocês têm mapas?", "cartas do Nordeste" (região não é
campo, seção 2), "mapas para uma trilha" (finalidade não é campo). O gabarito não tem
parâmetros e aceita **duas respostas**: buscar sem filtros (chamada sem parâmetros) ou não
buscar (pedir esclarecimento ou recusar). No *dataset* isso é o campo
`aceita_nao_chamar = true`. Uma chamada com qualquer parâmetro é erro (falso positivo).

- Diferença para F: F não tem intenção de busca no acervo — outro assunto, território fora
  do Brasil, pedido de produção, conversa. "Me ajuda" e "quero um mapa bonito" continuam F.
- Diferença para S: um único critério ("ortoimagens", "cartas 1:50.000", "cartas de
  Manaus") é consulta simples e exige a busca (instrução 1 do *prompt*: "um único parâmetro
  basta"), como nas 310.

**6.2 Tempo relativo parametrizado.** A tabela da seção 2 vale para qualquer quantidade e
qualquer ano (D = data de referência):

| Expressão | Leituras aceitas |
|---|---|
| últimos N meses | D − 30·N dias até D; mesmo dia N meses antes até D |
| últimos N anos | D − N anos até D; 1º de janeiro de (ano − N) até D |
| últimos N dias | D − N dias até D; D − (N − 1) dias até D |
| desde AAAA / a partir de AAAA | AAAA-01-01 até D; AAAA-01-01 sem limite final |
| depois de AAAA / após AAAA | início em AAAA-01-01 ou (AAAA+1)-01-01; fim D ou sem limite final |
| antes de AAAA / anteriores a AAAA | sem limite inicial até (AAAA−1)-12-31 |
| em AAAA / de AAAA / no ano de AAAA | AAAA-01-01 a AAAA-12-31 (leitura única) |
| entre AAAA e BBBB / de AAAA a BBBB | AAAA-01-01 a BBBB-12-31 (leitura única) |

**6.3 Municípios e UF.** Qualquer município da lista oficial do IBGE é `city`. A sigla da UF
junto ao município ("Campinas, SP", "Campinas (SP)") anota também `state` (sigla é sempre
estado, seção 2). O lote não usa municípios homônimos de UF (ex.: Goiás, Amapá, Paraná,
Tocantins), cuja ambiguidade o manual não prevê.

**6.4 Nomes de folha reais.** Nomes de folha do BDGEx precedidos de "carta"/"folha" são
`keyword` (seção 2); quando coincidem com o nome de um município da lista do IBGE, vale a
leitura estrutural `city` já prevista.

**6.5 Armadilhas de vocabulário.** "Carta", "mapa", "folha", "escala" e "projeto" em outro
sentido — "carta de vinhos", "carta de apresentação", "mapa astral", "mapa mental",
"folha de pagamento", "escala de plantão", "escala Richter", "projeto de lei" — não pedem
produto cartográfico: categoria F.

**6.6 Anotação às cegas do lote.** A data de referência é 2026-09-24, a mesma das 310.
Cada consulta é anotada sem acesso ao alvo que a originou; as consultas chegam ao anotador
embaralhadas e com identificadores neutros (a família não aparece).
