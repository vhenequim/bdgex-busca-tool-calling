# Auditoria do dataset de avaliação

Dataset: `data/dataset.json` (sha256 `c2a9e293f818c20b…`), 310 consultas.

## 1. Estrutura

Nenhum problema estrutural.

## 2. Consistência entre casos



- **detalhad** → `scale` (resolvido por exceção justificada): {"$um_de": ["1:25.000", "1:50.000"]} em P14; "1:25.000" em P21, GC018, GA018
  - P14: as escalas explícitas '(25k ou 50k)' prevalecem sobre o qualificativo 'detalhado'

## 3. Evidência (anotador por regras × gabarito)

310 de 310 consultas sem apontamento. Apontamentos por tipo:


| ID | Consulta | Gabarito | Apontamentos |
|---|---|---|---|
