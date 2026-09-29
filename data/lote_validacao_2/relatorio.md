# Lote de validação — relatório de montagem

Gerado em 2026-09-29 09:37 por `scripts/lote_validacao/montar_lote.py`. Metodologia: `docs/lote_validacao.md`.

## Funil

| Etapa | Consultas |
|---|---|
| Alvos sorteados | 975 |
| Consultas redigidas | 975 |
| Passaram nas checagens automáticas | 975 |
| Passaram na deduplicação | 949 |
| Compatíveis com a anotação às cegas (A) — **lote final** | **945** |

## Por família

| Família | Alvos | Checagem automática | Deduplicação | Anotação às cegas | Aceitas |
|---|---|---|---|---|---|
| VS | 140 | 0 | 5 | 1 | 134 (96%) |
| VC | 180 | 0 | 0 | 3 | 177 (98%) |
| VM | 80 | 0 | 1 | 0 | 79 (99%) |
| VT | 130 | 0 | 0 | 0 | 130 (100%) |
| VO | 100 | 0 | 1 | 0 | 99 (99%) |
| VA | 100 | 0 | 2 | 0 | 98 (98%) |
| VE | 75 | 0 | 10 | 0 | 65 (87%) |
| VF | 170 | 0 | 7 | 0 | 163 (96%) |

## Motivos de descarte (agrupados)

| Motivo | Ocorrências |
|---|---|
| leitura do anotador não aceita pelo gabarito: … (FP …) | 4 |
| repete VS0119 | 1 |
| repete VS0101 | 1 |
| repete GA002 | 1 |
| repete GS029 | 1 |
| repete BVS0030 | 1 |
| repete BVM0003 | 1 |
| repete VO0085 | 1 |
| repete N01 | 1 |
| repete BVA0032 | 1 |
| repete VE0149 | 1 |
| repete VE0017 | 1 |
| repete VE0014 | 1 |
| repete VE0067 | 1 |
| repete VE0136 | 1 |
| repete VE0140 | 1 |
| repete BVE0013 | 1 |
| repete BVE0019 | 1 |
| repete VE0056 | 1 |
| repete VE0041 | 1 |
| repete VF0191 | 1 |
| repete VF0332 | 1 |
| repete VF0243 | 1 |
| repete VF0092 | 1 |
| repete VF0179 | 1 |
| repete VF0097 | 1 |
| repete VF0109 | 1 |

## Concordância

Medidas de `audit.concordancia` (as mesmas da auditoria das 310), calculadas sobre todas as consultas redigidas e anotadas, antes do filtro. A decisão tem três classes neste lote (E: buscar ou esclarecer).

### Gabarito por construção × anotador A (todas as consultas)

- consultas: 975
- decisão (buscar / buscar ou esclarecer / não buscar): kappa de Cohen = 1.000
- leituras compatíveis nos dois sentidos: 971/975 (99.6%)
- leitura preferencial idêntica (quando ambos buscam): 801/805 (99.5%)
- presença de cada campo na leitura preferencial: kappa = 0.998
- valor igual quando ambos preenchem o campo: 1565/1565 (100.0%)
- detecção de leituras múltiplas: kappa = 0.961 (gabarito 236, anotador 239)

### Anotador A × anotador B (amostra aleatória de 20%)

- consultas: 195
- decisão (buscar / buscar ou esclarecer / não buscar): kappa de Cohen = 1.000
- leituras compatíveis nos dois sentidos: 195/195 (100.0%)
- leitura preferencial idêntica (quando ambos buscam): 156/156 (100.0%)
- presença de cada campo na leitura preferencial: kappa = 1.000
- valor igual quando ambos preenchem o campo: 289/289 (100.0%)
- detecção de leituras múltiplas: kappa = 1.000 (gabarito 40, anotador 40)

### Gabarito por construção × anotador B (mesma amostra)

- consultas: 195
- decisão (buscar / buscar ou esclarecer / não buscar): kappa de Cohen = 1.000
- leituras compatíveis nos dois sentidos: 195/195 (100.0%)
- leitura preferencial idêntica (quando ambos buscam): 156/156 (100.0%)
- presença de cada campo na leitura preferencial: kappa = 1.000
- valor igual quando ambos preenchem o campo: 289/289 (100.0%)
- detecção de leituras múltiplas: kappa = 0.983 (gabarito 39, anotador 40)

