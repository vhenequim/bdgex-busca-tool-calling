"""Orientações aprendidas com erros: markdowns com frontmatter, consultados pela v3.

Cada orientação é um arquivo em `experimentos/orientacoes/md/*.md`:

    ---
    tipo: orientacao-pfc          # só arquivos com este tipo são carregados
    status: ativa                 # ativa | retirada (retiradas ficam no histórico, mas não são usadas)
    nome: uf-por-extenso
    titulo: Estado sempre por extenso
    campos: [state]
    gatilhos: ['\\bestado\\b']     # expressões regulares sobre a consulta normalizada (minúsculas, sem acento)
    gatilhos_originais: ['\\b[A-Z]{2}\\b']   # sobre o texto original (ex.: siglas em maiúsculas)
    sempre: false                 # true = entra em toda consulta
    ciclo: 1                      # ciclo de aprendizagem em que entrou (docs/orientacoes_ciclos.md)
    origem: "lote 1, tc2: 134 execuções com state como sigla"
    ---
    Texto curto da regra, com exemplos genéricos.

O frontmatter garante duas coisas: o modelo só vê esses arquivos (nenhum outro texto do repositório
é carregado por aqui), e cada orientação só aparece quando é pertinente à consulta — por gatilho
(entrega automática) ou pelo nome/campo que o modelo pede (entrega pela ferramenta
`consultar_orientacoes`). As orientações são escritas a partir dos erros nos conjuntos de
DESENVOLVIMENTO (as 310 consultas e o lote 1); o lote 2, de teste, não é usado para escrevê-las.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from pfc_busca.ferramentas import norm

DIR = Path(__file__).resolve().parent / "md"
TIPO = "orientacao-pfc"


@dataclass
class Orientacao:
    nome: str
    titulo: str
    corpo: str
    campos: list[str] = field(default_factory=list)
    gatilhos: list[re.Pattern] = field(default_factory=list)
    gatilhos_originais: list[re.Pattern] = field(default_factory=list)
    sempre: bool = False
    ciclo: int = 1
    arquivo: str = ""

    def aplica(self, consulta: str) -> bool:
        if self.sempre:
            return True
        q = norm(consulta)
        return any(g.search(q) for g in self.gatilhos) or any(g.search(consulta) for g in self.gatilhos_originais)

    def texto(self) -> str:
        return f"[{self.nome}] {self.titulo}: {self.corpo}"


def _ler(arquivo: Path) -> Orientacao | None:
    bruto = arquivo.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", bruto, re.S)
    if not m:
        return None
    meta = yaml.safe_load(m.group(1)) or {}
    if meta.get("tipo") != TIPO or meta.get("status", "ativa") != "ativa":
        return None
    corpo = " ".join(m.group(2).split())
    return Orientacao(
        nome=str(meta["nome"]), titulo=str(meta.get("titulo", meta["nome"])), corpo=corpo,
        campos=list(meta.get("campos") or []),
        gatilhos=[re.compile(g) for g in meta.get("gatilhos") or []],
        gatilhos_originais=[re.compile(g) for g in meta.get("gatilhos_originais") or []],
        sempre=bool(meta.get("sempre")), ciclo=int(meta.get("ciclo", 1)), arquivo=arquivo.name,
    )


@lru_cache(maxsize=4)
def carregar(diretorio: str = str(DIR), ciclo_max: int | None = None) -> tuple[Orientacao, ...]:
    """Orientações ativas (opcionalmente só as dos ciclos até `ciclo_max`), em ordem de nome."""
    saida = []
    for arq in sorted(Path(diretorio).glob("*.md")):
        o = _ler(arq)
        if o and (ciclo_max is None or o.ciclo <= ciclo_max):
            saida.append(o)
    return tuple(saida)


def pertinentes(consulta: str, ciclo_max: int | None = None) -> list[Orientacao]:
    return [o for o in carregar(ciclo_max=ciclo_max) if o.aplica(consulta)]


def bloco_para_prompt(consulta: str, ciclo_max: int | None = None) -> str:
    """Orientações pertinentes à consulta, prontas para entrar no prompt de sistema (entrega automática)."""
    selecionadas = pertinentes(consulta, ciclo_max)
    if not selecionadas:
        return ""
    return "Orientações aprendidas com erros anteriores (siga-as):\n" + "\n".join(f"- {o.texto()}" for o in selecionadas)


def indice(ciclo_max: int | None = None) -> str:
    return "\n".join(f"- {o.nome}: {o.titulo} (campos: {', '.join(o.campos) or 'geral'})"
                     for o in carregar(ciclo_max=ciclo_max))


def consultar(assunto: str, consulta: str, ciclo_max: int | None = None) -> str:
    """Entrega pela ferramenta: por nome, por campo, ou as pertinentes à consulta ('consulta' ou vazio)."""
    todas = carregar(ciclo_max=ciclo_max)
    a = norm(assunto)
    escolhidas = [o for o in todas if a and (a == norm(o.nome) or a in {norm(c) for c in o.campos})]
    if not escolhidas:
        escolhidas = [o for o in todas if o.aplica(consulta)]
    if not escolhidas:
        return "Nenhuma orientação específica para esta consulta."
    return "\n".join(o.texto() for o in escolhidas)


def assinatura(ciclo_max: int | None = None) -> str:
    """SHA-256 do conjunto de orientações ativas (vai no manifesto da rodada: pré-registro)."""
    h = hashlib.sha256()
    for o in carregar(ciclo_max=ciclo_max):
        h.update((DIR / o.arquivo).read_bytes())
    return h.hexdigest()
