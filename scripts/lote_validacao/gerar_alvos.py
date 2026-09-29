"""Sorteia os ALVOS do lote de validação independente (etapa 1 da redação controlada).

    python scripts/lote_validacao/gerar_alvos.py      # grava data/lote_validacao/alvos.json

Cada alvo especifica, antes de existir a consulta:
  - o gabarito (`esperado`, `trocas`, `espera_tool_call`, `aceita_nao_chamar`), montado pelas
    regras de `docs/manual_de_anotacao.md` a partir dos parâmetros sorteados;
  - as instruções ao redator (`pedido`, `proibido`): o que a consulta precisa dizer, com a forma
    de superfície de cada valor (sigla, apelido de escala, grafia sem acento...), as pistas que
    decidem o campo (verbo de publicação ou de criação, pista da ordenação) e o que ela não pode
    dizer;
  - o registro de linguagem (formal, coloquial, pergunta, telegráfico...).

Os valores vêm de catálogos reais sempre que possível: nomes de folha, códigos MI/INOM, escalas,
tipos e CGEOs dos metadados públicos do BDGEx (`catalogo.carregar_bdgex`) e municípios da lista
oficial do IBGE (`catalogo.carregar_ibge`); os enumerados, do schema da ferramenta. Um único
gerador pseudoaleatório, com semente fixa, é consumido em ordem fixa.
"""

from __future__ import annotations

import importlib.util
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalogo  # noqa: E402

_spec = importlib.util.spec_from_file_location("gerador_g", RAIZ / "scripts" / "generate_dataset_paper.py")
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)

import config_lote  # noqa: E402

SEMENTE = config_lote.SEMENTES["alvos"]
DESTINO = config_lote.DIR / "alvos.json"
UM_DE, OPCIONAL = "$um_de", "$opcional"

# VS simples · VC compostas · VM códigos · VT tempo · VO ordenação · VA leituras múltiplas/ambíguas
# VE subespecificadas · VF fora do domínio
CONTAGENS_LOTE_1 = {"VS": 280, "VC": 360, "VM": 160, "VT": 260, "VO": 200, "VA": 200, "VE": 150, "VF": 340}
CONTAGENS = {f: round(n * config_lote.FATOR) for f, n in CONTAGENS_LOTE_1.items()}

# ---------------------------------------------------------------------------
# Registros de linguagem (distribuição das consultas no domínio)
# ---------------------------------------------------------------------------
REGISTROS = {
    "formal": ("frase completa e cortês, como num pedido por escrito a um setor técnico", 15),
    "direto": ("pedido curto e direto, como numa caixa de busca", 20),
    "coloquial": ("linguagem falada do dia a dia, com expressões informais ('tem aí', 'queria ver', 'me passa')", 15),
    "pergunta": ("pergunta ao sistema ('vocês têm...?', 'existe alguma...?', 'onde encontro...?')", 15),
    "telegrafico": ("só termos-chave, sem verbos nem artigos, como anotação rápida", 10),
    "sem_acento": ("tudo em minúsculas e sem acentos, como quem digita rápido no celular", 10),
    "erro_digitacao": ("com UM erro de digitação leve numa palavra comum (nunca num nome, código, número ou "
                       "expressão de tempo)", 5),
    "contexto": ("frase mais longa, que explica o uso ('estou planejando um trabalho de campo e...', "
                 "'para um relatório preciso de...'), sem acrescentar critérios de busca", 10),
}
REGISTROS_INFORMAIS = {"telegrafico", "sem_acento", "erro_digitacao"}

# Quem escreve (só o tom e o vocabulário; a persona nunca acrescenta critério de busca)
PERSONAS = [
    "oficial do Exército planejando uma operação", "analista de um Centro de Geoinformação",
    "pesquisador de universidade", "estudante de graduação em geografia", "técnico de prefeitura",
    "engenheiro civil de uma construtora", "servidor de órgão ambiental", "professor do ensino médio",
    "cidadão sem conhecimento técnico", "sargento topógrafo", "geólogo de campo", "agente da defesa civil",
]