Nas consultas da amostra que entraram no lote, o anotador B — que não participou do filtro — é compatível com o gabarito em 191/191 (100.0%). Essa é a estimativa independente da qualidade do gabarito do lote final.

## Composição do lote final

| Categoria | Consultas |
|---|---|
| S | 192 |
| C | 466 |
| M | 130 |
| T | 139 |
| O | 99 |
| A | 457 |
| E | 65 |
| F | 163 |

Consultas com mais de uma leitura aceita: 233; categoria E (buscar ou esclarecer): 65; fora do domínio: 163.

| Campo | Ocorrências no gabarito |
|---|---|
| `keyword` | 241 |
| `scale` | 197 |
| `productType` | 192 |
| `state` | 139 |
| `city` | 100 |
| `supplyArea` | 175 |
| `project` | 100 |
| `publicationPeriod` | 105 |
| `creationPeriod` | 34 |
| `sortField` | 99 |
| `sortDirection` | 99 |
| `limit` | 64 |

| Registro | Consultas |
|---|---|
| direto | 170 |
| pergunta | 167 |
| coloquial | 155 |
| formal | 148 |
| sem_acento | 115 |
| contexto | 79 |
| telegrafico | 75 |
| erro_digitacao | 36 |

| Subtipo (VA, VE, VF) | Alvos | Aceitas |
|---|---|---|
| VA·dois_codigos | 8 | 8 |
| VA·duas_escalas | 12 | 12 |
| VA·escala_qualitativa | 21 | 20 |
| VA·estado_ou_capital | 18 | 17 |
| VA·folha_municipio | 18 | 18 |
| VA·periodo_sem_verbo | 9 | 9 |
| VA·projeto_termo | 6 | 6 |
| VA·regiao_com_criterio | 8 | 8 |
| VE·finalidade | 20 | 18 |
| VE·generica | 30 | 24 |
| VE·regiao | 25 | 23 |
| VF·armadilha_lexical | 33 | 31 |
| VF·conceitual | 21 | 20 |
| VF·conversa | 16 | 15 |
| VF·cotidiano | 17 | 16 |
| VF·dados | 19 | 19 |
| VF·exterior | 14 | 14 |
| VF·ficcao | 11 | 10 |
| VF·producao | 6 | 6 |
| VF·rotas | 14 | 14 |
| VF·servicos | 19 | 18 |

## Exemplos aceitos (5 por família, sorteados)

