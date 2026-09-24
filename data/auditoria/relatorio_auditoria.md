# Auditoria do dataset de avaliação

Dataset: `data/dataset.json` (sha256 `07bf424a40d68392…`), 310 consultas.

## 1. Estrutura

Nenhum problema estrutural.

## 2. Consistência entre casos



- **detalhad** → `scale` (resolvido por exceção justificada): "1:25.000" em P21, GC018, GA018; {"$um_de": ["1:25.000", "1:50.000"]} em P14
  - P14: as escalas explícitas '(25k ou 50k)' prevalecem sobre o qualificativo 'detalhado'

## 3. Evidência (anotador por regras × gabarito)

310 de 310 consultas sem apontamento. Apontamentos por tipo:


| ID | Consulta | Gabarito | Apontamentos |
|---|---|---|---|

## 4. Anotação independente às cegas

Concordância com o gabarito em 309 de 310 consultas (99.7%).

| ID | Consulta | Gabarito | Divergência |
|---|---|---|---|
| GF007 | cartas do estado 42 | não chamar | chamar_ferramenta: gabarito=False anotador=True |

### Concordância (antes → após a adjudicação)

| Medida | Antes | Após |
|---|---|---|
| Decisão (chamar / não chamar / observacional) | 302/310 (97.4%) | 310/310 (100.0%) |
| — kappa de Cohen | 0.658 | 1.000 |
| Leituras compatíveis nos dois sentidos | 300/310 (96.8%) | 309/310 (99.7%) |
| Leitura preferencial idêntica | 294/298 (98.7%) | 294/298 (98.7%) |
| Presença de campo (kappa, 12 campos) | 0.999 | 0.999 |
| Valor igual quando ambos anotam | 534/537 (99.4%) | 534/537 (99.4%) |
| Mais de uma leitura aceita | 296/298 (99.3%) | 297/298 (99.7%) |
| — kappa de Cohen | 0.981 | 0.990 |
| Consultas com divergência em alguma medida, sem decisão | 14 | 0 |

### Por campo (após)

| Campo | Gabarito | Anotador | Ambos | Kappa | Valor igual |
|---|---|---|---|---|---|
| `keyword` | 62 | 62 | 62 | 1.000 | 62/62 |
| `scale` | 84 | 84 | 84 | 1.000 | 83/84 |
| `productType` | 44 | 44 | 44 | 1.000 | 44/44 |
| `state` | 130 | 130 | 130 | 1.000 | 130/130 |
| `city` | 27 | 27 | 27 | 1.000 | 27/27 |
| `supplyArea` | 40 | 40 | 40 | 1.000 | 40/40 |
| `project` | 11 | 10 | 10 | 0.951 | 10/10 |
| `publicationPeriod` | 51 | 51 | 51 | 1.000 | 51/51 |
| `creationPeriod` | 10 | 10 | 10 | 1.000 | 10/10 |
| `sortField` | 29 | 29 | 29 | 1.000 | 27/29 |
| `sortDirection` | 29 | 29 | 29 | 1.000 | 29/29 |
| `limit` | 21 | 21 | 21 | 1.000 | 21/21 |

## 5. Adjudicação

