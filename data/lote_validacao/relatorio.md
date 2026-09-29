# Lote de validação — relatório de montagem

Gerado em 2026-09-29 09:15 por `scripts/lote_validacao/montar_lote.py`. Metodologia: `docs/lote_validacao.md`.

## Funil

| Etapa | Consultas |
|---|---|
| Alvos sorteados | 1950 |
| Consultas redigidas | 1950 |
| Passaram nas checagens automáticas | 1945 |
| Passaram na deduplicação | 1930 |
| Compatíveis com a anotação às cegas (A) — **lote final** | **1929** |

## Por família

| Família | Alvos | Checagem automática | Deduplicação | Anotação às cegas | Aceitas |
|---|---|---|---|---|---|
| VS | 280 | 0 | 3 | 0 | 277 (99%) |
| VC | 360 | 0 | 0 | 1 | 359 (100%) |
| VM | 160 | 0 | 0 | 0 | 160 (100%) |
| VT | 260 | 0 | 1 | 0 | 259 (100%) |
| VO | 200 | 0 | 1 | 0 | 199 (100%) |
| VA | 200 | 5 | 2 | 0 | 193 (96%) |
| VE | 150 | 0 | 4 | 0 | 146 (97%) |
| VF | 340 | 0 | 4 | 0 | 336 (99%) |

## Motivos de descarte (agrupados)

| Motivo | Ocorrências |
|---|---|
| região homônima de município: … | 5 |
| repete VE0025 | 2 |
| repete GS036 | 1 |
| repete GA005 | 1 |
| repete GS037 | 1 |
| leitura do anotador não aceita pelo gabarito: … (FP …) | 1 |
| repete VT0019 | 1 |
| repete VO0127 | 1 |
| repete N01 | 1 |
| repete VA0144 | 1 |
| repete VE0003 | 1 |
| repete VE0053 | 1 |
| repete VF0110 | 1 |
| repete VF0179 | 1 |
| repete VF0191 | 1 |
| repete VF0152 | 1 |

## Concordância

Medidas de `audit.concordancia` (as mesmas da auditoria das 310), calculadas sobre todas as consultas redigidas e anotadas, antes do filtro. A decisão tem três classes neste lote (E: buscar ou esclarecer).

### Gabarito por construção × anotador A (todas as consultas)

- consultas: 1950
- decisão (buscar / buscar ou esclarecer / não buscar): kappa de Cohen = 1.000
- leituras compatíveis nos dois sentidos: 1947/1950 (99.8%)
- leitura preferencial idêntica (quando ambos buscam): 1607/1610 (99.8%)
- presença de cada campo na leitura preferencial: kappa = 0.999
- valor igual quando ambos preenchem o campo: 3174/3174 (100.0%)
- detecção de leituras múltiplas: kappa = 0.967 (gabarito 475, anotador 477)

### Anotador A × anotador B (amostra aleatória de 20%)

- consultas: 390
- decisão (buscar / buscar ou esclarecer / não buscar): kappa de Cohen = 1.000
- leituras compatíveis nos dois sentidos: 390/390 (100.0%)
- leitura preferencial idêntica (quando ambos buscam): 317/317 (100.0%)
- presença de cada campo na leitura preferencial: kappa = 1.000
- valor igual quando ambos preenchem o campo: 601/601 (100.0%)
- detecção de leituras múltiplas: kappa = 1.000 (gabarito 84, anotador 84)

### Gabarito por construção × anotador B (mesma amostra)

- consultas: 390
- decisão (buscar / buscar ou esclarecer / não buscar): kappa de Cohen = 1.000
- leituras compatíveis nos dois sentidos: 389/390 (99.7%)
- leitura preferencial idêntica (quando ambos buscam): 316/317 (99.7%)
- presença de cada campo na leitura preferencial: kappa = 0.999
- valor igual quando ambos preenchem o campo: 600/600 (100.0%)
- detecção de leituras múltiplas: kappa = 0.952 (gabarito 86, anotador 84)

Nas consultas da amostra que entraram no lote, o anotador B — que não participou do filtro — é compatível com o gabarito em 383/383 (100.0%). Essa é a estimativa independente da qualidade do gabarito do lote final.

## Composição do lote final

| Categoria | Consultas |
|---|---|
| S | 389 |
| C | 955 |
| M | 281 |
| T | 278 |
| O | 199 |
| A | 927 |
| E | 146 |
| F | 336 |

Consultas com mais de uma leitura aceita: 471; categoria E (buscar ou esclarecer): 146; fora do domínio: 336.

| Campo | Ocorrências no gabarito |
|---|---|
| `keyword` | 492 |
| `scale` | 415 |
| `productType` | 386 |
| `state` | 308 |
| `city` | 203 |
| `supplyArea` | 346 |
| `project` | 182 |
| `publicationPeriod` | 215 |
| `creationPeriod` | 63 |
| `sortField` | 199 |
| `sortDirection` | 199 |
| `limit` | 151 |

