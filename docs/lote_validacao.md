# Lote de validação independente — metodologia

Este documento descreve como foi construído, verificado e usado o **lote de validação**:
um segundo conjunto de consultas, independente das 310 do Cap. 3, usado para (i) repetir a
comparação *Tool Calling* × Saída Estruturada numa amostra grande e nova, (ii) medir a recusa
com um número de consultas fora do domínio suficiente para intervalos de confiança estreitos,
(iii) introduzir consultas subespecificadas (categoria E) e consultas com mais de uma resposta
aceita, e (iv) testar fora da amostra a especificação v2 (`src/pfc_busca/v2.py`), desenhada a
partir dos erros observados nas 310.

A construção das consultas é parte do método: cada etapa abaixo tem script, semente e
arquivo de saída versionados, e pode ser refeita com os comandos da seção 11.

## 1. Por que um segundo conjunto

As 310 consultas deixaram três perguntas em aberto:

1. **O resultado depende do conjunto?** A camada G das 310 é gerada por modelos de frase
   (Apêndice A); a categoria F tem só 8 consultas, o que torna a "recusa F" de cada modelo uma
   proporção sobre 8 casos.
2. **O gabarito é bom?** Nas 310 o gabarito foi verificado por auditoria automática,
   anotação independente às cegas e adjudicação (Cap. 3); ainda assim, um conjunto em que o
   gabarito nasce **antes** da consulta (por construção) e é **confirmado** por um anotador
   que não o conhece dá uma segunda linha de evidência.