| ID | Etapa | Divergência | Decisão | Justificativa |
|---|---|---|---|---|
| N36 | anotação independente | o gabarito classificava a consulta como observacional; o anotador a tratou como fora do domínio, com gabarito determinado 'não chamar' | corrigido | P4 e seção “Consultas fora do domínio” do manual: consulta sem intenção de busca no acervo brasileiro tem comportamento correto determinado (não chamar); P6 reserva 'observacional' às consultas cujo comportamento correto não é determinável. A consulta passa às métricas principais, na categoria F (fora do domínio). |
| N37 | anotação independente | o gabarito classificava a consulta como observacional; o anotador a tratou como fora do domínio, com gabarito determinado 'não chamar' | corrigido | P4 e seção “Consultas fora do domínio” do manual: consulta sem intenção de busca no acervo brasileiro tem comportamento correto determinado (não chamar); P6 reserva 'observacional' às consultas cujo comportamento correto não é determinável. A consulta passa às métricas principais, na categoria F (fora do domínio). |
| GF001 | anotação independente | o gabarito classificava a consulta como observacional; o anotador a tratou como fora do domínio, com gabarito determinado 'não chamar' | corrigido | P4 e seção “Consultas fora do domínio” do manual: consulta sem intenção de busca no acervo brasileiro tem comportamento correto determinado (não chamar); P6 reserva 'observacional' às consultas cujo comportamento correto não é determinável. A consulta passa às métricas principais, na categoria F (fora do domínio). |
| GF002 | anotação independente | o gabarito classificava a consulta como observacional; o anotador a tratou como fora do domínio, com gabarito determinado 'não chamar' | corrigido | P4 e seção “Consultas fora do domínio” do manual: consulta sem intenção de busca no acervo brasileiro tem comportamento correto determinado (não chamar); P6 reserva 'observacional' às consultas cujo comportamento correto não é determinável. A consulta passa às métricas principais, na categoria F (fora do domínio). |
| GF003 | anotação independente | o gabarito classificava a consulta como observacional; o anotador a tratou como fora do domínio, com gabarito determinado 'não chamar' | corrigido | P4 e seção “Consultas fora do domínio” do manual: consulta sem intenção de busca no acervo brasileiro tem comportamento correto determinado (não chamar); P6 reserva 'observacional' às consultas cujo comportamento correto não é determinável. A consulta passa às métricas principais, na categoria F (fora do domínio). |
| GF004 | anotação independente | o gabarito classificava a consulta como observacional; o anotador a tratou como fora do domínio, com gabarito determinado 'não chamar' | corrigido | P4 e seção “Consultas fora do domínio” do manual: consulta sem intenção de busca no acervo brasileiro tem comportamento correto determinado (não chamar); P6 reserva 'observacional' às consultas cujo comportamento correto não é determinável. A consulta passa às métricas principais, na categoria F (fora do domínio). |
| GF005 | anotação independente | o gabarito classificava a consulta como observacional; o anotador a tratou como fora do domínio, com gabarito determinado 'não chamar' | corrigido | P4 e seção “Consultas fora do domínio” do manual: consulta sem intenção de busca no acervo brasileiro tem comportamento correto determinado (não chamar); P6 reserva 'observacional' às consultas cujo comportamento correto não é determinável. A consulta passa às métricas principais, na categoria F (fora do domínio). |
| GF006 | anotação independente | o gabarito classificava a consulta como observacional; o anotador a tratou como fora do domínio, com gabarito determinado 'não chamar' | corrigido | P4 e seção “Consultas fora do domínio” do manual: consulta sem intenção de busca no acervo brasileiro tem comportamento correto determinado (não chamar); P6 reserva 'observacional' às consultas cujo comportamento correto não é determinável. A consulta passa às métricas principais, na categoria F (fora do domínio). |
| N33 | anotação independente | o gabarito exigia project = Mapeamento Sistemático; o anotador anotou só state = São Paulo e listou project como leitura alternativa, pois 'cartografia sistemática' não é nome nem apelido informado na ferramenta | ampliado | As duas leituras são razoáveis (P3): a expressão designa o programa pelo termo distintivo do nome, mas não consta da descrição da ferramenta. project passa a campo opcional; a regra de project do manual passa a registrar o caso. |
| GF007 | anotação independente | ambos classificam a consulta como observacional; o gabarito indica 'não chamar' e o anotador, 'chamar sem parâmetros' | mantido | Consulta observacional (P6, valor impossível de representar): o comportamento é reportado, mas não pontuado, de modo que a divergência não afeta nenhuma métrica. Mantém-se a indicação 'não chamar', coerente com N38 (escala 1:10.000.000). |
| P14 | consistência | 'detalhado' é anotado como 1:25.000 em todo o dataset, mas P14 aceita 1:25.000 ou 1:50.000 | mantido | As escalas explícitas '(25k ou 50k)' prevalecem sobre o qualificativo 'detalhado' (regra de scale: duas escalas explícitas, aceita-se qualquer uma). |
| P13 | anotação independente (medida estrita) | leitura preferencial diferente dentro do conjunto aceito: scale 1:25.000 no gabarito, 1:50.000 no anotador (ambas aceitas por 'maior que 100k') | mantido | Na camada P, a anotação original da equipe do 1º CGEO é mantida como leitura preferencial (manual, seção “Rastreabilidade”); a escolha da preferencial não afeta a pontuação. |
| P21 | anotação independente (medida estrita) | leitura preferencial diferente dentro do conjunto aceito: sortField creationDate no gabarito, publicationDate no anotador (ambos aceitos, sem pista ligada à ordenação) | mantido | Na camada P, a anotação original da equipe do 1º CGEO é mantida como leitura preferencial (manual, seção “Rastreabilidade”); a escolha da preferencial não afeta a pontuação. |
| P22 | anotação independente (medida estrita) | leitura preferencial diferente dentro do conjunto aceito: sortField creationDate no gabarito, publicationDate no anotador (ambos aceitos, sem pista ligada à ordenação) | mantido | Na camada P, a anotação original da equipe do 1º CGEO é mantida como leitura preferencial (manual, seção “Rastreabilidade”); a escolha da preferencial não afeta a pontuação. |
| GO016 | anotação independente (medida estrita) | o gabarito aceita sortField publicationDate ou creationDate; o anotador aceitou só publicationDate | mantido | Em 'as cartas mais recentes publicadas entre 2022 e 2023', o verbo qualifica o filtro de período, não a ordenação; sem pista ligada à ordenação, aceitam-se os dois campos (regra de ordenação). É o mesmo raciocínio do anotador em P22. |

## 6. Revisão humana de amostra

Pendente: preencher a coluna 'concorda (S/N)' de `revisao_humana_amostra.csv` (amostra estratificada de 40 consultas, semente 42).