| Registro | Consultas |
|---|---|
| direto | 389 |
| formal | 323 |
| coloquial | 306 |
| pergunta | 291 |
| sem_acento | 228 |
| telegrafico | 158 |
| contexto | 154 |
| erro_digitacao | 80 |

| Subtipo (VA, VE, VF) | Alvos | Aceitas |
|---|---|---|
| VA·dois_codigos | 12 | 12 |
| VA·duas_escalas | 15 | 15 |
| VA·escala_qualitativa | 32 | 32 |
| VA·estado_ou_capital | 41 | 39 |
| VA·folha_municipio | 33 | 33 |
| VA·periodo_sem_verbo | 19 | 19 |
| VA·projeto_termo | 18 | 18 |
| VA·regiao_com_criterio | 30 | 25 |
| VE·finalidade | 33 | 33 |
| VE·generica | 72 | 69 |
| VE·regiao | 45 | 44 |
| VF·armadilha_lexical | 65 | 65 |
| VF·conceitual | 32 | 31 |
| VF·conversa | 14 | 14 |
| VF·cotidiano | 53 | 51 |
| VF·dados | 26 | 26 |
| VF·exterior | 49 | 49 |
| VF·ficcao | 21 | 20 |
| VF·producao | 18 | 18 |
| VF·rotas | 23 | 23 |
| VF·servicos | 39 | 39 |

## Exemplos aceitos (5 por família, sorteados)

- `VS0167` preciso de mapas de rodelas pra minha pesquisa → city: "Rodelas"
- `VS0079` Solicito as cartas disponíveis do município de São Domingos. → city: "São Domingos"
- `VS0205` Existe alguma carta de Pernambuco no acervo de vocês? → state: "Pernambuco"
- `VS0025` Vocês têm cartas do Piauí? É pra um trabalho da faculdade. → state: "Piauí"
- `VS0038` cartas copa das confederacoes → project: "Copa das Confederações"
- `VC0276` Onde acho cartas topográficas vetoriais do 5º CGEO? → productType: "SCN Carta Topográfica Vetorial"; supplyArea: "5° Centro de Geoinformação"
- `VC0050` À equipe técnica: solicitamos as ortoimagens do projeto olimpíadas, para subsidiar o planejamento de ações de resposta. → productType: "SCN Carta Ortoimagem"; project: "Olimpíadas Rio 2016"
- `VC0189` Oi, vocês têm a carta topográfica da folha Rio Catete do 3o cgeo? → productType: "SCN Carta Topográfica Matricial"; supplyArea: "3° Centro de Geoinformação"; keyword: "Rio Catete"
- `VC0300` Estou procurnado cartas de Araçariguama do primeiro Centro de Geoinformação para a minha pesquisa. → supplyArea: "1° Centro de Geoinformação"; city: "Araçariguama"
- `VC0031` Nosso órgão necessita das cartas vetoriais do mapeamento sistematico; poderiam disponibilizá-las, por gentileza? → productType: "SCN Carta Topográfica Vetorial"; project: "Mapeamento Sistemático"
- `VM0130` Prezados, solicito, por gentileza, a folha 0562-2 referente ao estado de Pernambuco. → keyword: "0562-2"; state: "Pernambuco"
- `VM0055` Solicito, respeitosamente, a carta correspondente ao INOM SG-22-V-C-IV. → keyword: "SG-22-V-C-IV"
- `VM0010` Me arruma a folha MI 1719-4-NO aí, por favor? → keyword: "1719-4-NO"
- `VM0023` Consegue me mandar as topográficas 1:100.000 da SE-21-Z-B-V? → keyword: "SE-21-Z-B-V"; productType: "SCN Carta Topográfica Matricial"; scale: "1:100.000"
- `VM0112` folha 006 → keyword: "006"
- `VT0216` cartas temáticas do terceiro cgeo publicadas nos últimos 2 meses → publicationPeriod: últimos 2 meses; productType: "Cartas Temáticas Não SCN"; supplyArea: "3° Centro de Geoinformação"
- `VT0036` folhas nos últimos 7 dias → publicationPeriod: últimos 7 dias
- `VT0124` Algum MDS foi elaborado desde 2010? → creationPeriod: desde 2010; productType: "MDS — RAM"
- `VT0047` Preicso das cartas 1:100.000 do Amazonas desde 2014 para um estudo de viabilidade. → publicationPeriod: desde 2014; scale: "1:100.000"; state: "Amazonas"
- `VT0219` Olá, boa tarde. Seria possível consultar as cartas de Senador Canedo nos últimos 4 meses? Fico no aguardo, obrigado. → publicationPeriod: últimos 4 meses; city: "Senador Canedo"
- `VO0016` qual a carta mais recente por data de publicacao? → limit: 1 (opcional); sortField: "publicationDate"; sortDirection: "DESC"
- `VO0145` Manda aí as ortoimg mais antigas do 2º Centro de Geoinformação. → sortField: "publicationDate" ou "creationDate"; sortDirection: "ASC"; supplyArea: "2° Centro de Geoinformação"; productType: "SCN Carta Ortoimagem"
- `VO0032` Tenho um mapa guardado em casa e queria comparar com o de vocês, então preciso da mais antiga entre as topográficas da MI-0096-2. → limit: 1 (opcional); sortField: "publicationDate" ou "creationDate"; sortDirection: "ASC"; keyword: "0096-2"; productType: "SCN Carta Topográfica Matricial"
- `VO0058` Precsio das cartas mais recentes de Chapadão do Céu em escala detalhada. → sortField: "publicationDate" ou "creationDate"; sortDirection: "DESC"; city: "Chapadão do Céu"; scale: "1:25.000"
- `VO0162` Gostaria de solicitar a carta 1:100.000 mais antiga, seguindo a ordem de publicação. → limit: 1 (opcional); sortField: "publicationDate"; sortDirection: "ASC"; scale: "1:100.000"
- `VA0168` Tem uns mapas de Apiúna em média escala pra eu dar uma olhada? → scale: "1:50.000" ou "1:100.000"; city: "Apiúna"
- `VA0156` Será que tem cartas 1:2000 anteriores a 2010? Tô precisando. → publicationPeriod: antes de 2010; scale: "1:2.000"
- `VA0016` cartas Pará escala maior que 100k → scale: "1:50.000" ou "1:25.000" ou "1:10.000" ou "1:5.000" ou "1:2.000" ou "1:1.000"; state: "Pará"
- `VA0154` ortos nos últimos cinco anos → publicationPeriod: últimos 5 anos; productType: "SCN Carta Ortoimagem"
- `VA0105` Gostaria de solicitar cartas de São Paulo em escala detalhada para meu trabalho de conclusão de curso. Muito obrigado. → state: "São Paulo"; scale: "1:25.000"
- `VE0013` Onde eu acho mapas do litoral brasileiro para mostrar aos alunos? → {} (ou esclarecer)
- `VE0058` Há mapas da região Sul no acervo? → {} (ou esclarecer)
- `VE0012` Ao setor responsável: solicito acesso às cartas referentes à região Norte, para fins de pesquisa acadêmica. → {} (ou esclarecer)
- `VE0147` acervo, cartas e mapas → {} (ou esclarecer)
- `VE0035` mapas da região Sul → {} (ou esclarecer)
- `VF0150` Prezados, poderiam me enviar uma receita de bolo de chocolate para a confraternização da equipe? → não buscar
- `VF0217` Existe algum mapa de Atlântida, mesmo sendo uma lenda? → não buscar
- `VF0074` PIB de Pernambuco no último ano → não buscar
- `VF0280` Como é que eu chego na rodoviária daqui? Tô meio perdido. → não buscar
- `VF0061` quanto ta o dolar hoje → não buscar

