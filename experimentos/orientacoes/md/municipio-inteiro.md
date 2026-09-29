---
tipo: orientacao-pfc
status: ativa
nome: municipio-inteiro
titulo: Município com o nome inteiro, sem deduzir o estado
campos: [city, state]
gatilhos:
  - '\b(?:do|da|de|dos|das) (?:norte|sul|leste|oeste|piaui|goias|tocantins|maranhao|para|parana|minas|bahia|amazonas|acre|sergipe)\b'
  - '\bcartas? de\b'
  - '\bmunicipio\b'
  - '\bcidade\b'
sempre: false
ciclo: 1
origem: 'lote 1, rodadas v1/v2 da T4: 326 execuções erradas com o gatilho e erro em city, state (tc1 82, se1 55, tc2 78, se2 111)'
---
O nome do município vai inteiro em city, mesmo quando contém nome de estado ou ponto cardeal ('São José do Rio Preto', 'Aparecida de Goiânia', 'Santana do Livramento'). state só entra se a consulta citar o estado à parte ('Campinas, SP' → city Campinas e state São Paulo). Nunca deduza o estado a partir do município.
