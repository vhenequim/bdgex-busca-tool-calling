# Busca no acervo real do BDGEx: o lote 2 executado nos metadados do CSW

**Rótulo:** análise exploratória feita depois da entrega, sem rodar modelos; não altera nenhum resultado do texto. Gerado por `scripts/acervo_real/avaliar_acervo.py` a partir de `results/acervo_real/resultados.json`; todos os números saem do script.

## Por que esta análise

A avaliação do texto mede se a frase vira os parâmetros certos. A busca em si só tinha sido demonstrada no banco sintético (14 municípios, 117 produtos), o que esconde a ambiguidade do acervo real: folhas homônimas, sigla que casa com mais de um estado, várias edições da mesma folha. Aqui as buscas que o sistema faria no lote 2 (o gabarito e o que cada configuração emitiu) rodam no acervo real carregado num PostGIS com o esquema do protótipo, com a SQL de `tools.montar_sql` sem mudança. Nenhum modelo foi rodado.

## Método

- **Banco:** 21.229 registros do CSW do BDGEx em `datasets`, 27 UFs e 5.570 municípios das malhas do IBGE, 5 áreas de suprimento aproximadas (detalhes da carga em `carga.json`).
- **Consultas:** as 782 do lote 2 cujo correto é buscar (717 do domínio e 65 subespecificadas, em que pedir esclarecimento também vale). As 163 fora do domínio não buscam e entram no acerto do lote inteiro com a pontuação existente.
- **Gabarito:** cada leitura aceita (a preferencial e as alternativas, com as datas relativas resolvidas para 2026-09-24, como na pontuação) é expandida em buscas concretas (`$um_de`: cada valor; `$opcional`: com e sem o campo), 1.206 ao todo, 0 com erro.
- **Configurações:** as 16 rodadas do lote 2 (Gemma 4 E4B com TC v1, v2, v3d, v3a, v3 e SE v1, v2, v3; Gemma 4 E2B e Qwen 3 4B com TC e SE v1 e v3). A busca de cada execução é o `predito` do registro, a mesma que a pontuação por parâmetros avalia, e não necessariamente a última chamada registrada: no TC v1, quando a resposta trouxe duas chamadas, vale a primeira, como na pontuação (27 execuções nas três rodadas TC v1). Quando o `predito` é `{}` e o traço mostra que o validador recusou a chamada ("BUSCA NÃO EXECUTADA"), a execução conta como "não buscou", porque o sistema não buscou (Gemma 4 E4B TC v3d 2, Gemma 4 E4B TC v3a 11); o acerto não muda, porque `{}` já contava como erro.
- **Resultado igual:** o conjunto completo de cartas devolvido (sem LIMIT) é igual ao de alguma busca concreta aceita. **Acerto por resultado:** resultado igual, ou não buscar numa subespecificada.
- **Primeira página igual:** as cartas da primeira página (LIMIT de `montar_sql`, 10 por padrão) são as mesmas de alguma busca aceita. A SQL ordena só pela data, e muitas cartas têm a mesma data (em 287 das 782 buscas preferenciais o empate cruza a fronteira da página), então a página conta como igual quando existe uma ordem compatível com a SQL em que as duas coincidem. A igualdade da página como o PostgreSQL a devolveu também está em `resultados.json`.
- **Revocação e precisão:** do conjunto devolvido contra o da busca aceita mais próxima (maior Jaccard). A revocação só é definida quando a busca aceita tem cartas; a precisão, quando a devolvida tem.
- **Buscas distintas executadas:** 3.364 (com cache por SQL e argumentos). Duração total: 6,3 min.

## Resultados por configuração

O acerto por parâmetros é o do texto (repontuado aqui e conferido com `results/lote2/consolidado`). O acerto por resultado troca o critério: em vez de exigir os parâmetros do gabarito, exige o mesmo conjunto de cartas.