## Exemplos descartados (sorteados)

- `VF0189` [deduplicação] mapa de Nárnia — repete VF0179
- `VA0110` [checagem automática] Há cartas vetoriais do Sertão no acervo? — região homônima de município: 'Sertão'
- `VF0140` [deduplicação] o que é projeção UTM — repete VF0110
- `VO0174` [deduplicação] Quais são as cartas topográficas vetoriais mais antigas que vocês têm? — repete VO0127
- `VC0004` [anotação às cegas] cartas Bálsamo - AMAN — leitura do anotador não aceita pelo gabarito: {"keyword": "Bálsamo", "project": "AMAN"} (FP ['keyword'], FN ['city'])
- `VA0077` [checagem automática] Tô precisando de carta de 50 mil lá do Sertão pra minha pesquisa, tem aí? — região homônima de município: 'Sertão'
- `VF0316` [deduplicação] cotação do dólar hoje — repete VF0152
- `VS0178` [deduplicação] mapas do CE — repete GA005
- `VA0104` [checagem automática] cartas do Sertão em 1:100000 — região homônima de município: 'Sertão'
- `VA0118` [checagem automática] qeuria mapas do Sertão em 1:50.000, tem como ver? — região homônima de município: 'Sertão'
- `VE0044` [deduplicação] cartas do semiárido — repete VE0003
- `VF0264` [deduplicação] principais notícias do dia — repete VF0191
- `VS0041` [deduplicação] produtos do quarto cgeo — repete GS036
- `VE0116` [deduplicação] cartas e mapas do acervo — repete VE0025
- `VA0081` [deduplicação] cartas de São Paulo — repete N01
- `VE0071` [deduplicação] cartas e mapas do acervo — repete VE0025
- `VT0186` [deduplicação] mapas no primeiro trimestre deste ano — repete VT0019
- `VE0100` [deduplicação] ver cartas do acervo — repete VE0053
- `VA0117` [checagem automática] cartas 1:50000 Sertão — região homônima de município: 'Sertão'
- `VS0210` [deduplicação] produtos do 5º CGEO — repete GS037
- `VA0166` [deduplicação] cartas Rio de Janeiro — repete VA0144
