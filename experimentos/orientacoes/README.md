# Experimento descartado: orientações aprendidas com erros

Durante o desenvolvimento da v3 (docs/v3_desenvolvimento.md) foi testada uma "memória de lições": regras
curtas escritas pelos autores a partir dos erros nos conjuntos de desenvolvimento, uma por arquivo markdown
(`md/`), com um frontmatter YAML que dizia o tipo do arquivo (só `tipo: orientacao-pfc` era carregado), os
campos a que a regra se referia, os gatilhos (expressões regulares sobre a consulta) e a origem (o padrão de
erro que a motivou, contado por `contar_origens.py`). A regra entrava no prompt só quando um gatilho casava
com a consulta.

**Resultado no desenvolvimento (ciclo 2, 160 consultas do lote 1):** a mesma configuração com e sem as
orientações acertou 155 de 160 nos dois casos (4 × 4 consultas discordantes, McNemar p = 1,0), e a primeira
decisão do modelo foi melhor sem elas (85,6% × 82,5%). O ganho da v3 vinha do retorno do validador.

**Por que foi retirado:** não acrescentou nada mensurável e era a parte do desenho mais exposta a sobreajuste
— regras escritas em rodadas sobre os erros das mesmas consultas em que eram avaliadas. A v3 testada no lote 2
não tem orientações, nem no Tool Calling nem no controle de Saída Estruturada.

Conteúdo: `orientacoes.py` (carregador), `md/` (as 15 orientações do ciclo 2), `escrever_orientacoes_ciclo1.py`
(as 13 do ciclo 1) e `contar_origens.py`. O código não é importado pelo pacote `pfc_busca`.