- `BVS0086` Me passa aí as cartas de Água Nova, vou precisar pra planejar uma missão. → city: "Água Nova"
- `BVS0040` Vocês têm a carta MI 1998-3-SO? → keyword: "1998-3-SO"
- `BVS0106` Aqui na defesa civil vamos cruzar as áreas de risco de enchente no nosso SIG e precisamos de cartas vetoriais pra isso. → productType: "SCN Carta Topográfica Vetorial"
- `BVS0013` cartas de Lagoa do Barro do Piauí → city: "Lagoa do Barro do Piauí"
- `BVS0019` Onde encontro a folha sh21xdvi1? → keyword: "SH-21-X-D-VI-1"
- `BVC0141` cartas topográficas da copa das confederações do quarto Centro de Geoinformação → project: "Copa das Confederações"; supplyArea: "4° Centro de Geoinformação"; productType: "SCN Carta Topográfica Matricial"
- `BVC0025` Requisito, por favor, as ortoimagens banda X HH de Capivari, SP, referentes ao projeto copa das confederacoes. → project: "Copa das Confederações"; city: "Capivari"; state: "São Paulo"; productType: "SCN Carta Ortoimagem Banda X Pol HH"
- `BVC0097` cartas 25k do 2º Centro de Geoinformação → scale: "1:25.000"; supplyArea: "2° Centro de Geoinformação"
- `BVC0153` Prezados, solicito acesso à folha Cabeceira do Igarapé Capivara, do primeiro Centro de Geoinformação, para fins de pesquisa acadêmica. → keyword: "Cabeceira do Igarapé Capivara"; supplyArea: "1° Centro de Geoinformação"
- `BVC0015` Prezados, gostaria de solicitar a carta Bazuá, entre as cartas topo. Atenciosamente. → keyword: "Bazuá"; productType: "SCN Carta Topográfica Matricial"
- `BVM0066` folha 2961-1 50 mil → keyword: "2961-1"; scale: "1:50.000"
- `BVM0028` SF-23-V-C-VI-1 do 2o cgeo → keyword: "SF-23-V-C-VI-1"; supplyArea: "2° Centro de Geoinformação"
- `BVM0005` dá uma força aí, preciso da folha sf23xdiii4 → keyword: "SF-23-X-D-III-4"
- `BVM0012` tem a sa-20-y-c-vi-2 do tocantins do segundo centro de geoinformacao? vou pro campo e preciso dela → keyword: "SA-20-Y-C-VI-2"; state: "Tocantins"; supplyArea: "2° Centro de Geoinformação"
- `BVM0057` A carta MI 0031-2-SO da Paraíba está disponível pra download? → keyword: "0031-2-SO"; state: "Paraíba"
- `BVT0108` mapas feitos entre 2010 e 2013 → creationPeriod: 2010-01-01 a 2013-12-31
- `BVT0018` Com vistas ao planejamento operacional, necessito das cartas do estado do Rio Grande do Norte publicadas antes de 2009. Agradeço a atenção. → publicationPeriod: antes de 2009; state: "Rio Grande do Norte"
- `BVT0062` Gostaria de consultar as cartas publicadas após 2018 do 3o cgeo, poderiam me indicr onde estão? → publicationPeriod: depois de 2018; supplyArea: "3° Centro de Geoinformação"
- `BVT0024` Tem carta 1:25000 feita a partir de 2010? → creationPeriod: desde 2010; scale: "1:25.000"
- `BVT0109` Tem como me passar as cartas 1:25000 que foram feitas antes de 2010? → creationPeriod: antes de 2010; scale: "1:25.000"
- `BVO0008` Na construtora a gente está montando um estudo preliminar, e eu gostaria de ver as cinco cartas mais recentes do acervo. → limit: 5; sortField: "publicationDate" ou "creationDate"; sortDirection: "DESC"
- `BVO0074` Olá. Gostaria de obter, entre as cartas topográficas vetoriais do 3º CGEO, a mais recente disponível no acervo. → limit: 1 (opcional); sortField: "publicationDate" ou "creationDate"; sortDirection: "DESC"; supplyArea: "3° Centro de Geoinformação"; productType: "SCN Carta Topográfica Vetorial"
- `BVO0016` Quais são as cinco cartas mais recentes de Grão-Pará por data de publicação? → limit: 5; sortField: "publicationDate"; sortDirection: "DESC"; city: "Grão-Pará"
- `BVO0029` preciso das 2 circ de redencao com a atualizacao mais recente, to indo pra campo → limit: 2; sortField: "creationDate"; sortDirection: "DESC"; city: "Redenção"; productType: "CIRC"
- `BVO0082` me mostra as 4 cartas topograficas vetoriais mais antigas → limit: 4; sortField: "publicationDate" ou "creationDate"; sortDirection: "ASC"; productType: "SCN Carta Topográfica Vetorial"
- `BVA0082` Seria possível me enviar a relação das CIRC em 2009? → publicationPeriod: 2009-01-01 a 2009-12-31; productType: "CIRC"
- `BVA0076` alguem sabe onde acho a folha eldorado → keyword: "Eldorado"
- `BVA0008` mapas São Paulo → state: "São Paulo"
- `BVA0075` É possível encontrar cartas topográficas em grande escala aqui? → scale: "1:25.000" ou "1:10.000" ou "1:5.000" ou "1:2.000" ou "1:1.000"; productType: "SCN Carta Topográfica Matricial"
- `BVA0052` Estou organizando um trabalho de campo em Ferreira Gomes e preciso das cartas da cartografia sistemática que cobrem o município. → project: "Mapeamento Sistemático" (opcional); city: "Ferreira Gomes"
- `BVE0007` Senhores, solicito cartas que sirvam de apoio ao projeto de uma estrada. Grato pela atenção. → {} (ou esclarecer)
- `BVE0036` Opa, dá pra me mandar mapas pra levar num trabalho de campo? Sou leigo e não sei bem o que pedir. → {} (ou esclarecer)
- `BVE0006` listagem geral cartas acervo → {} (ou esclarecer)
- `BVE0022` Quais cartas vocês indicariam para uma aula de geografia? Vou ministrar uma instrução para os recrutas. → {} (ou esclarecer)
- `BVE0045` quais mapas voces tem? → {} (ou esclarecer)
- `BVF0114` Alguém me passa a escala de plantão do laboratório? Não sei se fico no sábado ou no domingo. → não buscar
- `BVF0038` tem mapa de lisboa pra eu baixar? → não buscar
- `BVF0146` Prezados, gostaria de saber onde posso obter o índice de chuva acumulada deste mês para um trabalho da faculdade. → não buscar
- `BVF0032` Poderiam me explicar o que é um MDT e para que ele é utilizado? → não buscar
- `BVF0154` Venho por meio desta parabenizar a equipe pela excelente qualidade do sistema e pelo atendimento. Muito obrigado. → não buscar