# ---------------------------------------------------------------------------
# Superfícies (formas de dizer cada valor) — todas previstas no manual ou na descrição da ferramenta
# ---------------------------------------------------------------------------
ESCALA_FORMAS = {
    "1:1.000": [("1:1.000", False), ("1:1000", False)],
    "1:2.000": [("1:2.000", False), ("1:2000", False)],
    "1:5.000": [("1:5.000", False), ("1:5000", False)],
    "1:10.000": [("1:10.000", False), ("1:10000", False), ("10 mil", True)],
    "1:25.000": [("1:25.000", False), ("1:25000", False), ("25k", True), ("25 mil", True), ("escala detalhada", True)],
    "1:50.000": [("1:50.000", False), ("1:50000", False), ("50k", True), ("50 mil", True)],
    "1:100.000": [("1:100.000", False), ("1:100000", False), ("100k", True), ("100 mil", True)],
    "1:250.000": [("1:250.000", False), ("1:250000", False), ("250k", True), ("250 mil", True), ("pequena escala", True)],
}
TIPO_FORMAS = {
    "SCN Carta Topográfica Matricial": [("cartas topográficas", False), ("carta topográfica", False), ("cartas topo", True), ("topográficas", False)],
    "SCN Carta Topográfica Vetorial": [("cartas topográficas vetoriais", False), ("cartas vetoriais", False), ("dados vetoriais", False)],
    "SCN Carta Ortoimagem": [("ortoimagens", False), ("cartas ortoimagem", False), ("ortos", True), ("ortoimg", True)],
    "SCN Carta Ortoimagem Banda P Pol HH": [("ortoimagens banda P HH", False), ("ortoimagem banda P polarização HH", False)],
    "SCN Carta Ortoimagem Banda X Pol HH": [("ortoimagens banda X HH", False), ("ortoimagem banda X polarização HH", False)],
    "MDT — RAM": [("MDTs", True), ("modelos digitais de terreno", False), ("MDT", True)],
    "MDS — RAM": [("MDSs", True), ("modelos digitais de superfície", False), ("MDS", True)],
    "CIRC": [("cartas CIRC", False), ("CIRC", False)],
    "Cartas Temáticas Não SCN": [("cartas temáticas", False), ("mapas temáticos", False)],
}
# peso do tipo no sorteio: os 4 tipos que aparecem no catálogo público pesam mais; os demais
# entram para que o F1 de productType cubra todo o enumerado
PESO_TIPO = {"SCN Carta Topográfica Matricial": 6, "SCN Carta Topográfica Vetorial": 4, "SCN Carta Ortoimagem": 5,
             "MDS — RAM": 3, "MDT — RAM": 2, "SCN Carta Ortoimagem Banda P Pol HH": 1,
             "SCN Carta Ortoimagem Banda X Pol HH": 1, "CIRC": 1, "Cartas Temáticas Não SCN": 2}
CGEO_FORMAS = [("{n}º CGEO", False), ("{n}o cgeo", True), ("{ord} cgeo", True), ("{n}º Centro de Geoinformação", False),
               ("{ord} Centro de Geoinformação", False)]
ORDINAIS = {"1": "primeiro", "2": "segundo", "3": "terceiro", "4": "quarto", "5": "quinto"}
PROJETO_FORMAS = {canon: [(a, a.lower() == a) for a in apelidos] for canon, apelidos in G.PROJETOS}

# expressões de tempo: (regra ou período absoluto, superfícies aceitas pela regra)
NUMEROS = {2: "dois", 3: "três", 4: "quatro", 5: "cinco", 6: "seis", 7: "sete", 10: "dez", 15: "quinze", 30: "trinta"}


def _tempos(rng: random.Random, anos_reais: list[int]) -> tuple[dict, list[str], str]:
    """Sorteia uma expressão de tempo: (período do gabarito, superfícies permitidas, rótulo)."""
    tipo = rng.choices(["fixa", "meses", "anos", "dias", "desde", "depois", "antes", "em", "entre"],
                       weights=[30, 10, 7, 5, 9, 9, 8, 14, 8])[0]
    if tipo == "fixa":
        regra, sup = rng.choice([
            ("ano_corrente", ["este ano", "esse ano", "deste ano", "neste ano"]),
            ("ano_anterior", ["no ano passado", "do ano passado"]),
            ("dois_anos_atras", ["2 anos atrás", "dois anos atrás"]),
            ("mes_anterior", ["no mês passado", "do mês passado"]),
            ("mes_corrente", ["este mês", "deste mês", "neste mês"]),
            ("semana_passada", ["na semana passada", "da semana passada"]),
            ("semana_corrente", ["esta semana", "nesta semana", "desta semana"]),
            ("hoje", ["hoje", "de hoje"]),
            ("primeiro_trimestre_corrente", ["no primeiro trimestre deste ano", "no 1º trimestre deste ano"]),
            ("segundo_semestre_anterior", ["no segundo semestre do ano passado"]),
            ("ultimo_trimestre_ano_anterior", ["no último trimestre do ano passado"]),
            ("trimestre_anterior", ["no trimestre passado"]),
        ])
        return {"rel": regra}, sup, regra
    if tipo == "meses":
        n = rng.choice([2, 3, 4, 6])
        sup = [f"nos últimos {n} meses", f"dos últimos {n} meses", f"nos últimos {NUMEROS[n]} meses"]
        return {"rel": f"ultimos_{n}_meses"}, sup, f"ultimos_{n}_meses"
    if tipo == "anos":
        n = rng.choice([2, 3, 5, 10])
        sup = [f"nos últimos {n} anos", f"dos últimos {n} anos", f"nos últimos {NUMEROS[n]} anos"]
        return {"rel": f"ultimos_{n}_anos"}, sup, f"ultimos_{n}_anos"
    if tipo == "dias":
        n = rng.choice([7, 15, 30])
        sup = [f"nos últimos {n} dias", f"nos últimos {NUMEROS[n]} dias"]
        return {"rel": f"ultimos_{n}_dias"}, sup, f"ultimos_{n}_dias"
    ano = rng.choice([a for a in anos_reais if 1990 <= a <= 2025])
    if tipo == "desde":
        return {"rel": f"desde_{ano}"}, [f"desde {ano}", f"a partir de {ano}"], f"desde_{ano}"
    if tipo == "depois":
        return {"rel": f"depois_de_{ano}"}, [f"depois de {ano}", f"após {ano}"], f"depois_de_{ano}"
    if tipo == "antes":
        return {"rel": f"antes_de_{ano}"}, [f"antes de {ano}", f"anteriores a {ano}"], f"antes_de_{ano}"
    if tipo == "em":
        return {"start": f"{ano}-01-01", "end": f"{ano}-12-31"}, [f"em {ano}", f"de {ano}", f"no ano de {ano}"], f"ano_{ano}"
    fim = min(2025, ano + rng.choice([1, 2, 3, 5]))
    return ({"start": f"{ano}-01-01", "end": f"{fim}-12-31"},
            [f"entre {ano} e {fim}", f"de {ano} a {fim}"], f"entre_{ano}_{fim}")