| Configuração | Acerto por parâmetros (945) | Acerto por resultado (945) | Acerto por resultado (782 que buscam) | Idem, só gabarito com cartas (545) | Primeira página igual | Revocação média | Precisão média |
|---|---|---|---|---|---|---|---|
| Gemma 4 E4B TC v1 | 58,6% | 64,8% | 57,4% | 50,6% (param. 47,2%) | 85,2% das que buscaram | 0,83 | 0,92 |
| Gemma 4 E4B TC v2 | 62,1% | 77,8% | 73,1% | 62,9% (param. 54,7%) | 73,6% das que buscaram | 0,73 | 0,94 |
| Gemma 4 E4B TC v3d | 75,2% | 87,3% | 84,7% | 80,0% (param. 71,4%) | 82,7% das que buscaram | 0,86 | 0,93 |
| Gemma 4 E4B TC v3a | 83,1% | 90,8% | 89,6% | 88,6% (param. 83,9%) | 91,7% das que buscaram | 0,95 | 0,95 |
| Gemma 4 E4B TC v3 | 94,4% | 97,0% | 97,4% | 96,7% (param. 94,3%) | 97,6% das que buscaram | 0,98 | 0,99 |
| Gemma 4 E4B SE v1 | 61,3% | 69,9% | 84,5% | 80,0% (param. 74,5%) | 84,4% das que buscaram | 0,84 | 0,92 |
| Gemma 4 E4B SE v2 | 73,8% | 80,7% | 76,7% | 72,5% (param. 70,5%) | 89,2% das que buscaram | 0,86 | 0,95 |
| Gemma 4 E4B SE v3 | 87,8% | 91,3% | 89,5% | 87,7% (param. 87,0%) | 93,1% das que buscaram | 0,91 | 0,96 |
| Gemma 4 E2B TC v1 | 58,1% | 76,5% | 72,9% | 64,0% (param. 54,1%) | 76,6% das que buscaram | 0,72 | 0,90 |
| Gemma 4 E2B TC v3 | 80,4% | 87,5% | 86,7% | 85,0% (param. 83,5%) | 89,9% das que buscaram | 0,89 | 0,95 |
| Gemma 4 E2B SE v1 | 36,5% | 55,9% | 67,5% | 56,5% (param. 49,9%) | 67,3% das que buscaram | 0,62 | 0,83 |
| Gemma 4 E2B SE v3 | 65,4% | 72,9% | 67,5% | 66,4% (param. 63,7%) | 75,2% das que buscaram | 0,87 | 0,77 |
| Qwen 3 4B TC v1 | 56,6% | 73,0% | 67,4% | 58,7% (param. 53,0%) | 69,6% das que buscaram | 0,70 | 0,79 |
| Qwen 3 4B TC v3 | 73,5% | 85,8% | 83,4% | 83,3% (param. 76,5%) | 86,2% das que buscaram | 0,95 | 0,91 |
| Qwen 3 4B SE v1 | 51,4% | 64,9% | 78,4% | 72,8% (param. 65,0%) | 79,8% das que buscaram | 0,80 | 0,90 |
| Qwen 3 4B SE v3 | 88,3% | 90,8% | 89,1% | 89,4% (param. 88,8%) | 94,7% das que buscaram | 0,95 | 0,96 |

Atenção ao denominador: em 237 das 782 consultas que buscam, todas as leituras do gabarito devolvem zero cartas no acervo real (seção seguinte). Nelas, qualquer busca que também devolva zero conta como resultado igual. Por isso a coluna restrita às 545 consultas cujo gabarito tem ao menos uma carta é a comparação mais justa.

### Parâmetro certo × resultado igual

