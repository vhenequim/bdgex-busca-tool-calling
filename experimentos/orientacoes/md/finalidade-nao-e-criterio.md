---
tipo: orientacao-pfc
status: ativa
nome: finalidade-nao-e-criterio
titulo: A finalidade declarada não é critério
campos: []
gatilhos:
  - '\b(?:para|pra|pro) (?:(?:uma|um|a|o|as|os|nossa|nosso|minha|meu) )?(?:obra|trabalho|prefeitura|pesquisa|estudo|equipe|levantamento|facul|faculdade|escola|aula|tese|tcc|artigo|relatorio|analise|uso|apoio|planejamento|projeto de)\b'
  - '\bpara uso\b'
  - '\be (?:pra|para) (?:um|uma|o|a)\b'
sempre: false
ciclo: 2
origem: 'ciclo 1 de desenvolvimento, tc3 nas 160 consultas: 2 execuções erradas com o gatilho e não buscou no domínio (tc3 2)'
---
Quando a consulta diz para que o usuário quer o material (uma obra, um trabalho da faculdade, a prefeitura, uma pesquisa, a equipe de campo), essa parte não é filtro nem muda o que se busca: busque pelos critérios de acervo que a consulta cita (lugar, tipo de produto, escala, código, data) e deixe a finalidade de lado.