# ---------------------------------------------------------------------------
# Construção dos alvos
# ---------------------------------------------------------------------------

class Alvo:
    def __init__(self, familia: str):
        self.familia = familia
        self.esperado: dict = {}
        self.trocas: list[list[str]] = []
        self.pedido: list[str] = []
        self.proibido: list[str] = []
        self.categorias: set[str] = set()
        self.espera_tool_call = True
        self.aceita_nao_chamar = False
        self.subtipo: str | None = None
        self.informal = False
        self.notas: list[str] = []
        self.descricao: list[str] = []
        # trechos que a consulta redigida PRECISA conter (checagem automática; cada item é uma lista de
        # alternativas, comparadas sem acento e sem caixa)
        self.superficies: list[list[str]] = []
        self.verbo: str | None = None   # publicacao | criacao | nenhum (checagem do verbo do período)

    def exige(self, *alternativas: str):
        self.superficies.append([x for x in alternativas if x])

    def campo(self, nome: str, valor, instrucao: str, informal: bool = False, nota: str | None = None):
        self.esperado[nome] = valor
        self.pedido.append(instrucao)
        self.informal |= informal
        self.descricao.append(nome)
        if nota:
            self.notas.append(nota)


class Gerador:
    def __init__(self, semente: int = SEMENTE):
        self.rng = random.Random(semente)
        self.bdgex = catalogo.carregar_bdgex()
        self.ibge = catalogo.carregar_ibge()
        nomes_estado = {catalogo.normalizar(e[0]) for e in G.ESTADOS}
        self.municipios_por_nome: dict[str, list[dict]] = {}
        for m in self.ibge:
            self.municipios_por_nome.setdefault(catalogo.normalizar(m["nome"]), []).append(m)
        # municípios aproveitáveis como `city`: nome sem coincidência com UF (manual: só SP/RJ são ambíguos)
        self.municipios = [m for m in self.ibge if catalogo.normalizar(m["nome"]) not in nomes_estado
                           and len(m["nome"]) > 3]
        folhas = Counter(r["nome_folha"] for r in self.bdgex if r["nome_folha"])
        self.folhas_distintivas = sorted(n for n in folhas if catalogo.normalizar(n) not in self.municipios_por_nome
                                         and len(n.split()) >= 2 and not catalogo.normalizar(n).startswith(("folha", "carta")))
        self.folhas_municipio = sorted(n for n in folhas if catalogo.normalizar(n) in self.municipios_por_nome
                                       and catalogo.normalizar(n) not in nomes_estado)
        self.registros_codigo = [r for r in self.bdgex if r["mi"] and r["inom"] and r["escala"]]
        self.anos_reais = [r["ano"] for r in self.bdgex if r["ano"]]
        self.escalas_reais = [r["escala"] for r in self.bdgex if r["escala"]]
        self.cgeos_reais = [r["cgeo"] for r in self.bdgex if r["cgeo"]]
        self.vistos: set[str] = set()

    # -- sorteios elementares ------------------------------------------------
    def registro(self) -> str:
        nomes = list(REGISTROS)
        return self.rng.choices(nomes, weights=[REGISTROS[n][1] for n in nomes])[0]

    def escala(self, real: str | None = None) -> str:
        if real:
            return real
        # 80% pela distribuição real do acervo, 20% uniforme sobre o enumerado (cobertura)
        if self.rng.random() < 0.8:
            return self.rng.choice(self.escalas_reais)
        return self.rng.choice(list(ESCALA_FORMAS))

    def tipo(self) -> str:
        tipos = list(PESO_TIPO)
        return self.rng.choices(tipos, weights=[PESO_TIPO[t] for t in tipos])[0]

    def cgeo(self, real: str | None = None) -> str:
        return real or self.rng.choice(self.cgeos_reais)

    # -- componentes -------------------------------------------------------------
    def c_estado(self, a: Alvo, permitir_ambiguo: bool = False):
        nome, apelidos, prep, _loc = self.rng.choice(G.ESTADOS)
        sigla = next((x for x in apelidos if x.isupper()), None)
        formas = ["nome", "nome", "sigla"] if sigla else ["nome"]
        forma = self.rng.choice(formas)
        if nome in G.ESTADO_OU_CAPITAL:
            if permitir_ambiguo:
                a.campo("state", nome, f'o lugar "{nome}", escrito só como "{nome}", SEM as palavras "estado", "cidade" '
                        f'ou "município" e sem sigla', nota=f"'{nome}' sem qualificador: estado ou capital (manual, state/city)")
                a.trocas.append(["state", "city"])
                a.categorias.add("A")
                a.exige(nome)
                return
            forma = "sigla" if self.rng.random() < 0.5 else "qualificado"
        if forma == "sigla":
            a.campo("state", nome, f'o estado de {nome}, escrito como a sigla "{sigla}"', informal=True)
            a.exige(sigla)
        elif forma == "qualificado":
            a.campo("state", nome, f'o estado de {nome}, escrito com a palavra "estado" (ex.: "estado {prep} {nome}")')
            a.exige(nome)
            a.exige("estado")
        else:
            a.campo("state", nome, f"o estado {prep} {nome} (escreva o nome do estado por extenso)")
            a.exige(nome)

    def c_municipio(self, a: Alvo, com_uf: bool = False):
        m = self.rng.choice(self.municipios)
        if com_uf:
            a.campo("city", m["nome"], f'o município de {m["nome"]}, seguido da sigla do estado "{m["sigla"]}" '
                    f'(ex.: "{m["nome"]}, {m["sigla"]}" ou "{m["nome"]} ({m["sigla"]})")')
            a.esperado["state"] = m["uf"]
            a.descricao.append("state")
            a.informal = True
            a.exige(m["sigla"])
        else:
            a.campo("city", m["nome"], f'o município de {m["nome"]} (escreva só o nome do município, sem o estado)')
        a.exige(m["nome"])

    def c_escala(self, a: Alvo, real: str | None = None):
        canon = self.escala(real)
        forma, informal = self.rng.choice(ESCALA_FORMAS[canon])
        a.campo("scale", canon, f'na escala {canon}, escrita como "{forma}"', informal=informal)
        a.exige(forma)

    def c_tipo(self, a: Alvo, canon: str | None = None):
        canon = canon or self.tipo()
        forma, informal = self.rng.choice(TIPO_FORMAS[canon])
        a.campo("productType", canon, f'produtos do tipo "{canon}", escrito como "{forma}"', informal=informal)
        a.exige(forma)

    def c_cgeo(self, a: Alvo, real: str | None = None):
        canon = self.cgeo(real)
        n = canon[0]
        molde, informal = self.rng.choice(CGEO_FORMAS)
        forma = molde.format(n=n, ord=ORDINAIS[n])
        a.campo("supplyArea", canon, f'do {canon}, escrito como "{forma}" (use "do/da", sem verbo como "produzido")',
                informal=informal)
        a.exige("cgeo", "centro de geoinformacao")
        a.exige(n, f"{n}o", ORDINAIS[n])

    def c_projeto(self, a: Alvo):
        canon = self.rng.choice([p[0] for p in G.PROJETOS])
        forma, informal = self.rng.choice(PROJETO_FORMAS[canon])
        a.campo("project", canon, f'do projeto "{canon}", escrito como "{forma}"', informal=informal)
        a.exige(forma)

    def c_folha(self, a: Alvo, nome: str | None = None, municipio: bool = False):
        nome = nome or self.rng.choice(self.folhas_distintivas)
        palavra = self.rng.choice(["carta", "folha"])
        a.campo("keyword", nome, f'a {palavra} chamada "{nome}" (escreva "{palavra}" antes do nome)')
        a.exige(nome)
        a.exige(palavra)
        if municipio:
            a.trocas.append(["keyword", "city"])
            a.notas.append("nome da folha coincide com o de um município: aceita-se city (manual, keyword)")
            a.categorias.add("A")

    def c_mi(self, a: Alvo, r: dict):
        codigo = r["mi"]
        forma = self.rng.choice([f"MI {codigo}", f"folha {codigo}", f"carta MI {codigo}", f"MI-{codigo}", f"folha MI {codigo}"])
        a.campo("keyword", codigo, f'o código MI {codigo}, escrito como "{forma}"')
        a.exige(codigo)
        a.categorias.add("M")

    def c_inom(self, a: Alvo, r: dict):
        codigo = r["inom"]
        if self.rng.random() < 0.2:
            forma = codigo.replace("-", "").lower()
            a.campo("keyword", codigo, f'o código INOM {codigo}, escrito compacto e em minúsculas: "{forma}"', informal=True)
            a.exige(forma)
        else:
            forma = self.rng.choice([codigo, f"INOM {codigo}", f"folha {codigo}"])
            a.campo("keyword", codigo, f'o código INOM {codigo}, escrito como "{forma}"')
            a.exige(codigo)
        a.categorias.add("M")

    def c_periodo(self, a: Alvo, verbo: str | None = None):
        periodo, superficies, rotulo = _tempos(self.rng, self.anos_reais)
        verbo = verbo or self.rng.choices(["publicacao", "criacao", "nenhum"], weights=[45, 25, 30])[0]
        sup = self.rng.choice(superficies)
        a.verbo = verbo
        for numero in re.findall(r"\d+", sup):
            a.exige(numero, *(nome for n, nome in NUMEROS.items() if str(n) == numero))
        if verbo == "publicacao":
            a.campo("publicationPeriod", periodo, f'com período de PUBLICAÇÃO dado pela expressão "{sup}", ligada a um verbo '
                    f'de publicação (publicada/publicado/publicadas/lançada)')
        elif verbo == "criacao":
            a.campo("creationPeriod", periodo, f'com período de CRIAÇÃO dado pela expressão "{sup}", ligada a um verbo de '
                    f'criação (criada/feita/elaborada/produzida)')
        else:
            a.campo("publicationPeriod", periodo, f'com a expressão de tempo "{sup}" SEM nenhum verbo de publicação ou de '
                    f'criação (ex.: "cartas {sup}"), de modo que não se saiba se é data de publicação ou de criação')
            a.trocas.append(["publicationPeriod", "creationPeriod"])
            a.notas.append("período sem verbo que desempate: publicação ou criação (manual, períodos)")
        a.categorias.add("T")
        a.descricao.append(rotulo)

    def c_ordenacao(self, a: Alvo):
        direcao = self.rng.choice(["DESC", "ASC"])
        pista = self.rng.choices(["nenhuma", "publicacao", "criacao"], weights=[45, 30, 25])[0]
        limite = self.rng.choices(["numero", "singular", "plural"], weights=[45, 25, 30])[0]
        n = self.rng.choice([2, 3, 4, 5, 10])
        sentido = "as mais recentes/últimas" if direcao == "DESC" else "as mais antigas/primeiras"
        if limite == "numero":
            escrita = str(n) if self.rng.random() < 0.6 else NUMEROS.get(n, str(n))
            q = f'exatamente {n} resultados (escreva o número como "{escrita}")'
            a.esperado["limit"] = n
            a.exige(str(n), NUMEROS.get(n, ""))
        elif limite == "singular":
            q = "UM só resultado, no singular e sem número (ex.: \"a carta mais recente\", \"a mais antiga\")"
            a.esperado["limit"] = {OPCIONAL: 1}
            a.notas.append("singular sem número: limit 1 opcional (manual, limite)")
        else:
            q = "vários resultados, no plural e SEM dizer quantos"
        if pista == "publicacao":
            campo = "publicationDate"
            p = 'a ordem deve ser explicitamente pela data de PUBLICAÇÃO (ex.: "últimas publicadas", "em ordem de publicação")'
        elif pista == "criacao":
            campo = "creationDate"
            p = ('a ordem deve ser explicitamente pela data de CRIAÇÃO ou ATUALIZAÇÃO (ex.: "criadas mais recentemente", '
                 '"última atualização", "primeiro mapeamento feito")')
        else:
            campo = {UM_DE: ["publicationDate", "creationDate"]}
            p = 'a ordem NÃO pode dizer se é por publicação ou por criação (ex.: "as mais recentes", "as 3 mais antigas")'
            a.notas.append("ordenação sem pista: publicationDate ou creationDate (manual, campo de ordenação)")
        a.esperado["sortField"] = campo
        a.esperado["sortDirection"] = direcao
        a.pedido.append(f"ordenadas por data, {sentido} ({'decrescente' if direcao == 'DESC' else 'crescente'}); {p}; {q}")
        a.descricao += ["sortField", "sortDirection"] + (["limit"] if limite != "plural" else [])
        a.categorias.add("O")

    # -- famílias ------------------------------------------------------------------
    def familia(self, fam: str, i: int) -> Alvo:
        a = Alvo(fam)
        rng = self.rng
        if fam == "VS":
            escolha = rng.choices(["estado", "municipio", "cgeo", "projeto", "folha", "mi", "inom", "tipo", "escala"],
                                  weights=[18, 17, 9, 8, 11, 10, 10, 11, 6])[0]
            r = rng.choice(self.registros_codigo)
            {"estado": lambda: self.c_estado(a), "municipio": lambda: self.c_municipio(a),
             "cgeo": lambda: self.c_cgeo(a), "projeto": lambda: self.c_projeto(a), "folha": lambda: self.c_folha(a),
             "mi": lambda: self.c_mi(a, r), "inom": lambda: self.c_inom(a, r), "tipo": lambda: self.c_tipo(a),
             "escala": lambda: self.c_escala(a)}[escolha]()
        elif fam == "VC":
            r = rng.choice([x for x in self.registros_codigo if x["tipo"]]) if rng.random() < 0.5 else None
            opcoes = ["local", "escala", "tipo", "cgeo", "projeto", "folha"]
            k = rng.choices([2, 3, 4], weights=[50, 35, 15])[0]
            escolhidos = rng.sample(opcoes, k)
            if "folha" in escolhidos and "local" in escolhidos and rng.random() < 0.5:
                escolhidos.remove("local")
            for c in escolhidos:
                if c == "local":
                    rng.choice([lambda: self.c_estado(a), lambda: self.c_municipio(a), lambda: self.c_municipio(a, com_uf=True)])()
                elif c == "escala":
                    self.c_escala(a, r["escala"] if r else None)
                elif c == "tipo":
                    self.c_tipo(a, r["tipo"] if r and rng.random() < 0.7 else None)
                elif c == "cgeo":
                    self.c_cgeo(a, r["cgeo"] if r else None)
                elif c == "projeto":
                    self.c_projeto(a)
                else:
                    self.c_folha(a, r["nome_folha"] if r and r["nome_folha"] and
                                 catalogo.normalizar(r["nome_folha"]) not in self.municipios_por_nome else None)
        elif fam == "VM":
            r = rng.choice(self.registros_codigo)
            (self.c_mi if rng.random() < 0.5 else self.c_inom)(a, r)
            extras = rng.sample(["escala", "tipo", "cgeo", "estado"], rng.choice([0, 1, 1, 2]))
            for c in extras:
                {"escala": lambda: self.c_escala(a, r["escala"]), "tipo": lambda: self.c_tipo(a, r["tipo"] if r["tipo"] else None),
                 "cgeo": lambda: self.c_cgeo(a, r["cgeo"]), "estado": lambda: self.c_estado(a)}[c]()
        elif fam == "VT":
            self.c_periodo(a)
            for c in rng.sample(["local", "escala", "tipo", "cgeo"], rng.choice([0, 1, 1, 2])):
                {"local": lambda: rng.choice([lambda: self.c_estado(a), lambda: self.c_municipio(a)])(),
                 "escala": lambda: self.c_escala(a), "tipo": lambda: self.c_tipo(a), "cgeo": lambda: self.c_cgeo(a)}[c]()
        elif fam == "VO":
            self.c_ordenacao(a)
            for c in rng.sample(["local", "escala", "tipo", "cgeo", "mi"], rng.choice([0, 1, 1, 2])):
                if c == "mi":
                    self.c_mi(a, rng.choice(self.registros_codigo))
                else:
                    {"local": lambda: rng.choice([lambda: self.c_estado(a), lambda: self.c_municipio(a)])(),
                     "escala": lambda: self.c_escala(a), "tipo": lambda: self.c_tipo(a), "cgeo": lambda: self.c_cgeo(a)}[c]()
        elif fam == "VA":
            self._ambigua(a)
        elif fam == "VE":
            self._subespecificada(a)
        elif fam == "VF":
            self._fora(a)
        return a

    def _ambigua(self, a: Alvo):
        rng = self.rng
        tipo = rng.choices(["estado_ou_capital", "escala_qualitativa", "duas_escalas", "dois_codigos",
                            "projeto_termo", "folha_municipio", "regiao_com_criterio", "periodo_sem_verbo"],
                           weights=[20, 16, 10, 10, 7, 17, 12, 8])[0]
        a.subtipo = tipo
        a.categorias.add("A")
        if tipo == "regiao_com_criterio":
            regiao = rng.choice(["Nordeste", "Sul", "Sudeste", "Norte", "Centro-Oeste", "Amazônia Legal", "região Sul",
                                 "litoral nordestino", "Pantanal", "Sertão"])
            rng.choice([lambda: self.c_tipo(a), lambda: self.c_escala(a), lambda: self.c_cgeo(a)])()
            a.pedido.append(f'mencione também a região "{regiao}" (é só uma região, não diga estado nem município)')
            a.exige(regiao.replace("região ", ""))
            a.notas.append("região não é estado nem município: nada anotado para ela (manual, state/city)")
            return
        if tipo == "periodo_sem_verbo":
            self.c_periodo(a, verbo="nenhum")
            rng.choice([lambda: self.c_estado(a), lambda: self.c_tipo(a), lambda: self.c_escala(a)])()
            return
        if tipo == "estado_ou_capital":
            nome = rng.choice(["São Paulo", "Rio de Janeiro"])
            prep = "de" if nome == "São Paulo" else "do"
            a.campo("state", nome, f'o lugar "{nome}", escrito só como "{nome}", SEM as palavras "estado", "cidade" ou '
                    f'"município" e sem sigla (ex.: "cartas {prep} {nome}")',
                    nota=f"'{nome}' sem qualificador: estado ou capital (manual, state/city)")
            a.trocas.append(["state", "city"])
            a.exige(nome)
            for c in rng.sample(["escala", "tipo", "cgeo"], rng.choice([0, 1, 1])):
                {"escala": lambda: self.c_escala(a), "tipo": lambda: self.c_tipo(a), "cgeo": lambda: self.c_cgeo(a)}[c]()
        elif tipo == "escala_qualitativa":
            forma, valores = rng.choice([
                ("grande escala", ["1:25.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000"]),
                ("média escala", ["1:50.000", "1:100.000"]),
                ("escala maior que 100k", ["1:50.000", "1:25.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000"]),
            ])
            a.campo("scale", {UM_DE: valores}, f'numa escala descrita qualitativamente como "{forma}" (use exatamente essa '
                    f'expressão, sem número de escala)', nota=f"'{forma}': conjunto de escalas (manual, scale)")
            a.exige(forma)
            rng.choice([lambda: self.c_estado(a), lambda: self.c_tipo(a), lambda: self.c_municipio(a)])()
        elif tipo == "duas_escalas":
            e1, e2 = rng.sample(["1:25.000", "1:50.000", "1:100.000", "1:250.000"], 2)
            f1 = rng.choice(ESCALA_FORMAS[e1])[0]
            f2 = rng.choice(ESCALA_FORMAS[e2])[0]
            a.campo("scale", {UM_DE: [e1, e2]}, f'aceitando duas escalas, "{f1}" OU "{f2}" (ex.: "em {f1} ou {f2}")',
                    nota="duas escalas explícitas: qualquer uma (manual, scale)")
            a.exige(f1)
            a.exige(f2)
            rng.choice([lambda: self.c_estado(a), lambda: self.c_tipo(a), lambda: self.c_cgeo(a)])()
        elif tipo == "dois_codigos":
            r1, r2 = rng.sample(self.registros_codigo, 2)
            c1, c2 = r1["mi"], r2["inom"]
            if rng.random() < 0.5:
                c1, c2 = r1["inom"], r2["mi"]
            a.campo("keyword", {UM_DE: [c1, c2]}, f'dois códigos de folha, "{c1}" OU "{c2}", nessa ordem (ex.: "MI/INOM '
                    f'{c1} ou {c2}")', nota="dois códigos: o schema só comporta um; qualquer um (manual, keyword)")
            a.exige(c1)
            a.exige(c2)
            a.categorias.add("M")
        elif tipo == "projeto_termo":
            a.campo("project", {OPCIONAL: "Mapeamento Sistemático"},
                    'o programa de cartografia sistemática, dito como "cartografia sistemática" (sem a palavra "projeto" e '
                    'sem "mapeamento")', nota="termo distintivo do nome, sem apelido na ferramenta: project opcional")
            a.exige("cartografia sistematica")
            rng.choice([lambda: self.c_estado(a), lambda: self.c_escala(a), lambda: self.c_municipio(a)])()
        else:
            nome = rng.choice(self.folhas_municipio)
            self.c_folha(a, nome, municipio=True)
            for c in rng.sample(["escala", "tipo"], rng.choice([0, 1])):
                {"escala": lambda: self.c_escala(a), "tipo": lambda: self.c_tipo(a)}[c]()

    def _subespecificada(self, a: Alvo):
        rng = self.rng
        # Só consultas com intenção de busca no acervo e NENHUM critério representável no schema.
        # Um único critério ("ortoimagens", "cartas 1:50.000") não é subespecificação: é consulta
        # simples, e o manual exige a busca (Instrução 1 do prompt: "um único parâmetro basta").
        tipo = rng.choices(["generica", "regiao", "finalidade"], weights=[40, 35, 25])[0]
        a.subtipo = tipo
        a.categorias.add("E")
        a.aceita_nao_chamar = True
        a.notas.append("subespecificada: buscar sem filtros ou pedir esclarecimento são ambos aceitos (manual, categoria E)")
        if tipo == "generica":
            a.pedido.append("peça de forma genérica cartas, mapas ou produtos do acervo, SEM nenhum critério (nenhum lugar, "
                            "escala, tipo, data, código, projeto, ordem ou quantidade)")
        elif tipo == "regiao":
            regiao = rng.choice(["Nordeste", "Sul", "Sudeste", "Norte", "Centro-Oeste", "Amazônia Legal", "região Sul",
                                 "litoral brasileiro", "semiárido", "fronteira oeste", "Pantanal", "Sertão nordestino"])
            a.pedido.append(f'peça cartas ou mapas de uma região do Brasil — "{regiao}" — SEM estado, município ou outro critério')
            a.exige(regiao.replace("região ", ""))
            a.notas.append("região não é estado nem município: nenhum campo (manual, state/city)")
        else:
            finalidade = rng.choice(["uma trilha", "um trabalho de campo", "um exercício militar", "estudar relevo",
                                     "um projeto de estrada", "aula de geografia", "planejar uma obra", "orientação"])
            a.pedido.append(f'peça cartas ou mapas para {finalidade}, dizendo a finalidade mas SEM nenhum critério do acervo '
                            '(nenhum lugar, escala, tipo de produto, data, código, projeto, ordem ou quantidade)')

    def _fora(self, a: Alvo):
        rng = self.rng
        subtipos = {
            "cotidiano": (40, "outro assunto do dia a dia: previsão do tempo, trânsito, esportes, receitas, notícias, "
                              "horários de ônibus, programação de TV",
                          ["previsão do tempo", "resultado de jogo de futebol", "receita de bolo", "trânsito agora",
                           "horário do ônibus", "cotação do dólar", "notícias do dia", "filme em cartaz", "piada", "horóscopo"]),
            "dados": (30, "pedido de dado que não é produto cartográfico: população, PIB, CEP, telefone, endereço, "
                          "estatística, eleição",
                      ["população de uma cidade", "PIB de um estado", "CEP de uma rua", "telefone de um órgão",
                       "número de eleitores", "IDH", "taxa de desemprego", "temperatura média", "índice de chuva do mês"]),
            "exterior": (40, "cartas ou mapas de um lugar FORA do Brasil (outro país, cidade estrangeira, continente, "
                             "polo, outro planeta ou a Lua)",
                         ["Argentina", "Paraguai", "Portugal", "Lisboa", "Paris", "Tóquio", "Angola", "Chile", "Antártida",
                          "Lua", "Marte", "Europa", "Nova York", "Bolívia", "Peru", "Uruguai", "México", "Canadá"]),
            "rotas": (25, "navegação ou rota: como chegar, distância entre cidades, caminho de carro, GPS, trajeto",
                      ["rota de carro", "distância entre duas capitais", "como chegar a um lugar", "melhor caminho",
                       "tempo de viagem", "localização atual"]),
            "conceitual": (35, "pergunta conceitual sobre cartografia ou sobre o sistema, sem pedir produtos (o que é, "
                               "como funciona, para que serve)",
                           ["o que é INOM", "o que é o MI", "o que é projeção UTM", "como ler curvas de nível",
                            "diferença entre escala grande e pequena", "o que é um MDT", "o que faz a DSG",
                            "o que é o Sistema Cartográfico Nacional", "como calcular distância numa carta"]),
            "servicos": (30, "serviço de conta ou atendimento, sem pedir produto: senha, cadastro, erro de download, "
                             "contato, preço, compra, prazo",
                         ["esqueci a senha", "como me cadastrar", "o download deu erro", "telefone de contato",
                          "quanto custa", "prazo de entrega", "falar com um atendente", "nível de acesso"]),
            "conversa": (25, "conversa sem intenção de busca: saudação, agradecimento, teste, mensagem vazia de conteúdo",
                         ["saudação", "agradecimento", "teste do sistema", "pergunta se está funcionando",
                          "elogio", "despedida", "emoji ou interjeição"]),
            "ficcao": (20, "mapa de lugar fictício ou imaginário (livros, filmes, jogos, lendas)",
                       ["Terra Média", "Hogwarts", "Atlântida", "Nárnia", "Westeros", "mapa do tesouro",
                        "cidade de um videogame", "Eldorado"]),
            "producao": (15, "pedido para PRODUZIR algo novo, não buscar no acervo (desenhar, criar, editar ou gerar um mapa)",
                         ["desenhar mapa do bairro", "criar mapa personalizado", "editar uma carta", "gerar mapa com IA",
                          "fazer um croqui"]),
            "armadilha_lexical": (60, "pedido que usa as palavras 'carta', 'mapa', 'folha', 'escala' ou 'projeto' em "
                                      "OUTRO sentido, sem nenhuma relação com produtos cartográficos (armadilha de "
                                      "vocabulário)",
                                  ["carta de vinhos", "carta de apresentação", "mapa astral", "mapa mental",
                                   "mapa de calor de vendas", "folha de pagamento", "folha de ponto",
                                   "escala de plantão", "escala de trabalho", "escala musical", "carta de baralho",
                                   "carta de motorista", "mapa do genoma", "projeto de lei", "carta de crédito",
                                   "mapa de assentos do avião", "cartas de tarô", "escala Richter"]),
        }
        nomes = list(subtipos)
        tipo = rng.choices(nomes, weights=[subtipos[n][0] for n in nomes])[0]
        _peso, descricao, temas = subtipos[tipo]
        tema = rng.choice(temas)
        a.subtipo = tipo
        a.espera_tool_call = False
        a.categorias.add("F")
        a.pedido.append(f"escreva uma mensagem de usuário do tipo: {descricao}. Tema sugerido: {tema}. A mensagem NÃO pode "
                        "pedir produtos cartográficos do território brasileiro que existam num acervo (nada de cartas de "
                        "estados, municípios, escalas ou códigos do Brasil)")
        a.notas.append(f"fora do domínio ({tipo}): não chamar a ferramenta (manual, P4)")

    # -- montagem ------------------------------------------------------------------
    def categorias(self, a: Alvo) -> list[str]:
        """Categorias como no dataset de 310: S (um critério) ou C (mais de um), mais M/T/O/A.

        O bloco de ordenação (sortField + sortDirection + limit) e o período contam como um critério
        cada; uma consulta cujo único critério é o período ou a ordenação fica só em T ou O, como as
        famílias GT e GO do gerador do dataset de 310.
        """
        cats = set(a.categorias)
        if "F" in cats:
            return ["F"]
        if "E" in cats:
            return ["E"] + (["A"] if a.informal else [])
        criterios = [c for c in a.esperado if c not in ("sortField", "sortDirection", "limit")]
        n = len(criterios) + (1 if "O" in cats else 0)
        if n > 1:
            cats.add("C")
        elif not (n == 1 and ({"T", "O"} & cats) and not (set(criterios) - {"publicationPeriod", "creationPeriod"})):
            cats.add("S")
        if a.informal:
            cats.add("A")
        ordem = ["S", "C", "M", "T", "O", "A", "E", "F"]
        return [c for c in ordem if c in cats]

    def gerar(self) -> list[dict]:
        alvos = []
        for fam, n in CONTAGENS.items():
            for i in range(1, n + 1):
                a = self.familia(fam, i)
                registro = self.registro() if fam != "VF" else self.rng.choice(
                    ["direto", "coloquial", "pergunta", "formal", "sem_acento"])
                if registro in REGISTROS_INFORMAIS and fam not in ("VF",):
                    a.informal = True
                proibido = []
                if fam not in ("VF",):
                    proibido = [
                        "não acrescente NENHUM outro critério além dos pedidos: nada de outro lugar, escala, tipo de "
                        "produto, data, código, projeto, CGEO, ordem ou quantidade",
                        'palavras genéricas como "cartas", "mapas", "folhas" e "produtos" podem ser usadas, mas não use '
                        '"topográfica", "ortoimagem", "vetorial", "MDT", "MDS" ou outro tipo se o tipo não foi pedido',
                        "não escreva nomes de campos nem termos do sistema (keyword, supplyArea, enum...)",
                    ]
                    if not any(c in a.esperado for c in ("publicationPeriod", "creationPeriod")):
                        proibido.append("não use verbos de data (publicada, criada, feita, elaborada, produzida) nem "
                                        "expressões de tempo")
                persona = self.rng.choice(PERSONAS)
                alvos.append({
                    "id": f"{config_lote.PREFIXO_ID}{fam}{i:04d}", "familia": fam, "categorias": self.categorias(a),
                    "registro": registro, "registro_descricao": REGISTROS[registro][0], "persona": persona,
                    "superficies": a.superficies, "verbo_periodo": a.verbo,
                    "subtipo": a.subtipo, "pedido": a.pedido, "proibido": proibido,
                    "esperado": a.esperado, "trocas": a.trocas, "espera_tool_call": a.espera_tool_call,
                    "aceita_nao_chamar": a.aceita_nao_chamar, "observacional": False,
                    "notas": "; ".join(dict.fromkeys(a.notas)),
                    "fonte": f"scripts/lote_validacao/gerar_alvos.py · semente {SEMENTE} · {fam} · "
                             f"{'+'.join(a.descricao) or a.subtipo}",
                })
        return alvos


def main() -> int:
    g = Gerador()
    alvos = g.gerar()
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(json.dumps({"semente": SEMENTE, "total": len(alvos), "contagens": CONTAGENS,
                                   "alvos": alvos}, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    cats = Counter(c for a in alvos for c in a["categorias"])
    campos = Counter(k for a in alvos for k in a["esperado"])
    print(f"{len(alvos)} alvos -> {DESTINO.relative_to(RAIZ)}")
    print("categorias:", dict(cats))
    print("campos:", dict(campos))
    print("registros:", dict(Counter(a["registro"] for a in alvos)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