| Configuração | Buscou | Certo e igual | Certo e diferente | Errado e igual (com zero cartas) | Errado e diferente | Erro de SQL | Não buscou (D / E) |
|---|---|---|---|---|---|---|---|
| Gemma 4 E4B TC v1 | 466 | 327 | 2 | 60 (44) | 77 | 0 | 254 / 62 |
| Gemma 4 E4B TC v2 | 770 | 414 | 1 | 149 (111) | 205 | 1 | 3 / 9 |
| Gemma 4 E4B TC v3d | 768 | 539 | 2 | 116 (74) | 111 | 0 | 7 / 7 |
| Gemma 4 E4B TC v3a | 739 | 608 | 1 | 74 (53) | 56 | 0 | 24 / 19 |
| Gemma 4 E4B TC v3 | 761 | 717 | 1 | 26 (17) | 17 | 0 | 2 / 19 |
| Gemma 4 E4B SE v1 | 782 | 574 | 5 | 87 (63) | 116 | 0 | 0 / 0 |
| Gemma 4 E4B SE v2 | 601 | 465 | 4 | 70 (60) | 62 | 0 | 116 / 65 |
| Gemma 4 E4B SE v3 | 685 | 602 | 4 | 37 (34) | 42 | 0 | 36 / 61 |
| Gemma 4 E2B TC v1 | 661 | 344 | 0 | 174 (130) | 143 | 0 | 69 / 52 |
| Gemma 4 E2B TC v3 | 736 | 594 | 2 | 69 (65) | 71 | 0 | 31 / 15 |
| Gemma 4 E2B SE v1 | 782 | 340 | 5 | 188 (166) | 248 | 1 | 0 / 0 |
| Gemma 4 E2B SE v3 | 637 | 408 | 0 | 71 (62) | 155 | 3 | 96 / 49 |
| Qwen 3 4B TC v1 | 708 | 331 | 2 | 157 (135) | 217 | 1 | 35 / 39 |
| Qwen 3 4B TC v3 | 709 | 508 | 1 | 117 (84) | 83 | 0 | 46 / 27 |
| Qwen 3 4B SE v1 | 782 | 483 | 3 | 130 (91) | 166 | 0 | 0 / 0 |
| Qwen 3 4B SE v3 | 673 | 610 | 3 | 27 (24) | 33 | 0 | 49 / 60 |

- **A pontuação por parâmetros não infla o acerto.** No TC v3 (E4B), 717 das 718 buscas com parâmetros certos devolvem as mesmas cartas do gabarito.
- **Erros de parâmetro com o mesmo resultado:** no TC v3 (E4B), 26 das 43 execuções que buscaram com parâmetro errado devolvem o mesmo conjunto, mas quase todos por limitação do acervo, não porque o erro seja irrelevante: 17 zeram nos dois lados; 4 trocam o campo de data (publicação por criação, ou acrescentam o outro) e só coincidem porque o CSW grava uma data só; 2 mudam só o `limit` (o conjunto é o mesmo, a página mostrada não); e 3 são de fato inofensivos (nos três, conferidos à mão, a data inicial 1900 acrescentada). Por isso não chamamos a métrica por parâmetros de conservadora.
- No SE v3 (E4B): 37 erros com o mesmo resultado, dos quais 34 com zero cartas, 1 por troca de campo de data, 1 de `limit` e 1 de fato inofensivos. Campos dos erros que mudam o resultado: keyword (24), scale (12), keyword+state (2), city+keyword (1), city+state (1), state (1), outros (1); no TC v3: keyword (11), publicationPeriod (2), city (1), scale (1), city+keyword (1), state (1).
- **Parâmetro certo, resultado diferente:** 36 execuções nas 16 configurações (1 no TC v3 E4B). Em 35 delas a keyword difere do gabarito só por acento ou caixa, e em 1 por pontuação ou caractere (o nome do catálogo tem um caractere de controle e o sinal de menos U+2212, que a normalização da pontuação apaga). A pontuação compara texto normalizado, mas a busca por palavra-chave do protótipo (full-text `portuguese` e `LIKE`) é sensível a acento. 3 delas têm letra maiúscula acentuada, que o `lower()` deste banco não converte porque ele foi criado com locale `C`; num banco com locale UTF-8 essas 3 provavelmente coincidiriam.

## Ambiguidade do acervo real (buscas do gabarito)

Leitura preferencial de cada consulta, com os campos opcionais presentes.