## Exemplos descartados (sorteados)

- `BVM0034` [deduplicação] carta MI 1590-1-NO — repete BVM0003
- `BVE0025` [deduplicação] listar cartas do acervo — repete VE0136
- `BVF0087` [deduplicação] escala de dó maior no violão — repete VF0092
- `BVE0057` [deduplicação] mapas para aula de geografia — repete VE0056
- `BVS0134` [deduplicação] cartas do segundo cgeo — repete BVS0030
- `BVS0087` [deduplicação] mapas do PR — repete GA002
- `BVE0026` [deduplicação] acervo: cartas e mapas disponíveis — repete VE0140
- `BVF0020` [deduplicação] principais notícias do dia — repete VF0191
- `BVE0054` [deduplicação] Cartas da região Sul — repete BVE0019
- `BVC0033` [anotação às cegas] Preciso das cartas em 1:100000 da BCD do Amapá, do 2º CGEO, para o planejamento da operção. — leitura do anotador não aceita pelo gabarito: {"scale": "1:100.000", "project": "Base Cartográfica Digital do Amapá", "supplyArea": "2° Centro de Geoinformação", "state": "Amapá"} (FP ['state'], FN [])
- `BVA0038` [deduplicação] cartas de São Paulo — repete N01
- `BVF0054` [deduplicação] significado das cartas de tarô — repete VF0332
- `BVF0109` [deduplicação] esqueci minha senha, como faco pra recuperar o acesso — repete VF0097
- `BVS0075` [deduplicação] cartas do terceiro cgeo — repete VS0101
- `BVS0057` [anotação às cegas] Há cartas da BCD da Bahia disponíveis para consulta? — leitura do anotador não aceita pelo gabarito: {"project": "Base Cartográfica Digital da Bahia", "state": "Bahia"} (FP ['state'], FN [])
- `BVF0137` [deduplicação] o que é um MDT e pra que serve — repete VF0109
- `BVE0070` [deduplicação] cartas do acervo — repete VE0041
- `BVC0052` [anotação às cegas] cartas Mampituba 1:25.000, projeto copa das confederacoes, do 3º CGEO — leitura do anotador não aceita pelo gabarito: {"keyword": "Mampituba", "scale": "1:25.000", "project": "Copa das Confederações", "supplyArea": "3° Centro de Geoinformação"} (FP ['keyword'], FN ['city'])
- `BVO0050` [deduplicação] qual a carta mais antiga que voces tem — repete VO0085
- `BVC0071` [anotação às cegas] cartas Anapurus 50k — leitura do anotador não aceita pelo gabarito: {"keyword": "Anapurus", "scale": "1:50.000"} (FP ['keyword'], FN ['city'])
- `BVF0089` [deduplicação] mapa de Nárnia — repete VF0179
- `BVF0074` [deduplicação] valeu demais pela ajuda, era isso mesmo que eu precisava — repete VF0243
- `BVA0091` [deduplicação] mapas temáticos média escala — repete BVA0032
- `BVS0133` [deduplicação] MDTs disponíveis — repete GS029
- `BVE0009` [deduplicação] cartas para exercício militar — repete VE0149