3. **O *Tool Calling* estava mal especificado?** Na análise de erros do Gemma 4 E4B nas 310
   (seção 9.2), os dois erros mais frequentes, não buscar numa consulta do domínio e acrescentar
   o tipo de produto a "cartas", contrariam instruções que o *prompt* v1 já dava ("Um único
   parâmetro basta"; "não complete campos por suposição"). Outros vêm de convenções do manual
   de anotação que a definição da ferramenta não informava ao modelo, ou de exemplos que ela
   trazia. A v2 reforça essas instruções e explicita as convenções; para medir o efeito fora da
   amostra que orientou o desenho, é preciso um conjunto que o desenho da v2 não viu.

## 2. Visão geral

| Etapa | Script | Saída |
|---|---|---|
| 1. Coleta dos catálogos reais | `scripts/lote_validacao/coletar_bdgex.py`, `catalogo.py` | `data/lote_validacao/bdgex_resumo.json`, `ibge_municipios.json` |
| 2. Sorteio dos alvos (gabarito por construção) | `scripts/lote_validacao/gerar_alvos.py` (semente 2026) | `data/lote_validacao/alvos.json` |
| 3. Redação controlada | `scripts/lote_validacao/redacao.py` (15 redatores) | `data/lote_validacao/consultas_redigidas.json` |
| 4. Anotação às cegas (A: todas; B: 20%) | `scripts/lote_validacao/anotacao.py` (18 anotadores) | `data/lote_validacao/anotacao/anotacao_{A,B}.json` |
| 5. Checagens, deduplicação e filtro de concordância | `scripts/lote_validacao/montar_lote.py` | `data/lote_validacao.json`, `relatorio.md`, `descartes.json` |
| 6. Avaliação (Gemma 4 E4B, T4, 4 configurações) | `notebooks/lote_validacao_colab.ipynb` | `results/lote/`, `results/v2_310/` |
| 7. Análise | `python -m pfc_busca.evaluation.lote` | `results/lote/consolidado/` e tabelas do texto |

## 3. Fontes reais

**BDGEx.** Os metadados públicos do catálogo foram coletados em 28/09/2026 pelo serviço
CSW do BDGEx (`https://bdgex.eb.mil.br/csw`, OGC CSW 2.0.2, saída JSON): **31.190
registros**. O serviço é público (o *GetCapabilities* não declara taxas nem restrições de
acesso; a política do BDGEx permite pesquisar e visualizar metadados sem cadastro). Só
metadados foram lidos; nenhum produto foi baixado. A cópia bruta não é versionada (fica em
`data/lote_validacao/bdgex_csw/`, ignorada pelo git); o repositório guarda o script de coleta,
o hash SHA-256 de cada página e as distribuições agregadas (`bdgex_resumo.json`).

De cada registro, `catalogo.py` extrai do título e dos campos Dublin Core: nome da folha,
código MI, código INOM, escala, tipo de produto, CGEO produtor e ano. O tipo de produto é
inferido por heurística (título "Modelo Digital de Superfície…" → MDS; "Mosaico
Ortorretificado"/"Ortoimagem" → ortoimagem; "Vetorial" ou formato *shapefile* → vetorial;
formatos raster → matricial). Distribuições no catálogo público:

| Escala | Registros | | Tipo (heurística) | Registros | | CGEO | Registros |
|---|---|---|---|---|---|---|---|
| 1:25.000 | 12.598 | | Topográfica matricial | 15.538 | | 3º | 7.578 |
| 1:50.000 | 12.569 | | Topográfica vetorial | 9.784 | | 2º | 7.427 |
| 1:100.000 | 4.565 | | Ortoimagem | 2.164 | | 1º | 6.366 |
| 1:250.000 | 1.046 | | MDS | 2.127 | | 5º | 2.583 |
| outras | 412 | | não identificado | 1.577 | | 4º | 1.857 |

Nomes de folha distintos: 7.838; registros com MI: 30.732; com INOM: 30.432.

**IBGE.** Lista oficial de municípios da API de localidades do IBGE (5.571 municípios, com a
UF), usada para sortear municípios reais e para saber quando o nome de uma folha coincide com
o de um município (manual, seções 2 e 6.4).

**O que é real e o que é sintético.** São reais os **valores**: nomes de folha, códigos MI e
INOM, escalas, CGEOs, anos e municípios. Nas consultas compostas, metade das combinações de
escala, tipo, CGEO e folha é tirada de um único registro do catálogo (a mesma carta), de modo
que essa parte da combinação existe no acervo; o **lugar** (estado ou município) é sorteado à
parte, e por isso parte das consultas combina um código ou uma folha com uma UF que não a
contém (os anotadores apontaram casos como um INOM do Sul pedido "do Ceará"). O gabarito anota
o que o texto diz (P1), que é o que a camada de tradução deve fazer; se a busca devolveria
algo é uma questão de nível de produto, fora do escopo (seção 10). É sintético o **texto**: a
consulta é redigida por um modelo de linguagem a partir do alvo (seção 5). Não há registro de
consultas reais de usuários do BDGEx disponível; esta é a principal limitação do lote.

## 4. Alvos: o gabarito antes da consulta

Um **alvo** especifica, antes de a consulta existir: o gabarito (`esperado`, `trocas`,
`espera_tool_call`, `aceita_nao_chamar`), o que a consulta precisa dizer (`pedido`, com a
forma de superfície de cada valor), o que ela não pode dizer (`proibido`), o registro de
linguagem e a persona de quem escreve. O gabarito segue o manual de anotação
(`docs/manual_de_anotacao.md`, seções 1 a 6), com as leituras múltiplas do princípio P3:

- valor alternativo (`$um_de`): "grande escala", "média escala", duas escalas, dois códigos,
  ordenação sem pista de campo;
- campo opcional (`$opcional`): singular sem número (`limit = 1`), "cartografia sistemática";
- leitura estrutural (`trocas`): São Paulo/Rio de Janeiro sem qualificador (estado ou cidade),
  folha homônima de município (keyword ou city), período sem verbo (publicação ou criação);
- regras de tempo relativo resolvidas na execução, com todas as leituras da tabela do manual,
  inclusive as parametrizadas da seção 6.2 ("últimos N meses", "desde AAAA"…).

**Famílias.**

| Família | Alvos | O que testa | Categorias |
|---|---|---|---|
| VS | 280 | um critério: estado, município, CGEO, projeto, folha, MI, INOM, tipo ou escala | S (+A, M) |
| VC | 360 | dois a quatro critérios combinados (metade tirada de um registro real) | C (+A, M) |
| VM | 160 | código MI ou INOM, sozinho ou com escala/tipo/CGEO/estado do mesmo registro | M, S/C (+A) |
| VT | 260 | período de publicação ou criação (15 regras fixas e 6 parametrizadas, anos reais) | T (+C, A) |
| VO | 200 | ordenação: direção, campo (pista de publicação, de criação ou nenhuma) e limite | O (+C, M, A) |
| VA | 200 | leituras múltiplas: estado ou capital, escala qualitativa, duas escalas, dois códigos, termo de projeto, folha homônima de município, região com critério, período sem verbo | A (+S, C, M, T) |
| VE | 150 | subespecificadas: pedido genérico, só região, só finalidade (categoria E) | E |
| VF | 340 | fora do domínio: cotidiano, dados não cartográficos, exterior/fictício, rotas, conceitos, serviços, conversa, produção de mapa e **armadilhas de vocabulário** ("carta de vinhos", "folha de pagamento", "escala de plantão") | F |

**Superfícies.** Cada valor é pedido numa forma de superfície sorteada entre as que o manual
e a descrição da ferramenta cobrem: escala como "1:25.000", "1:25000", "25k", "25 mil" ou
"escala detalhada"; tipo como "cartas topo", "ortos", "MDTs", "modelos digitais de
superfície"…; CGEO como "3º CGEO", "3o cgeo", "terceiro cgeo", "3º Centro de Geoinformação";
estado por extenso, pela sigla ou com a palavra "estado"; INOM com hífens ou compacto em
minúsculas ("sf22yd"); município com ou sem a sigla da UF.

**Registros de linguagem** (peso no sorteio): formal (15), direto (20), coloquial (15),
pergunta (15), telegráfico (10), sem acento (10), com um erro de digitação (5), com contexto
de uso (10). **Personas** (12): oficial do Exército, analista de CGEO, pesquisador, estudante,
técnico de prefeitura, engenheiro, servidor ambiental, professor, cidadão leigo, sargento
topógrafo, geólogo, agente da defesa civil — só tom e vocabulário, nunca critério.

**Cobertura das métricas.** Os alvos foram dimensionados para que cada medida do Cap. 5 tenha
casos suficientes: todos os 12 campos com dezenas a centenas de ocorrências (F1 por campo),
todos os 9 tipos de produto e as 8 escalas do enumerado, 340 consultas fora do domínio (recusa
com precisão, recall e F1), 150 subespecificadas e mais de 500 consultas com mais de uma
leitura aceita. As contagens finais estão em `data/lote_validacao/relatorio.md`.

## 5. Redação controlada

Os 1.950 alvos foram embaralhados (semente 2027) e divididos em 15 tarefas de 130, cada uma
com alvos de todas as famílias. Cada tarefa foi redigida por um agente de linguagem (Claude,
um agente por tarefa, em paralelo), com as instruções de `redacao.py` (`INSTRUCOES_REDATOR`):
uma mensagem por alvo; todos os itens de `pedido`, com cada forma de superfície literal;
nenhum critério além dos pedidos; tom da persona e do registro; variação de construção entre
mensagens. O redator recebeu só `pedido`, `proibido`, registro e persona — não o gabarito, as
categorias nem as notas de anotação — e foi instruído a não abrir nenhum outro arquivo do
repositório. Cada redator conferiu a própria saída (JSON válido, todos os ids, superfícies
presentes, nenhum termo proibido).

Adaptação recorrente relatada pelos redatores: nos alvos de ordenação com pista explícita de
campo, que também proíbem verbos de data, a pista foi escrita com substantivo ("em ordem de
publicação", "pela data de criação", "atualização mais recente"), forma que o manual aceita
como pista (seção 2, campo de ordenação).

## 6. Checagens automáticas e deduplicação

`montar_lote.py` descarta a consulta que:

- não contém algum trecho exigido (comparação sem acento e sem caixa);
- tem período com o verbo errado (publicação × criação) ou, no período sem verbo, algum verbo
  que desempate;
- contém marcador forte de um campo que o alvo não tem (tipo de produto, escala, CGEO, ano ou
  expressão de tempo, ordenação, projeto, código, sigla ou nome de UF), depois de retirar os
  trechos exigidos e contextos neutros ("primeiro CGEO", "últimos 3 meses", "desde já");
- contém nome de campo do sistema;
- repete, depois de normalizada, uma das 310 consultas ou outra consulta do lote.

Na primeira execução, as checagens reprovaram 121 consultas; a inspeção mostrou que todas eram
falsos positivos do próprio verificador (o número do CGEO em "4o cgeo" não era reconhecido; o
"3" de "últimos 3 meses" era retirado antes do contexto neutro; "desde já agradeço" contava
como expressão de tempo; o "2" de um limite quebrava o código "2392-3-SE"). Os quatro defeitos
foram corrigidos no verificador — não nas consultas — e os testes em
`tests/test_lote_validacao.py` cobrem os casos.

## 7. Anotação às cegas

Cada consulta redigida foi anotada de novo por um agente que **não conhece o alvo**:

- as consultas chegam embaralhadas (semente 2028), com identificador neutro (`Q0001`…), sem
  família, persona ou registro; a correspondência com o alvo só é gravada depois
  (`anotacao.py coletar`);
- o anotador recebe o manual (seções 1 a 6), a definição da ferramenta (`schema.py`), a lista
  de municípios do IBGE e o módulo `relative_time.py` para a aritmética das datas das tabelas
  do manual (a escolha da regra e do campo é do anotador), e é instruído a não abrir os alvos,
  as consultas redigidas, as tarefas de outros anotadores nem os resultados;
- formato idêntico ao da anotação independente das 310 (`data/auditoria/anotacao_independente.json`),
  mais o campo `aceita_nao_chamar` (categoria E).

Duas passadas: **A**, todas as consultas (15 anotadores, a passada que decide o filtro), e
**B**, uma amostra aleatória de 20% (semente 2029), anotada por outros três agentes, que não
participa do filtro e serve para medir a concordância entre anotadores e para estimar, sem
viés de seleção, a qualidade do gabarito do lote final.

## 8. Filtro de concordância e lote final

Entra no lote a consulta cujo gabarito por construção e anotação A são **compatíveis**:
mesma decisão (buscar / buscar ou esclarecer / não buscar) e leituras compatíveis nos dois
sentidos — a leitura preferencial do anotador é aceita pelo gabarito, e a do gabarito é aceita
pelo anotador (`audit.comparar_anotacao`, o mesmo critério usado na auditoria das 310). Nada é
corrigido à mão: consulta incompatível é descartada, com o motivo, em
`data/lote_validacao/descartes.json`.

O filtro tem um custo conhecido: remove as consultas em que duas leituras independentes do
texto divergem, que tendem a ser as mais difíceis. O lote final mede, portanto, o desempenho
em consultas cujo gabarito é **defensável por duas fontes independentes**; as descartadas são
relatadas por família e motivo, e a passada B (fora do filtro) estima a qualidade do gabarito
que ficou. Os números estão em `data/lote_validacao/relatorio.md`.

**Resultado.** Das 1.950 consultas redigidas, 1.929 (98,9%) formam o lote final:

| Etapa | Descartadas | Motivo |
|---|---|---|
| Checagens automáticas | 5 | alvos de região com "Sertão", que também é município (RS): a seção 6.3 faria dele `city`, o que o alvo não previa (apontado pelos próprios anotadores) |
| Deduplicação | 15 | 4 repetiam uma das 310 consultas ("cartas de São Paulo", "mapas do ce"…); 11 repetiam outra consulta do lote (pedidos genéricos e fora do domínio curtos) |
| Anotação às cegas | 1 | leitura do anotador não aceita pelo gabarito |

Concordância, sobre as 1.950 consultas, antes do filtro (construção × anotador A): decisão com
kappa 1,000; leituras compatíveis nos dois sentidos em 99,8%; leitura preferencial idêntica em
99,8% das que ambos buscam; valor igual em 100% dos campos preenchidos por ambos; detecção de
leituras múltiplas com kappa 0,967. Entre os dois anotadores (A × B, 390 consultas), todas as
medidas ficaram em 100%. Nas 383 consultas da amostra B que entraram no lote, o anotador B — que
não participou do filtro — é compatível com o gabarito em todas.

**Leitura desses números.** A concordância é alta por construção: os alvos exigem superfícies
explícitas e o manual decide as ambiguidades previstas. Ela mostra que cada consulta sustenta o
seu gabarito segundo o manual, com leituras reproduzíveis por anotadores independentes; não
mostra que pessoas leriam do mesmo modo, porque redatores e anotadores são modelos da mesma
família. Dois sinais indicam que a anotação não copiou o gabarito: na amostra B, os dois
anotadores concordam mais entre si (84 consultas com leituras múltiplas cada) do que com a
construção (86), e só 13 das 390 justificativas coincidem literalmente entre A e B (similaridade
textual média de 0,74).

**Ajuste de gabarito pelo texto.** Um único ajuste é feito na montagem, por regra do manual e a
partir do texto redigido: "copa do mundo"/"copa 2014" sem a palavra "projeto" não é nome
completo, sigla nem apelido informado na ferramenta, e o manual (seção 2, `project`) torna o
campo opcional nesse caso (12 consultas). A divergência foi apontada pelos anotadores.

## 9. Avaliação

### 9.1 Modelo e ambiente

Gemma 4 E4B (`gemma4:e4b-it-qat`), o modelo local de maior acurácia com *Tool Calling* nas
310, na mesma GPU T4 do Colab das rodadas completas, temperatura 0, uma repetição, sem SQL.
Data de referência: 24/09/2026 no lote (a da anotação) e 14/09/2026 nas 310 (a das rodadas v1).

### 9.2 Especificação v2

A análise de erros do Tool Calling v1 do Gemma 4 E4B nas 310 (918 execuções das métricas
principais, três repetições; 365 erradas; `lote.diagnostico_v1`, macros `\res{diag}{tc1}{…}`)
mostrou:

| Erro | Execuções |
|---|---|
| não buscou numa consulta do domínio | 161 (17,5%) |
| … das quais pedindo esclarecimento ("preciso saber qual é o ano atual", "especifique o tipo de produto") | 154 |
| `productType` acrescentado sem que a consulta nomeasse o tipo ("cartas"/"mapas" sozinhos) | 72 |
| código com sufixo acrescentado ("2901" → "2901-2-NE", o código do exemplo da descrição) ou "folha" como keyword | 21 |
| escala sem o ponto de milhar ("1:2000") | 21 |
| período relativo só com `start` igual à data atual ("este ano" → start = hoje) | 18 |

Outros erros pontuais do mesmo tipo: região que virou CGEO ("amazônia legal" → 1º CGEO),
estado que virou projeto ("mapas do amapá" → BCD do Amapá), "AM" lido como Amapá e plural sem
número com `limit = 1`.

Os dois erros mais frequentes da tabela, a não busca e o `productType` acrescentado, contrariam
instruções explícitas do *prompt* v1 (instrução 1, "Um único parâmetro basta"; instrução 2, "Só
deixe de chamar a ferramenta quando..."; instrução 3, "não complete campos por suposição"). O que
a descrição v1 de fato não informava são convenções do gabarito como "última atualização" →
`creationDate`, o fim nos períodos que vão até hoje e o preenchimento de uma escala qualitativa
("grande escala").

A v2 (`src/pfc_busca/v2.py`) muda **só a especificação**: (1) descrições dos parâmetros que
explicitam as convenções do manual (quando preencher cada campo, a forma canônica, o que não
deduzir), sem os códigos de exemplo da v1 e com a lista das siglas das 27 UFs; (2) no Tool
Calling, uma segunda ferramenta, `recusar_consulta(motivo)`, e a instrução de chamar exatamente
uma das duas, nunca pedindo esclarecimento; (3) na Saída Estruturada, as mesmas descrições, a
mesma regra e o campo `fora_do_escopo`, que torna a recusa representável. Tipos, enumerados e
mecanismo não mudam.

A v2 não ficou livre de exemplos copiáveis nem de ambiguidade de forma. A descrição de `keyword`
traz 'sf22yd' → 'SF-22-Y-D', o código da consulta N35 das 310 com o seu gabarito, e a de `limit`,
'a carta mais recente' → 1. A de `state` pede o nome por extenso, mas troca a regra com direção
da v1 ("Normalizar siglas: 'RJ' → 'Rio de Janeiro'") por uma lista de pares ("AC Acre, AL
Alagoas, …"), e os dois *prompts* v2 perderam a frase da instrução 1 da v1 "siglas, abreviações e
grafias sem acento são esperadas e devem ser reconhecidas e normalizadas".

As duas v2 recebem as mesmas descrições dos 12 parâmetros, mas o texto que enquadra a recusa
difere. Só o Tool Calling lê "mesmo que de forma vaga" (no *prompt*), "Uma consulta sem nenhum
parâmetro reconhecível ainda é uma busca: chame com os parâmetros vazios" (na descrição de
`buscar_catalogo`) e "Não use para consultas vagas sobre o acervo" (na de `recusar_consulta`).
Só a Saída Estruturada lê `{"fora_do_escopo": true} e nada mais` (no *prompt*) e "Consultas
vagas sobre o acervo não são fora do escopo" (na descrição do campo). A comparação TC v2 × SE v2
mede, portanto, o mecanismo junto com esse texto, sobretudo na recusa.

Como a v2 foi desenhada olhando os erros nas 310, esperava-se que o seu resultado **nas 310**
(dentro da amostra) fosse otimista. Não foi: nas 310, o TC v2 fez 47,4% e a SE v2, 68,0%, abaixo
das v1 no mesmo conjunto (60,1% e 75,2%). A comparação direta com o lote (62,8% e 72,4%) não
serve, porque o lote tem 17,4% de consultas F, que as duas v2 recusam, contra 2,6% nas 310. No
domínio, v2 − v1 foi de −13,1 p.p. (310) × +4,4 p.p. (lote) no TC e de −10,1 × −12,2 p.p. na SE:
dentro da amostra, a v2 foi pior do que fora dela no TC e parecida na SE. Das consultas do
domínio que o TC v1 acertava, o TC v2 errou 82/176 = 46,6% nas 310, contra 213/708 = 30,1% no
lote, em boa parte porque os erros de forma introduzidos pela v2 (sigla da UF, prefixo MI)
atingem formas que se repetem na camada G ('cartas de <UF>', 'folha MI <código> do <UF>'); a
composição explica de 40% a 85% do excesso de quebras, conforme a definição do estrato. Os consertos
dentro da amostra existem (nas 310, o TC v2 acertou 25 consultas em que o TC v1 não buscava e 18
em que buscava com erro), mas são menores que as quebras (82). A medida que vale continua sendo a do lote
(macros `\res{base}{tc1tc2}{…}` e `\res{lote}{tc1tc2}{…}` de `numeros_lote.tex`).

A docstring de `v2.py` não foi atualizada, porque o arquivo fica congelado junto com as rodadas,
e ainda diz "sem códigos de exemplo", "exatamente a mesma especificação" e "otimista"; vale o
que está nesta seção.

### 9.3 Configurações e conjuntos

| | Lote de validação | 310 consultas |
|---|---|---|
| Tool Calling v1 | rodado | rodada da T4 (Cap. 5, três repetições) |
| Saída Estruturada v1 | rodado | rodada da T4 (seção 5.3) |
| Tool Calling v2 | rodado | rodado (dentro da amostra) |
| Saída Estruturada v2 | rodado | rodado (dentro da amostra) |

### 9.4 Medidas

As mesmas do Cap. 5 — acurácia por consulta com IC de Wilson, F1 ponderado (e macro e micro),
F1 por campo, acurácia por categoria — e, com o tamanho do lote:

- **recusa como classificação**: positivo = consulta fora do domínio; previsto positivo = não
  buscou. Precisão, recall (a "recusa F" do Cap. 5), F1 e taxa de **falsa recusa** nas consultas
  do domínio (fora de F e E);
- **categoria E**: proporção que buscou sem filtros, que não buscou e que buscou com algum
  filtro (erro). Como no manual (seção 6.1), qualquer não busca conta como acerto, pedido de
  esclarecimento ou recusa. A SE v2 marca `fora_do_escopo` em todas as consultas E, o que
  contraria a própria descrição do campo; a acurácia com essas recusas contadas como erro sai
  em `\res{lote}{se2}{accEerro}`;
- acurácia nas consultas com **uma** e com **mais de uma** leitura aceita;
- acurácia por registro de linguagem e por subtipo (VA, VE, VF);
- comparações pareadas (TC v1 × SE v1, TC v2 × SE v2, TC v1 × TC v2, SE v1 × SE v2,
  TC v1 × SE v2): McNemar exato com uma observação por consulta e *bootstrap* pareado (2.000
  reamostragens das consultas, semente 42) para a diferença de acurácia e de F1 ponderado.

### 9.5 Medidas complementares (análise de 29/09/2026)

`python -m pfc_busca.evaluation.lote` também gera, nas macros `\res{...}` de
`numeros_lote.tex`, as medidas da síntese da análise do lote. São **simulações post hoc** sobre
as rodadas existentes, não pipelines executados:

- **duas etapas** (`hib`, função `duas_etapas`): o TC v2 decide se busca e, quando busca, valem
  os parâmetros da SE v1 na mesma consulta; latência = soma das duas chamadas quando há busca.
  Pares com a convenção de `comparar` (A × B, diferença B − A): `se2hib`, `se1hib`, `tc2hib`,
  `se1vaziohib` e `se2normhib` (SE v2 com as três normalizações);
- **regra do objeto vazio** (`se1vazio`, função `regra_objeto_vazio`): a resposta da SE v1 sem
  nenhum campo do schema conta como não busca (regra definida depois de ver os dados);
- as duas configurações derivadas, ao lado das quatro rodadas e nos dois conjuntos, vão para
  `tab_lote_duas_etapas.tex` (Tabela `tab:lote_duas_etapas` do Cap. 5);
- sigla da UF nas mesmas consultas (`siglamesmas`, TC v2 × SE v2): consultas do domínio com estado
  no gabarito em que as duas buscaram; sigla = primeira palavra do valor de `state` é uma sigla de
  UF (inclui a forma 'XX Nome' copiada da lista), com McNemar exato;
- decomposição TC v1 → v2 (consertos de falsa recusa, consertos de campo, quebras), saldos
  SE v1 → v2 por grupo, falsa recusa por forma da resposta (expressões regulares de
  `forma_nao_busca`) e por subgrupo, extração quando as duas buscam, subconjunto comum,
  diferença das diferenças nas leituras múltiplas e comparação por registro (Fisher exato);
- efeitos na SQL de `tools.montar_sql` sem banco: o ILIKE sobre os 27 nomes de UF e os
  municípios do IBGE (`ibge_municipios.json`) é reproduzido em Python e coincide, consulta a
  consulta, com o do PostgreSQL; a condição de *full-text* da keyword é aproximada (termos da
  consulta contidos no documento, sem radicalização);
- auditoria (`auditoria_complementar`): convenções que a descrição v1 não informa (K1 a K5),
  SQL das respostas erradas sem as aproximações de datas e a classe b sob dois critérios. O
  critério estrito usa os julgamentos de `data/lote_validacao/auditoria_criterios.json`
  (execuções b para o analista que contrariam uma regra escrita do manual); o amplo é calculado
  por código (b do analista, busca equivalente à de uma leitura aceita ou acerto sob K1 a K5).

## 10. Limitações

- **Texto sintético.** As consultas são redigidas por modelo de linguagem a partir de alvos,
  não colhidas de usuários reais; o controle por alvo garante o gabarito, mas a distribuição
  de formulações é a que o redator produz, dentro dos registros sorteados.
- **Mesma família de modelos na redação e na anotação.** Redatores e anotadores são agentes
  Claude; vieses de leitura comuns aos dois podem passar pelo filtro. O modelo avaliado é de
  outra família (Gemma), e a passada B mede a concordância entre anotadores diferentes.
- **Filtro conservador.** O lote exclui as consultas em que construção e anotação divergem;
  mede o desempenho em consultas de gabarito defensável, não em toda a variedade possível.
- **Um modelo, uma repetição.** O lote avalia só o Gemma 4 E4B; a variância entre repetições
  foi medida nas 310 (Cap. 5).
- **Nível de produto.** Como nas 310, a avaliação é da tradução em parâmetros; se a busca
  devolve a carta certa no acervo não é medido.

## 11. Reprodução

```bash
python scripts/lote_validacao/coletar_bdgex.py        # ~31 mil registros do CSW (opcional: o resumo já está versionado)
python scripts/lote_validacao/catalogo.py             # resumo do catálogo
python scripts/lote_validacao/gerar_alvos.py          # alvos.json (semente 2026)
python scripts/lote_validacao/redacao.py preparar     # tarefas dos redatores
python scripts/lote_validacao/redacao.py coletar      # consultas_redigidas.json
python scripts/lote_validacao/anotacao.py preparar    # tarefas dos anotadores (A e B)
python scripts/lote_validacao/anotacao.py coletar     # anotacao_A.json, anotacao_B.json
python scripts/lote_validacao/montar_lote.py          # data/lote_validacao.json + relatório
python scripts/empacotar_colab.py                     # dist/pfc_busca_colab.zip (com o lote e os hashes)
# Colab: notebooks/lote_validacao_colab.ipynb (T4)
python -m pfc_busca.evaluation.lote --paper ../paper_revisado
```

A redação e a anotação dependem de agentes de linguagem e não são deterministas; os textos
redigidos e as anotações de cada tarefa ficam versionados (`redacao/saida_*.json`,
`anotacao/saida_*.json`), de modo que as etapas seguintes são exatamente reprodutíveis.