| Cartas devolvidas | Consultas |
|---|---|
| 0 | 252 |
| 1 | 57 |
| 2 a 10 | 115 |
| 11 a 100 | 61 |
| 101 a 1.000 | 64 |
| mais de 1.000 | 233 |

- Mediana de 6 cartas por busca; **362 das 782 buscas passam do tamanho da primeira página** (o usuário vê só as 10 mais recentes, ou o `limit` pedido).
- **Zeros:** 252 buscas preferenciais devolvem zero cartas; em 237 delas todas as leituras aceitas zeram e em 15 alguma leitura alternativa tem cartas (entre as 782 consultas, 29 têm leituras com e sem cartas). Classificação das 252 (o primeiro critério que se aplica):
  - projeto (o CSW não traz projeto): 100
  - combinação de filtros sem carta em comum: 98
  - tipo de produto ausente do acervo: 40
  - escala ausente do acervo: 8
  - um filtro sozinho já zera: creationPeriod: 3
  - um filtro sozinho já zera: publicationPeriod: 2
  - município sem polígono na malha do IBGE carregada: 1
  - nas 237 que zeram em todas as leituras: combinação de filtros sem carta em comum (94), projeto (o CSW não traz projeto) (89), tipo de produto ausente do acervo (40), escala ausente do acervo (8), um filtro sozinho já zera: creationPeriod (3), um filtro sozinho já zera: publicationPeriod (2), município sem polígono na malha do IBGE carregada (1).
  - nas buscas que zeram pela combinação, o campo cuja retirada sozinha já devolve cartas: keyword+state (19), keyword+supplyArea (15), keyword+productType (11), publicationPeriod+city (8), keyword+scale (7), keyword (7), outros (31).
  - Leitura: 100 zeram pelo mapeamento (o CSW não traz projeto); 48 pedem um tipo ou uma escala que o acervo coletado não tem (o gabarito cobre o enumerado inteiro para testar a extração); 98 combinam filtros sem carta em comum; 6 têm um filtro que sozinho já zera. No gerador do gabarito, as consultas por código (VM) e metade das consultas combinadas (VC) partem de um registro real, de onde vêm código, escala, tipo, CGEO e nome da folha; estado, município e projeto, e o CGEO ou o tipo quando o registro não os tem, são sorteados à parte. Os zeros por combinação aparecem nesses campos sorteados à parte.
- **Municípios homônimos e por substring:** o filtro `city` é `unaccent(lower(nome)) ILIKE '%valor%'`. Das 135 consultas com município, **33 casam mais de um município** (32 em mais de uma UF; até 7), por substring ou por homônimo em outra UF; em 3 delas o pedido também traz o estado, que restringe o resultado. Exemplos: "Baliza" casa 2 (Baliza/GO, São João da Baliza/RR); "Arujá" casa 3 (Arujá/SP, Guarujá/SP, Guarujá do Sul/SC); "Passagem" casa 4 (Passagem/PB, Passagem/RN, Passagem Franca/MA, Passagem Franca do Piauí/PI); "Colorado" casa 3 (Colorado/PR, Colorado/RS, Colorado do Oeste/RO); "Santa Maria" casa 17 (Santa Maria/RN, Santa Maria/RS, Santa Maria Madalena/RJ, Santa Maria da Boa Vista/PE, ...). 1 pede um município sem polígono na malha carregada.
- **Folhas homônimas:** das 111 consultas que pedem uma folha pelo nome, 18 têm 2 ou mais INOM/MI distintos com exatamente aquele nome. Separando: **12 têm folhas de mesmo nome em lugares distintos** (9 com dois INOM na mesma escala; até 3 lugares, por exemplo Terra Nova em SA-20-V-A-V-2, SB-19-Y-A-III, SF-22-Z-C-IV-3), e 6 têm só a folha e suas subdivisões com o mesmo nome (a folha-mãe e uma folha contida nela, em outra escala). 71 têm 2 ou mais registros com o nome (a mesma folha em mais de um produto). A busca só por keyword, que também casa nomes que contêm o termo, traz mais folhas que o nome exato em 15 consultas.
- **Produtos, edições e duplicatas por código:** das 130 consultas por MI ou INOM (INOM: 66, MI: 64), **95 têm 2 ou mais registros com o código** (até 5); 83 em mais de um tipo de produto, 72 com mais de uma data, 1 em mais de uma escala, e 11 com registros duplicados no próprio catálogo (mesma escala, tipo e data, UUIDs distintos; em 6 só há a duplicata). No catálogo inteiro, 890 grupos (1.781 registros) têm o mesmo INOM, tipo, escala e data. A busca só pelo código traz outros registros além dos do código em 43 consultas (o full-text casa a folha-mãe e vizinhas).
- **A primeira página mostra a edição mais recente?** Sim em 98, não em 3 (1 por ordem ascendente pedida), e em 29 o gabarito não devolve nenhum registro do código (outros filtros zeram). A ordem padrão é a data decrescente, então a mais recente vem primeiro.
- **Grafia do MI:** 500 códigos MI aparecem escritos com e sem zero à esquerda no BDGEx ("0757-4" e "757-4"). Em 3 das 64 consultas por MI há registros na outra grafia, que a busca por igualdade não devolve. (MI com menos de 4 dígitos, por si, não é ambiguidade: é a numeração normal da 1:250.000.)
- **Grafia do nome:** 281 dos 10.971 INOM do acervo têm registros com nomes que só diferem por acento ou caixa (ex.: "Vila Propício" e "Vila Propicio"). Como a busca por keyword é sensível a acento, a mesma folha aparece ou não conforme a grafia.

