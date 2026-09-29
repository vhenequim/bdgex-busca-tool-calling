---
tipo: orientacao-pfc
status: ativa
nome: tipo-so-quando-nomeado
titulo: productType só quando o tipo é nomeado
campos: [productType]
sempre: true
ciclo: 1
origem: 'lote 1, rodadas v1/v2 da T4: 606 execuções erradas com o gatilho e erro em productType (tc1 228, se1 29, tc2 266, se2 83)'
---
productType só quando a consulta nomeia o tipo: topográfica/topo, vetorial, ortoimagem/orto, banda P, banda X, MDT, MDS, CIRC, temática. 'cartas', 'mapas', 'folhas', 'produtos' e 'cartografia sistemática' sozinhos não definem tipo: sem productType.
