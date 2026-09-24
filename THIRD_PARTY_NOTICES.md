# Avisos de terceiros

## Protótipo de busca do 1º Centro de Geoinformação

Partes deste repositório derivam do protótipo
[`1cgeo/prototipo_busca_llm`](https://github.com/1cgeo/prototipo_busca_llm):

- `db/init_schema_prototipo.sql` — esquema do banco do protótipo (`postgres/init.sql`);
- as 22 consultas da camada P do *dataset* (`src/pfc_busca/evaluation/manual_cases.py`
  e `data/dataset.json`, IDs P01–P22), extraídas de `backend/evaluation/test-cases.ts`,
  com a anotação original mantida como leitura preferencial;
- a lógica das consultas SQL de `src/pfc_busca/tools.py`, portada de `backend/src/services/search.ts`.

Esse material é distribuído sob a licença abaixo.

```
MIT License
Copyright (c) 2025 Exército Brasileiro - Diretoria de Serviço Geográfico
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## abnTeX2

`texto/abntex2.cls`, `texto/abntex2cite.sty` e `texto/abntex2ime.sty` são do
[abnTeX2](https://www.abntex.net.br/) e da sua customização para o IME, distribuídos sob a
LaTeX Project Public License (LPPL), versão 1.3 ou posterior, conforme o cabeçalho de cada
arquivo.