### Siglas no filtro de estado

O filtro de estado é `unaccent(lower(nome)) ILIKE '%valor%'`. Com a sigla no lugar do nome:

- **Simulação das 27 siglas:** só 5 devolvem o mesmo que o nome da UF; 10 não casam estado nenhum (zero cartas); 10 casam a própria UF e outras; 2 casam o estado errado e não a própria ("RN" casa Pernambuco; "SP" casa Espírito Santo).

| Sigla | Estados que casam | Cartas com a sigla | Cartas com o nome | A mais | A menos |
|---|---|---|---|---|---|
| AL | Alagoas, Distrito Federal | 173 | 87 | 86 | 0 |
| AM | Amapá, Amazonas, Pernambuco | 5.992 | 4.026 | 1.966 | 0 |
| BA | Bahia, Paraíba | 5.186 | 5.068 | 118 | 0 |
| DF | (nenhum) | 0 | 87 | 0 | 87 |
| GO | Alagoas, Goiás | 582 | 496 | 86 | 0 |
| MA | Amapá, Amazonas, Maranhão, Mato Grosso, Mato Grosso do Sul, Roraima | 7.773 | 202 | 7.571 | 0 |
| MG | (nenhum) | 0 | 1.031 | 0 | 1.031 |
| MS | (nenhum) | 0 | 754 | 0 | 754 |
| MT | (nenhum) | 0 | 1.536 | 0 | 1.536 |
| PA | Amapá, Paraná, Paraíba, Pará, São Paulo | 5.121 | 3.162 | 1.959 | 0 |
| PB | (nenhum) | 0 | 120 | 0 | 120 |
| PE | Pernambuco, Sergipe | 484 | 433 | 51 | 0 |
| PI | Espírito Santo, Piauí | 478 | 362 | 116 | 0 |
| PR | (nenhum) | 0 | 1.421 | 0 | 1.421 |
| RJ | (nenhum) | 0 | 274 | 0 | 274 |
| RN | Pernambuco | 433 | 78 | 430 | 75 |
| RO | Mato Grosso, Mato Grosso do Sul, Rio de Janeiro, Rondônia, Roraima | 2.825 | 390 | 2.435 | 0 |
| RR | (nenhum) | 0 | 677 | 0 | 677 |
| RS | (nenhum) | 0 | 2.004 | 0 | 2.004 |
| SC | (nenhum) | 0 | 713 | 0 | 713 |
| SP | Espírito Santo | 117 | 699 | 116 | 698 |
| TO | Distrito Federal, Espírito Santo, Mato Grosso, Mato Grosso do Sul, Tocantins | 2.151 | 437 | 1.714 | 0 |
| AC, AP, CE, ES, SE | só a própria | = | = | 0 | 0 |

