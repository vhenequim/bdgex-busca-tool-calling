"""Escreve as orientações do ciclo 1 (experimentos/orientacoes/md/). Ver docs/v3_desenvolvimento.md.

Cada orientação nasce de um padrão de erro observado nos conjuntos de DESENVOLVIMENTO (310 consultas e
lote 1). Os exemplos do corpo são genéricos, não consultas do lote. O campo `origem` é preenchido por
`experimentos/orientacoes/contar_origens.py` com as contagens de execuções afetadas.
"""

from __future__ import annotations

import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent / "md"

SIGLAS = r"\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b"

ORIENTACOES = [
    dict(nome="uf-por-extenso", titulo="Estado sempre por extenso", campos=["state"],
         gatilhos=[r"\bestado\b"], gatilhos_originais=[SIGLAS],
         corpo="O campo state leva o nome da UF por extenso, com acentos: AM → Amazonas, PA → Pará, DF → Distrito "
               "Federal, ES → Espírito Santo, MS → Mato Grosso do Sul. Nunca escreva a sigla nem 'sigla + nome'."),
    dict(nome="codigo-sem-prefixo", titulo="Código MI/INOM sem prefixo", campos=["keyword"],
         gatilhos=[r"\bmi\b", r"\binom\b", r"\b[ns][a-h] ?\d{2}", r"\bfolha \d"],
         corpo="keyword leva só o código, como escrito: 'MI 1234-5' → '1234-5'; 'folha MI-1234-5-NO' → '1234-5-NO'; "
               "INOM em maiúsculas e com hífens: 'sb20xa' → 'SB-20-X-A'. Não acrescente nem remova sufixos e não "
               "escreva 'MI', 'INOM', 'folha' ou 'carta' dentro de keyword."),
    dict(nome="limite-so-com-numero", titulo="limit só com número ou pedido no singular", campos=["limit"],
         gatilhos=[r"mais recente", r"mais antig", r"\bultim", r"\bprimeir", r"recentes", r"antigas", r"atualiza"],
         corpo="limit só entra quando a consulta diz quantos resultados quer ('as 5 mais antigas' → 5; 'três cartas' "
               "→ 3) ou pede UM resultado no singular ('a carta mais recente' → 1). Plural sem número ('as mais "
               "recentes', 'as últimas cartas', 'as edições mais novas') → não preencha limit."),
    dict(nome="tipo-so-quando-nomeado", titulo="productType só quando o tipo é nomeado", campos=["productType"],
         sempre=True,
         corpo="productType só quando a consulta nomeia o tipo: topográfica/topo, vetorial, ortoimagem/orto, banda P, "
               "banda X, MDT, MDS, CIRC, temática. 'cartas', 'mapas', 'folhas', 'produtos' e 'cartografia "
               "sistemática' sozinhos não definem tipo: sem productType."),
    dict(nome="municipio-inteiro", titulo="Município com o nome inteiro, sem deduzir o estado", campos=["city", "state"],
         gatilhos=[r"\b(?:do|da|de|dos|das) (?:norte|sul|leste|oeste|piaui|goias|tocantins|maranhao|para|parana|"
                   r"minas|bahia|amazonas|acre|sergipe)\b", r"\bcartas? de\b", r"\bmunicipio\b", r"\bcidade\b"],
         corpo="O nome do município vai inteiro em city, mesmo quando contém nome de estado ou ponto cardeal "
               "('São José do Rio Preto', 'Aparecida de Goiânia', 'Santana do Livramento'). state só entra se a "
               "consulta citar o estado à parte ('Campinas, SP' → city Campinas e state São Paulo). Nunca deduza o "
               "estado a partir do município."),
    dict(nome="regiao-nao-e-filtro", titulo="Região não é estado nem município", campos=["state", "city"],
         gatilhos=[r"nordeste", r"sudeste", r"\bnorte\b", r"\bsul\b", r"centro oeste", r"amazonia legal", r"litoral",
                   r"semiarido", r"sertao", r"pantanal", r"\bregiao\b", r"fronteira"],
         corpo="Regiões (Nordeste, Sul, Amazônia Legal, litoral, semiárido, Pantanal) não são estado nem município: "
               "não viram state nem city. Se a região for o único critério, busque sem filtros ou peça "
               "esclarecimento; se houver outro critério, busque só com ele."),
    dict(nome="projeto-nao-e-estado", titulo="Nome de projeto não é estado", campos=["project", "state"],
         gatilhos=[r"\bbcd\b", r"base cartografica digital"],
         corpo="'BCD da Bahia', 'Base Cartográfica Digital de Rondônia' e 'BCD do Amapá' são projetos: preencha "
               "project, e não state (o estado faz parte do nome do projeto)."),
    dict(nome="keyword-ou-city", titulo="Nome de carta × município", campos=["keyword", "city"],
         gatilhos=[r"\b(?:carta|folha) (?!(?:de|do|da|dos|das|em|na|no|mi|inom|topo\w*|vetor\w*|orto\w*|tematic\w*|"
                   r"mais|circ|mdt|mds|com|que|para|pra)\b)[a-z]"],
         corpo="Nome logo depois de 'carta' ou 'folha' ('carta Rio das Pedras', 'folha Serra Azul') é keyword, "
               "copiado como está escrito. 'cartas de X', com X município, é city. Não use keyword para palavras "
               "genéricas ('carta', 'folha') nem para o tipo de produto."),
    dict(nome="periodo-intervalo-inteiro", titulo="Período como intervalo completo", campos=["publicationPeriod",
                                                                                          "creationPeriod"],
         gatilhos=[r"\b(?:19|20)\d{2}\b", r"\bano\b", r"\bmes\b", r"\bsemana\b", r"\bhoje\b", r"trimestre",
                   r"semestre", r"\bultimos\b", r"\bdesde\b", r"\bdepois\b", r"\bantes\b", r"\bapos\b"],
         corpo="Período é um intervalo completo resolvido com a data atual: 'este ano' → de 1º de janeiro a 31 de "
               "dezembro; 'no ano passado' → o ano anterior inteiro; 'últimos 6 meses' → de 6 meses atrás até hoje; "
               "'desde 2015' → start 2015-01-01 e end hoje; 'em 2008' → 2008-01-01 a 2008-12-31; 'antes de 2010' → "
               "só end, 2009-12-31. Verbo de publicação (publicada, lançada) ou nenhum verbo → publicationPeriod; "
               "criada, feita, elaborada, produzida → creationPeriod."),
    dict(nome="esclarecer-so-sem-criterio", titulo="Esclarecimento só sem nenhum critério", campos=[], sempre=True,
         corpo="Não peça esclarecimento quando a consulta tiver algum critério (lugar, escala, tipo, código, data, "
               "projeto ou CGEO): busque com ele. 'cartas do 2º CGEO' ou 'ortoimagens de Goiás' já são buscas "
               "completas. Só uma consulta sem nenhum critério ('quero ver as cartas do acervo') admite pergunta."),
    dict(nome="ordenacao-so-quando-pedida", titulo="Ordenação só quando pedida", campos=["sortField", "sortDirection"],
         gatilhos=[r"mais recente", r"mais antig", r"\bultim", r"\bprimeir", r"recentes", r"antigas", r"ordem",
                   r"cronolog", r"mais nov", r"atualiza"],
         corpo="sortField e sortDirection só quando a consulta pede ordem ou posição. 'mais recente(s)', 'últimas', "
               "'mais novas' → DESC; 'mais antiga(s)', 'primeiras', 'ordem cronológica' → ASC. sortField = "
               "creationDate se a pista for criação ou atualização ('criadas mais recentemente', 'última "
               "atualização'); senão publicationDate."),
    dict(nome="escala-qualitativa", titulo="Escalas descritas em palavras", campos=["scale"],
         gatilhos=[r"grande escala", r"escala grande", r"media escala", r"escala media", r"pequena escala",
                   r"escala pequena", r"detalhad", r"maior que"],
         corpo="'grande escala' → uma escala de 1:25.000 a 1:1.000 (use 1:25.000); 'média escala' → 1:50.000 ou "
               "1:100.000 (use 1:50.000); 'pequena escala' → 1:250.000; 'detalhada' → 1:25.000; 'maior que 100k' → "
               "1:50.000 ou maior. A escala sempre com ponto de milhar: 1:2.000, 1:25.000."),
    dict(nome="cartografia-sistematica", titulo="Mapeamento Sistemático", campos=["project", "productType"],
         gatilhos=[r"cartografia sistematica", r"mapeamento sistematico"],
         corpo="'cartografia sistemática' e 'mapeamento sistemático' referem-se ao projeto Mapeamento Sistemático "
               "(project), não a um tipo de produto: não preencha productType por causa delas."),
]


def main() -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    for o in ORIENTACOES:
        linhas = ["---", "tipo: orientacao-pfc", "status: ativa", f"nome: {o['nome']}", f"titulo: {o['titulo']}",
                  f"campos: [{', '.join(o['campos'])}]"]
        for chave in ("gatilhos", "gatilhos_originais"):
            if o.get(chave):
                linhas.append(f"{chave}:")
                linhas += [f"  - '{g}'" for g in o[chave]]
        linhas += [f"sempre: {'true' if o.get('sempre') else 'false'}", "ciclo: 1", "origem: 'a contar'", "---",
                   o["corpo"], ""]
        destino = DIR / f"{o['nome']}.md"
        if destino.exists() and "--forcar" not in sys.argv:
            continue   # as revisões dos ciclos seguintes são feitas nos arquivos (docs/orientacoes_ciclos.md)
        destino.write_text("\n".join(linhas), encoding="utf-8", newline="\n")
    print(f"{len(ORIENTACOES)} orientações em {DIR}")


if __name__ == "__main__":
    main()