- **Execuções reais:** 51 execuções (de todas as configurações) puseram uma sigla em `state`: Gemma 4 E4B TC v2 38, Gemma 4 E4B SE v2 13. Nenhuma das configurações v1 e v3 emitiu sigla. Em 18 delas o resultado muda em relação ao nome da UF (10.467 cartas a mais e 4.378 a menos no total; 6 perdem todas as cartas certas). Esse é o efeito que a v3 corrige no validador (sigla vira nome da UF) e que a métrica por parâmetros já contava como erro.

## Latência da SQL no acervo real

tools.buscar_catalogo na leitura preferencial (conexão nova a cada busca, contagem + primeira página), 3 rodadas seguidas depois de todas as buscas já terem rodado uma vez (cache aquecido), num notebook de uso geral; os quantis juntam as rodadas.

| Buscas | n | Mediana (ms) | p95 (ms) | Máximo (ms) |
|---|---|---|---|---|
| Todas | 2346 | 49 | 127 | 710 |
| Com filtro espacial (city, state, supplyArea) | 1071 | 67 | 154 | 710 |
| Sem filtro espacial | 1275 | 43 | 60 | 394 |
| Rodada 1 (todas) | 782 | 47 | 120 | 574 |
| Rodada 2 (todas) | 782 | 48 | 130 | 710 |
| Rodada 3 (todas) | 782 | 52 | 135 | 566 |

A medida varia entre rodadas (mediana de 47 a 52 ms e p95 de 120 a 135 ms nas 3 rodadas; uma execução anterior deste script, em outro momento, mediu 89 ms e 231 ms numa rodada só), porque a máquina é de uso geral; leia como ordem de grandeza: cerca de 0,1 s por busca. Banco sintético: não há medida comparável: nas rodadas do lote 2 a busca não foi executada (latencia_tool_ms vazio em todos os registros). Para comparação, a latência do modelo por consulta, no texto, é de segundos.

## Conferência

15 consultas (BVC0135, BVA0013, BVS0070, BVA0044, BVC0079, BVC0171, BVA0004, BVA0018, BVC0153, BVS0068, BVT0070, BVC0116, BVC0069, BVE0012, BVE0071), gabarito e Gemma 4 E4B TC v3:
- parâmetros, SQL e argumentos conferem com o registro da execução e com o gabarito resolvido em todas as 15;
- as contagens foram refeitas com SQL escrita à mão (filtro pela sigla da UF ou da área, igualdade de nome, de escala e de tipo) em 11 das 15 e deram o mesmo número em todas; as outras 4 são as 3 com project, que zeram por construção, e a subespecificada sem busca;
- a classificação 'resultado igual' está certa nas 15: 6 iguais com parâmetro certo (4 delas com zero cartas: projeto, tipo MDT ausente do acervo, nome + tipo sem registro, nome + tipo + escala + área sem registro), 3 iguais com parâmetro errado (data inicial 1900 acrescentada; UF omitida numa busca com projeto; keyword a mais numa busca com projeto, as duas com zero cartas), 5 diferentes (keyword encurtada que casa outras folhas; keyword sem acento; nome encurtado que acha outra folha; busca vazia que devolve o acervo inteiro; keyword genérica numa subespecificada) e 1 'não buscou' numa subespecificada;
- dois achados do acervo real apareceram na amostra: a mesma folha está escrita 'Vila Propício' num registro e 'Vila Propicio' no outro, e a busca por palavra-chave é sensível a acento, então a keyword sem acento devolve o outro registro; e uma folha pedida 'do 1º CGEO', que no acervo é do 2º CGEO, dá zero no gabarito, enquanto o modelo, que encurtou o nome, achou outra folha de nome parecido;

Duas conferências independentes refizeram, com SQL própria, a carga (registros sorteados contra o JSON do CSW, sem divergência), buscas do gabarito, as acurácias, a tabela cruzada, as contagens de homônimas, códigos, siglas e cortes de página, e obtiveram os mesmos números. Os ajustes de interpretação que elas apontaram (classificação dos zeros e dos erros com o mesmo resultado, homônimas aninhadas, municípios por substring, duplicatas do catálogo, grafias do MI, chamadas recusadas, áreas de suprimento e latência) estão incorporados nesta versão.

## Limitações e o que o mapeamento aproxima

- **O dump não é o catálogo inteiro.** A coleta de 28/09/2026 tem 31.190 registros, mas só 21.229 identificadores distintos: a paginação do servidor CSW repetiu páginas (9.961 cópias idênticas descartadas). O servidor declara 31.190 registros; provavelmente cerca de 9.961 registros do catálogo não foram coletados (não verificamos se o número declarado conta registros distintos). O texto entregue cita "31.190 registros"; o número de registros distintos é 21.229. As contagens de homônimas e edições são, portanto, limites inferiores.
- **Projeto:** o CSW não traz projeto (`projeto` = '' em todos). As 100 consultas com `project` devolvem zero no gabarito e em qualquer configuração; elas contam como resultado igual sempre que a configuração também usa `project` ou também zera.
- **Datas:** `data_publicacao` = `data_criacao` = `dc:date` (o CSW não distingue). Diferenças entre `publicationPeriod` e `creationPeriod`, ou entre `sortField`, não aparecem no resultado.
- **Áreas de suprimento:** não há polígonos oficiais; cada área é a união das caixas dos registros produzidos pelo CGEO. O filtro `supplyArea` passa a significar "a região onde aquele CGEO tem produtos no catálogo", que se afasta muito da área de suprimento real: o 1º CGEO cobre RS 95%, PR 94%, SC 92%, RR 39%, AM 19%; o 2º cobre AP 95%, AC 52%, AM 51%; o 4º cobre AM 31%, PA 31%, RR 43%, AC 36%. Contagens absolutas com `supplyArea` não representam a área real. 81 registros dos CGEO ficaram fora por não terem caixa válida (zerada, ausente ou em pixel); o teto de área por caixa não excluiu nenhuma. 175 das 782 consultas usam `supplyArea` em alguma leitura; para a métrica 'resultado igual' o efeito é pequeno, porque quando o gabarito e a configuração pedem a mesma área o resultado coincide de qualquer forma; a aproximação pesa quando a configuração erra a área.
- **Tipo e escala:** heurística sobre título e formato (o CSW não tem campo de tipo); 1.052 registros ficaram sem tipo e 165 sem escala, com valores que nenhum filtro casa. Ausentes do acervo coletado: os tipos SCN Carta Ortoimagem Banda P Pol HH, SCN Carta Ortoimagem Banda X Pol HH, MDT — RAM, CIRC, Cartas Temáticas Não SCN; as escalas 1:1.000, 1:5.000.
- **Municípios:** 1 município da lista do IBGE não tem polígono na malha baixada (5101837 Boa Esperança do Norte/MT); a única consulta que o pede zera por isso.
- **Locale do banco:** `C`; o `lower()` não converte maiúsculas acentuadas (afeta só keywords escritas em maiúsculas com acento, contadas acima).
- **Resultado igual com zero cartas:** quando o gabarito devolve zero, toda busca que também zera conta como igual; a coluna restrita ao gabarito com cartas corrige isso.
- **O gabarito testa a extração, não a satisfação do usuário.** Parte das combinações tem campos sorteados à parte e não corresponde a nenhum registro. O teste mede se a busca do sistema devolve as mesmas cartas que a busca do gabarito, não se o usuário achou o que queria.
- É uma análise exploratória feita depois da entrega. Não muda nenhum número do texto.
