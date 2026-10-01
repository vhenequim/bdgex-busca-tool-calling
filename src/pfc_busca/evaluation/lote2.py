"""Lote 2 (teste da v3): medidas, pares, decomposição do acerto, tabelas, macros e relatório.

    python -m pfc_busca.evaluation.lote2 [--dir results/lote2] [--dataset data/lote_validacao_2.json]
        [--dir-310 results/v3_310] [--paper ../paper_revisado] [--sufixo-macro lote2]

Implementa o plano de análise do lote 2, fixado antes da rodada (docs/v3.md, seção 3), com as funções de
`pfc_busca.evaluation.lote` (carregamento e repontuação, medidas, efeitos de forma, pares, duas etapas):

1. As rodadas de cada configuração presente em DIR/<prefixo>gemma4-e4b-it-qat (as ausentes ficam de fora,
   com aviso), repontuadas contra o gabarito vigente de --dataset, uma execução por consulta
   (`lote._uma_por_id`). Prefixos: tc1 '', se1 'se-', tc2 'tc2-', se2 'se2-', tc3d 'tc3d-', tc3a 'tc3a-',
   tc3 'tc3-', se3 'se3-'.
2. A derivada `hib` = `lote.duas_etapas(tc2, se1)` (o TC v2 decide, a SE v1 extrai), simulada post hoc com as
   rodadas do próprio lote 2.
3. Por configuração: `lote.medidas` (acurácia com IC de Wilson, domínio, recusa em F, falsa recusa, E, F1
   ponderado, latência mediana e p95), `lote.efeitos_de_forma` e chamadas ao modelo por consulta; nas v3,
   consultas com pergunta, perguntas em texto, recusas contestadas e chamadas escritas como texto (dos extras
   gravados em cada execução; os extras podem vir como strings repr ou JSON).
4. Pares (`lote.comparar`: McNemar exato por consulta, diferença de acurácia e de F1 ponderado com IC por
   bootstrap pareado de 2.000 reamostragens), só nas consultas presentes nas duas configurações: principal
   (tc3, se3); degraus (tc1, tc2), (tc2, tc3d), (tc3d, tc3a), (tc3a, tc3); secundários (melhor, tc3),
   (hib, tc3), (hib, se3), (melhor, se3), em que `melhor` é a configuração v1/v2 isolada (tc1, se1, tc2, se2)
   de maior acurácia no lote 2 (empate: maior F1 ponderado, depois essa ordem).
5. Decomposição do acerto (tc3a, tc3, se3): acurácia da primeira decisão do modelo × final, consultas
   consertadas e estragadas pelo retorno e, entre as consertadas, o tipo de retorno que receberam (regras
   explícitas em `classificar_mensagem`, derivadas dos textos de `ferramentas.py`).
6. As rodadas das 310 consultas (tc3 e se3 em --dir-310, contra data/dataset.json), com as mesmas medidas,
   par e decomposição, sob o rótulo de desenvolvimento: dentro da amostra que orientou a v3.

Saídas em DIR/consolidado/ (as .tex também em PAPER/tabelas/, com --paper): numeros_<sufixo>.tex, com
\\res{<sufixo>}{<config>}{<medida>}, \\res{<sufixo>}{<a><b>}{<medida>} e \\res{v3base}{tc3|se3}{<medida>};
tab_lote2_degraus.tex, tab_lote2_pares.tex e tab_lote2_decomposicao.tex; lote2.md e lote2.json.

O lote 2 é o conjunto de teste: nada aqui imprime ou grava o texto de uma consulta, nem as mensagens do
validador (que citam trechos delas). Só contagens e medidas.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import statistics
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from pfc_busca import ferramentas, schema, v2, v3
from pfc_busca.evaluation import lote, metrics, report
from pfc_busca.evaluation.dataset_builder import CAMINHO_SAIDA as DATASET_310
from pfc_busca.evaluation.run_evaluation import DIR_RESULTADOS, RAIZ_REPO, carregar_execucoes, slug

MODELO = lote.MODELO
# chave: (prefixo da pasta, nome na tabela, nome curto, degrau)
CONFIGS: dict[str, tuple[str, str, str, str]] = {
    "tc1": (lote.CONFIGS["tc1"][0], "Tool Calling v1", "TC v1", "0"),
    "tc2": (lote.CONFIGS["tc2"][0], "Tool Calling v2", "TC v2", "1"),
    "tc3d": (v3.PREFIXOS["tool_calling_v3d"], "Tool Calling v3d (descrições v3)", "TC v3d", "2"),
    "tc3a": (v3.PREFIXOS["tool_calling_v3a"], "Tool Calling v3a (+ ferramentas auxiliares)", "TC v3a", "3"),
    "tc3": (v3.PREFIXOS["tool_calling_v3"], "Tool Calling v3 (+ retorno)", "TC v3", "4"),
    "se3": (v3.PREFIXOS["saida_estruturada_v3"], "Saída Estruturada v3 (controle)", "SE v3", "Controle"),
    "se1": (lote.CONFIGS["se1"][0], "Saída Estruturada v1", "SE v1", "Referência"),
    "se2": (lote.CONFIGS["se2"][0], "Saída Estruturada v2", "SE v2", "Referência"),
}
HIB = "hib"
NOME_HIB = ("Duas etapas (TC v2 decide, SE v1 extrai)", "Duas etapas", "Simulação")
V3_TC = ("tc3d", "tc3a", "tc3")
V3 = (*V3_TC, "se3")
ISOLADAS = ("tc1", "se1", "tc2", "se2")          # candidatas a "melhor configuração v1/v2 isolada"
DECOMPOSTAS = ("tc3a", "tc3", "se3")
CONFIGS_310 = ("tc3", "se3")
PAR_PRINCIPAL = [("tc3", "se3")]
PARES_DEGRAUS = [("tc1", "tc2"), ("tc2", "tc3d"), ("tc3d", "tc3a"), ("tc3a", "tc3")]
PARES_SECUNDARIOS = [("melhor", "tc3"), (HIB, "tc3"), (HIB, "se3"), ("melhor", "se3")]
GRUPOS_PARES = (("principal", PAR_PRINCIPAL), ("degraus", PARES_DEGRAUS), ("secundarios", PARES_SECUNDARIOS))
# extensão a outros modelos (docs/v3.md, "Extensão a outros modelos"): a comparação principal, o ganho da v3 sobre
# a solução do Cap. 4 e o A/B da v1
GRUPOS_PARES_EXTENSAO = (("principal", PAR_PRINCIPAL), ("extensao", [("tc1", "tc3"), ("tc1", "se1")]))
DECOMPOSTAS_EXTENSAO = ("tc3", "se3")
SUFIXO_PADRAO = "lote2"
ROTULO_310 = "v3base"


def sufixo_extensao(modelo: str) -> str:
    """Rótulo das macros da extensão a outro modelo (gemma4:e2b-it-qat -> lote2gemma4e2b)."""
    return SUFIXO_PADRAO + re.sub(r"[^a-z0-9]", "", slug(modelo).split("-it")[0].split("-instruct")[0])


def nome(k: str, curto: bool = False) -> str:
    if k == HIB:
        return NOME_HIB[1 if curto else 0]
    return CONFIGS[k][2 if curto else 1]


# ---------------------------------------------------------------------------
# Extras gravados nas execuções (podem vir como strings repr ou JSON)
# ---------------------------------------------------------------------------

SEM_TRACO = object()   # a execução não permite reconstruir a primeira decisão


def _literal(v: Any) -> Any:
    """Uma string repr (ast.literal_eval) ou JSON (json.loads: true/false/null) de volta a objeto; senão, v."""
    if isinstance(v, str):
        try:
            return ast.literal_eval(v)
        except (ValueError, SyntaxError, MemoryError, RecursionError):
            pass
        try:
            return json.loads(v)
        except (ValueError, RecursionError):
            return v
    return v


def _sim(v: Any) -> bool:
    """Booleano gravado como True, 'True' ou 'true'."""
    return v is True or (isinstance(v, str) and v.strip().lower() == "true")


def _grupo(linha: dict) -> str:
    """F (fora do domínio), E (subespecificada) ou dominio — a mesma partição de `lote.medidas`."""
    if not linha["espera_tool_call"]:
        return "F"
    return "E" if linha.get("aceita_nao_chamar") else "dominio"


def extra(linha: dict, chave: str, padrao: Any = None) -> Any:
    """Um campo de `extras`, com strings repr ou JSON convertidas de volta (`_literal`)."""
    extras = _literal(linha.get("extras"))
    v = (extras if isinstance(extras, dict) else {}).get(chave, padrao)
    return _literal(v)


def normalizar_extras(linha: dict) -> dict:
    """A linha com `extras` já convertido (uma vez) de strings repr ou JSON para objetos, campo a campo."""
    extras = _literal(linha.get("extras"))
    if isinstance(extras, dict):
        return {**linha, "extras": {k: _literal(v) for k, v in extras.items()}}
    return linha


def _int(v: Any, padrao: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return padrao


def primeira_decisao(linha: dict):
    """Parâmetros da primeira busca, None para recusa/não busca, ou SEM_TRACO se o traço não permite saber.

    Tool Calling v3: a primeira chamada a buscar_catalogo, ou a recusa, se veio antes de qualquer busca (no
    traço, recusar_consulta só aparece quando foi contestada); sem nenhuma das duas, a primeira decisão é a
    final. Saída Estruturada v3: o primeiro objeto do histórico de tentativas (uma string = recusa; um objeto
    fora do schema = {})."""
    historico = extra(linha, "historico")
    if isinstance(historico, list) and historico:          # Saída Estruturada v3
        h = historico[0]
        if isinstance(h, str):
            return None
        if not isinstance(h, dict):
            return SEM_TRACO
        # objeto fora do schema (params None): é uma busca malformada, não uma recusa — como na resposta final,
        # que o aceita como {} (v3.TradutorEstruturadoV3), e como a chamada malformada do Tool Calling
        return h["params"] if isinstance(h.get("params"), dict) else {}
    traco = extra(linha, "traco")
    if not isinstance(traco, list):
        return SEM_TRACO
    for t in traco:
        f = t.get("ferramenta") if isinstance(t, dict) else None
        if f == "buscar_catalogo":
            return t.get("args") if isinstance(t.get("args"), dict) else {}
        if f == "recusar_consulta":
            return None
    return linha["predito"]   # nenhuma busca nem recusa contestada: a primeira decisão é a final


def correto_com(linha: dict, predito) -> bool:
    x = dict(linha, predito=predito, chamou_ferramenta=predito is not None)
    return metrics.avaliar_linha(x).correto


# ---------------------------------------------------------------------------
# Classificação do retorno (item 5 do plano)
# ---------------------------------------------------------------------------
#
# O retorno que o modelo recebeu antes da decisão final vem do que foi gravado na execução:
#   TC: extras.traco — cada entrada de buscar_catalogo cujo `resultado` não é "Busca executada." (a mensagem de
#       ferramentas.mensagem_validacao, ou "BUSCA NÃO EXECUTADA: <erro de tipo>"), e cada entrada de
#       recusar_consulta (gravada só quando a recusa foi contestada: ferramentas.mensagem_recusa). O traço
#       guarda os 300 primeiros caracteres da mensagem; quando os argumentos gravados são um objeto, a lista
#       completa de erros e avisos é refeita com ferramentas.validar_parametros (determinístico: a mesma v3
#       congelada, com a consulta e a data da execução) e só é usada se reproduzir exatamente o trecho gravado;
#       senão, vale o trecho, item por item.
#   SE: extras.historico — os `erros` e `avisos` de cada tentativa devolvida ao modelo (todas as entradas com
#       objeto menos a última, que é a aceita) e cada "fora_do_escopo contestado".
# Cada item (uma linha da mensagem) recebe a primeira categoria cuja regra casa, nesta ordem:
#   contestada  recusa contestada: "RECUSA AINDA NÃO REGISTRADA..." ou "fora_do_escopo contestado";
#   valor       o item traz o valor a preencher ou a usar: "preencha state='X'", "preencha city='X'",
#               "preencha project='X'" (UF, município, projeto citados), "preencha productType (ex.: 'X')" (o
#               tipo nomeado na consulta), "corresponde a {...} (resolver_periodo)" (as datas pela tabela do
#               manual), "use ... state='X'" (sigla, "sigla + nome" ou UF na keyword → o nome), "use só o
#               código na forma canônica", "Use '1:...'" e "Use um de [...]" (escala canônica ou o conjunto
#               aceito pelo manual), "o mais próximo é '...'" (município do IBGE) e "a consulta cita o
#               município '...', com o nome inteiro";
#   remover     "remova ..." sem valor: campo sem evidência na consulta (tipo, limite, estado, período,
#               ordenação, CGEO, projeto) e keyword genérica ou com tipo de produto;
#   forma       os demais erros de forma, sem valor: parâmetro inexistente, valor fora do enumerado, state que
#               não é UF, período malformado ou invertido, limit não inteiro, objeto fora do schema, chamada
#               malformada ou com argumentos fora do tipo;
#   aponta      os demais avisos: indicam o campo (preencher scale, período, keyword, ordenação ou supplyArea;
#               trocar city/state/keyword de campo; conferir o período) sem trazer o valor.
# Uma consulta consertada (ou estragada) é atribuída à primeira categoria, na mesma ordem, entre as que recebeu:
# a precedência credita ao código a correção mais informativa. `recebeu_<categoria>` conta, sem exclusão, as
# consertadas que receberam ao menos um item de cada categoria.

CATEGORIAS_RETORNO = ("contestada", "valor", "remover", "forma", "aponta")
SEM_MENSAGEM = "sem_mensagem"
_RE_CONTESTADA = re.compile(r"^(?:RECUSA AINDA NÃO REGISTRADA|fora_do_escopo contestado$)")
_RE_VALOR = [re.compile(p) for p in (
    r"\bpreencha \w+='",
    r"\bpreencha productType \(ex\.: '",
    r"corresponde a \{.*\} \(resolver_periodo\)",
    r"\buse\b[^.;]*\bstate='",
    r"use só o código na forma canônica",
    r"\bUse '1:",
    r"\bUse um de \[",
    r"o mais próximo é '",
    r"a consulta cita o município '[^']+', com o nome inteiro",
)]
_RE_REMOVER = re.compile(r"\bremova\b")
_RE_FORMA = [re.compile(p) for p in (
    r"parâmetro inexistente", r"não é um valor válido", r"não é o nome de uma UF brasileira",
    r"use um objeto com as chaves", r"datas em ISO", r"start depois de end", r"número inteiro positivo",
    r"não é um objeto JSON válido", r"^BUSCA NÃO EXECUTADA:", r"argumentos fora do tipo", r"chamada malformada",
    r"os argumentos precisam ser um objeto JSON",
)]
_CABECALHOS_VALIDACAO = ("BUSCA NÃO EXECUTADA. Corrija", "AVISOS sobre os parâmetros")
_LIMITE_TRACO = 300   # caracteres do resultado que o traço da v3 guarda (v3.TradutorV3: msg[:300])


def classificar_mensagem(texto: str) -> str:
    """Categoria de um item de retorno (ver o bloco de comentários acima)."""
    t = str(texto or "").strip()
    if _RE_CONTESTADA.search(t):
        return "contestada"
    if any(r.search(t) for r in _RE_VALOR):
        return "valor"
    if _RE_REMOVER.search(t):
        return "remover"
    if any(r.search(t) for r in _RE_FORMA):
        return "forma"
    return "aponta"


def itens_da_mensagem(msg: str) -> list[str]:
    """Itens de uma mensagem de `ferramentas.mensagem_validacao` (cabeçalho + '\\n- ' item ...)."""
    if msg.startswith(_CABECALHOS_VALIDACAO) and "\n- " in msg:
        return [i for i in msg.split("\n- ")[1:] if i.strip()]
    return [msg]


def _itens_da_busca(args: Any, resultado: str, linha: dict, contagem: Counter) -> list[str]:
    if isinstance(args, dict) and resultado.startswith(_CABECALHOS_VALIDACAO):
        try:
            hoje = date.fromisoformat(linha["hoje"])
            erros, avisos = ferramentas.validar_parametros(args, linha.get("consulta") or "", hoje)
        except Exception:  # noqa: BLE001 — sem reconstrução, vale o trecho gravado
            erros, avisos = [], []
        if (erros or avisos) and ferramentas.mensagem_validacao(erros, avisos)[:len(resultado)] == resultado:
            contagem["refeitas"] += len(resultado) >= _LIMITE_TRACO
            return erros + avisos
    contagem["truncadas_sem_reconstrucao"] += len(resultado) >= _LIMITE_TRACO
    return itens_da_mensagem(resultado)


def mensagens_de_retorno(linha: dict, contagem: Counter | None = None) -> list[str]:
    """Itens de retorno do validador e da recusa contestada que o modelo recebeu antes da decisão final."""
    contagem = contagem if contagem is not None else Counter()
    historico = extra(linha, "historico")
    if isinstance(historico, list) and historico:                     # Saída Estruturada v3
        itens: list[str] = []
        for k, h in enumerate(historico):
            if isinstance(h, str):
                if h.startswith("fora_do_escopo contestado"):
                    itens.append(h)
            elif isinstance(h, dict) and k < len(historico) - 1:      # a última tentativa é a aceita
                itens += [str(x) for x in (h.get("erros") or [])] + [str(x) for x in (h.get("avisos") or [])]
        return itens
    traco = extra(linha, "traco")
    itens = []
    for t in traco if isinstance(traco, list) else []:
        if not isinstance(t, dict):
            continue
        f, resultado = t.get("ferramenta"), str(t.get("resultado") or "")
        if f == v2.NOME_RECUSA and resultado.startswith("RECUSA AINDA NÃO REGISTRADA"):
            itens.append(resultado)
        elif f == schema.NOME_FERRAMENTA and resultado and not resultado.startswith("Busca executada"):
            itens += _itens_da_busca(t.get("args"), resultado, linha, contagem)
    return itens


def categoria_principal(categorias: set[str] | list[str]) -> str:
    return next((c for c in CATEGORIAS_RETORNO if c in categorias), SEM_MENSAGEM)


def decompor(linhas: list[dict]) -> dict[str, int]:
    """Primeira decisão × final (as contagens de scripts/v3/decompor_ganho.py) e o tipo de retorno.

    Chaves: n (execuções com traço), final, primeira, consertou, estragou, sem_traco, contestadas,
    contestada_<F|E|dominio>_<certa|errada> (a partição de `lote.medidas`: E, a subespecificada, fora do
    domínio), com_aviso (TC: avisos_recebidos > 0), com_retorno (recebeu algum item do validador ou da recusa
    contestada), consertou_<categoria>, estragou_<categoria> (exclusivas, pela precedência; uma estragada cuja
    execução terminou em erro de infraestrutura conta como estragou_erro_infra, porque não foi o retorno que a
    estragou) e recebeu_<categoria> (entre as consertadas, sem exclusão); erro_infra; refeitas e
    truncadas_sem_reconstrucao (mensagens do traço cortadas em 300 caracteres)."""
    c: Counter = Counter()
    for x in linhas:
        final = metrics.avaliar_linha(x).correto
        p = primeira_decisao(x)
        if p is SEM_TRACO:
            c["sem_traco"] += 1
            continue
        primeira = correto_com(x, p)
        c["n"] += 1
        c["final"] += final
        c["primeira"] += primeira
        c["consertou"] += final and not primeira
        c["estragou"] += primeira and not final
        c["erro_infra"] += metrics.erro_de_infra(x)
        if _sim(extra(x, "recusa_contestada")):
            c["contestadas"] += 1
            c["contestada_" + _grupo(x) + ("_certa" if final else "_errada")] += 1
        if _int(extra(x, "avisos_recebidos", 0) or 0) > 0:
            c["com_aviso"] += 1
        categorias = {classificar_mensagem(m) for m in mensagens_de_retorno(x, c)}
        c["com_retorno"] += bool(categorias)
        if final and not primeira:
            c["consertou_" + categoria_principal(categorias)] += 1
            for cat in categorias:
                c["recebeu_" + cat] += 1
        elif primeira and not final:
            c["estragou_" + ("erro_infra" if metrics.erro_de_infra(x) else categoria_principal(categorias))] += 1
    if c["n"]:
        # "só mandando remover ou corrigir a forma de um campo": o agregado do item 5 do plano (docs/v3.md)
        c["consertou_remover_forma"] = c["consertou_remover"] + c["consertou_forma"]
    return dict(c)


# ---------------------------------------------------------------------------
# Carregamento e medidas
# ---------------------------------------------------------------------------

def carregar_rodadas(diretorio: Path, dataset: Path, configs, avisos: list[str]) -> dict[str, dict]:
    """config -> {"linhas" (uma execução por consulta), "casos", "pasta", "descartadas", "cobertura"}."""
    dados: dict[str, dict] = {}
    for k in configs:
        p = diretorio / (CONFIGS[k][0] + MODELO)
        r = lote.carregar_pasta(p, dataset)
        if r is None:
            avisos.append(f"{k}: sem rodada em {_mostrar(p)} (fora da análise)")
            continue
        linhas, casos = r
        descartadas = sum(1 for b in carregar_execucoes(p)
                          if (casos.get(b["id"]) or {}).get("consulta") != b.get("consulta"))
        unicas = [normalizar_extras(x) for x in lote._uma_por_id(linhas).values()]
        n_conjunto = sum(1 for c in casos.values() if not c.get("observacional"))
        if descartadas:
            avisos.append(f"{k}: {descartadas} execução(ões) descartada(s) na repontuação (id ou texto fora de "
                          f"{dataset.name})")
        if not unicas:
            avisos.append(f"{k}: nenhuma execução válida contra {dataset.name} (fora da análise)")
            continue
        if len(unicas) < n_conjunto:
            avisos.append(f"{k}: {len(unicas)} de {n_conjunto} consultas (rodada incompleta; as medidas são das "
                          f"consultas presentes e os pares usam só as comuns)")
        if k in V3:
            sem_extras = sum(1 for x in unicas if not isinstance(extra(x, "traco"), list)
                             and not isinstance(extra(x, "historico"), list))
            if sem_extras:
                avisos.append(f"{k}: {sem_extras} execução(ões) sem traço nem histórico legível em extras (chamadas, "
                              f"perguntas e decomposição não as contam; confira o formato gravado)")
        dados[k] = {"linhas": unicas, "casos": casos, "pasta": _mostrar(p), "descartadas": descartadas,
                    "n_conjunto": n_conjunto, "cobertura": len(unicas) / n_conjunto if n_conjunto else None}
    return dados


def _mostrar(p: Path) -> str:
    try:
        return p.resolve().relative_to(RAIZ_REPO).as_posix()
    except ValueError:
        return p.resolve().as_posix()


def chamadas_por_consulta(k: str, linhas: list[dict]) -> float | None:
    """Média de chamadas ao modelo por consulta: TC v3 (extras.chamadas_modelo), SE v3 (extras.tentativas);
    v1 e v2 fazem uma chamada por construção."""
    if not linhas:
        return None
    if k in V3_TC:
        return statistics.fmean(_int(extra(x, "chamadas_modelo", 1), 1) for x in linhas)
    if k == "se3":
        return statistics.fmean(_int(extra(x, "tentativas", 1), 1) for x in linhas)
    return 1.0


def chamadas_hib(decisao: list[dict], hib: list[dict]) -> float | None:
    """Duas etapas: uma chamada (a decisão) e mais uma (a extração) quando a decisão busca."""
    dec = lote._uma_por_id(decisao)
    vals = [1 + (dec[x["id"]]["predito"] is not None) for x in hib if x["id"] in dec]
    return statistics.fmean(vals) if vals else None


def medidas_v3(k: str, linhas: list[dict]) -> dict[str, Any]:
    """Chamadas, perguntas, recusas contestadas e chamadas escritas como texto (extras das v3)."""
    ex = {"perguntas": [], "perguntas_em_texto": [], "chamadas_em_texto": [], "recusa_contestada": [],
          "sem_final": []}
    contestadas = Counter()
    texto_certas = 0
    for x in linhas:
        if _int(extra(x, "chamadas_em_texto", 0) or 0) > 0 and metrics.avaliar_linha(x).correto:
            texto_certas += 1
        for chave in ("perguntas", "perguntas_em_texto", "chamadas_em_texto"):
            ex[chave].append(_int(extra(x, chave, 0) or 0))
        contestada = _sim(extra(x, "recusa_contestada"))
        ex["recusa_contestada"].append(contestada)
        ex["sem_final"].append(_sim(extra(x, "sem_final")))
        if contestada:
            final = metrics.avaliar_linha(x).correto
            contestadas[_grupo(x) + ("_certa" if final else "_errada")] += 1
    tc = k in V3_TC
    return {
        "n": len(linhas),
        "com_pergunta": sum(v > 0 for v in ex["perguntas"]) if tc else None,
        "perguntas": sum(ex["perguntas"]) if tc else None,
        "com_pergunta_em_texto": sum(v > 0 for v in ex["perguntas_em_texto"]) if tc else None,
        "perguntas_em_texto": sum(ex["perguntas_em_texto"]) if tc else None,
        "com_chamada_em_texto": sum(v > 0 for v in ex["chamadas_em_texto"]) if tc else None,
        "chamadas_em_texto": sum(ex["chamadas_em_texto"]) if tc else None,
        "com_chamada_em_texto_certa": texto_certas if tc else None,
        "contestadas": sum(ex["recusa_contestada"]),
        "contestadas_detalhe": dict(contestadas),
        "sem_final": sum(ex["sem_final"]) if tc else None,
    }


def chamadas_em_texto_nao_interpretadas(linhas: list[dict]) -> int:
    """Tool Calling v1/v2: respostas sem busca com uma chamada escrita como texto (o parser da v3 a
    interpretaria; na v1/v2 a resposta fica sem busca)."""
    nomes = {schema.NOME_FERRAMENTA, v2.NOME_RECUSA}
    return sum(1 for x in linhas if x["predito"] is None and v3.chamadas_em_texto(x.get("texto_resposta") or "", nomes))


def medidas_config(k: str, linhas: list[dict], casos: dict[str, dict]) -> dict[str, Any]:
    m = lote.medidas(linhas, casos)
    m["efeitos"] = lote.efeitos_de_forma(linhas)
    m["chamadas"] = chamadas_por_consulta(k, linhas)
    if k in V3:
        m["v3"] = medidas_v3(k, linhas)
    if k in ("tc1", "tc2"):
        m["chamadas_em_texto_nao_interpretadas"] = chamadas_em_texto_nao_interpretadas(linhas)
    return m


def melhor_isolada(medidas: dict[str, dict]) -> str | None:
    presentes = [k for k in ISOLADAS if k in medidas]
    if not presentes:
        return None
    return max(presentes, key=lambda k: (medidas[k]["acuracia"], medidas[k]["f1"], -ISOLADAS.index(k)))


def _pares(linhas: dict[str, list[dict]], grupos, avisos: list[str]) -> dict[str, dict]:
    saida: dict[str, dict] = {}
    for grupo, pares in grupos:
        for a, b in pares:
            chave = f"{a}{b}"
            if a not in linhas or b not in linhas:
                avisos.append(f"par {chave}: falta {', '.join(x for x in (a, b) if x not in linhas)} (fora)")
                continue
            comuns = {x["id"] for x in linhas[a]} & {x["id"] for x in linhas[b]}
            if not comuns:
                avisos.append(f"par {chave}: nenhuma consulta em comum (fora)")
                continue
            saida[chave] = {"grupo": grupo, "a": a, "b": b, **lote.comparar(linhas[a], linhas[b])}
    return saida


def analisar(dados: dict[str, dict], grupos, decompostas, avisos: list[str],
             derivar: bool = True) -> dict[str, Any]:
    """Medidas, pares e decomposição de um conjunto (dados: config -> carregar_rodadas)."""
    medidas = {k: medidas_config(k, v["linhas"], v["casos"]) for k, v in dados.items()}
    linhas = {k: v["linhas"] for k, v in dados.items()}
    if derivar and "tc2" in dados and "se1" in dados:
        hib = lote.duas_etapas(dados["tc2"]["linhas"], dados["se1"]["linhas"])
        if hib:
            casos = dados["se1"]["casos"]
            medidas[HIB] = lote.medidas(hib, casos)
            medidas[HIB]["efeitos"] = lote.efeitos_de_forma(hib)
            medidas[HIB]["chamadas"] = chamadas_hib(dados["tc2"]["linhas"], hib)
            linhas[HIB] = hib
    elif derivar:
        avisos.append("hib: precisa de tc2 e se1 (fora)")
    melhor = melhor_isolada(medidas) if derivar else None
    if melhor:
        linhas["melhor"] = linhas[melhor]
        ns = {medidas[k]["n"] for k in ISOLADAS if k in medidas}
        if len(ns) > 1:
            avisos.append(f"melhor: as candidatas v1/v2 têm números de consultas diferentes ({sorted(ns)}); a escolha "
                          f"compara acurácias de conjuntos diferentes")
    pares = _pares(linhas, grupos, avisos)
    # EXPLORATÓRIO (fora do plano de docs/v3.md, acrescentado depois do teste a pedido da revisão): as primeiras
    # decisões do TC v3 e do controle comparadas por consulta, como se fossem respostas finais.
    if derivar and "tc3" in dados and "se3" in dados:
        prim = {k: [dict(x, predito=pd, chamou_ferramenta=pd is not None)
                    for x in dados[k]["linhas"] if (pd := primeira_decisao(x)) is not SEM_TRACO]
                for k in ("tc3", "se3")}
        if prim["tc3"] and prim["se3"]:
            pares["tc3se3primeira"] = {"grupo": "exploratorio", "a": "tc3", "b": "se3",
                                       **lote.comparar(prim["tc3"], prim["se3"])}
    decomposicao = {k: decompor(dados[k]["linhas"]) for k in decompostas if k in dados}
    for k, d in decomposicao.items():
        if d.get("sem_traco"):
            avisos.append(f"{k}: {d['sem_traco']} execução(ões) sem traço, fora da decomposição")
        if d.get("truncadas_sem_reconstrucao"):
            avisos.append(f"{k}: {d['truncadas_sem_reconstrucao']} mensagem(ns) do traço cortada(s) em "
                          f"{_LIMITE_TRACO} caracteres sem reconstrução (classificadas pelo trecho gravado)")
    return {"rodadas": {k: {c: v[c] for c in ("pasta", "descartadas", "n_conjunto", "cobertura")}
                        | {"n": len(v["linhas"])} for k, v in dados.items()},
            "medidas": medidas, "pares": pares, "decomposicao": decomposicao,
            "melhor_isolada": {"config": melhor, "nome": nome(melhor), "acuracia": medidas[melhor]["acuracia"],
                               "f1": medidas[melhor]["f1"]} if melhor else None}


def gerar(diretorio: Path, dataset: Path, dir_310: Path | None, dataset_310: Path = DATASET_310,
          extensao: bool = False) -> dict[str, Any]:
    avisos: list[str] = []
    dados = carregar_rodadas(diretorio, dataset, CONFIGS, avisos)
    res: dict[str, Any] = {"dir": _mostrar(diretorio), "dataset": _mostrar(dataset),
                           "n_conjunto": next((v["n_conjunto"] for v in dados.values()), None),
                           "presentes": list(dados), "ausentes": [k for k in CONFIGS if k not in dados]}
    if extensao:
        res.update(analisar(dados, GRUPOS_PARES_EXTENSAO, DECOMPOSTAS_EXTENSAO, avisos, derivar=False))
    else:
        res.update(analisar(dados, GRUPOS_PARES, DECOMPOSTAS, avisos))
    res["avisos"] = avisos
    if dir_310 is not None:
        av310: list[str] = []
        d310 = carregar_rodadas(dir_310, dataset_310, CONFIGS_310, av310)
        if d310:
            r310 = analisar(d310, [("principal", PAR_PRINCIPAL)], CONFIGS_310, av310, derivar=False)
            res["desenvolvimento_310"] = {"dir": _mostrar(dir_310), "dataset": _mostrar(dataset_310),
                                          "n_conjunto": next(iter(d310.values()))["n_conjunto"],
                                          "presentes": list(d310), **r310, "avisos": av310}
        else:
            res["desenvolvimento_310"] = None
        avisos += [f"310: {a}" for a in av310]
    return res


# ---------------------------------------------------------------------------
# Macros
# ---------------------------------------------------------------------------

def _macros_conjunto(put, ns: str, r: dict[str, Any]) -> None:
    fmt = report._pct
    for k, m in r["medidas"].items():
        lote.macros_config(put, ns, k, m)
        put(ns, k, "acuraciaen", fmt(m["acuracia"]).replace(",", "."))   # para o abstract, em inglês
        for efeito, (num, den) in m["efeitos"].items():
            put(ns, k, efeito, fmt(num / den) if den else "---")
            put(ns, k, efeito + "n", f"{num}/{lote._milhar(den)}")
        if m.get("chamadas") is not None:
            put(ns, k, "chamadas", report._num(m["chamadas"], 2))
        if "chamadas_em_texto_nao_interpretadas" in m:
            put(ns, k, "chamadastexto", str(m["chamadas_em_texto_nao_interpretadas"]))
        x = m.get("v3")
        if x:
            put(ns, k, "contestadas", str(x["contestadas"]))
            for chave, v in x["contestadas_detalhe"].items():
                put(ns, k, "contestadas" + chave.replace("_", ""), str(v))
            if x["com_pergunta"] is not None:
                put(ns, k, "compergunta", str(x["com_pergunta"]))
                put(ns, k, "comperguntapct", fmt(x["com_pergunta"] / x["n"]) if x["n"] else "---")
                put(ns, k, "perguntastexto", str(x["com_pergunta_em_texto"]))
                put(ns, k, "chamadastexto", str(x["com_chamada_em_texto"]))
                put(ns, k, "chamadastextopct", fmt(x["com_chamada_em_texto"] / x["n"]) if x["n"] else "---")
                put(ns, k, "chamadastextocertas", str(x["com_chamada_em_texto_certa"]))
                put(ns, k, "chamadastextocertaspct", fmt(x["com_chamada_em_texto_certa"] / x["com_chamada_em_texto"])
                    if x["com_chamada_em_texto"] else "---")
    melhor = r.get("melhor_isolada")
    if melhor:
        lote.macros_config(put, ns, "melhor", r["medidas"][melhor["config"]])
        put(ns, "melhor", "config", melhor["config"])
        put(ns, "melhor", "nome", melhor["nome"])
    for chave, cmp in r["pares"].items():
        lote.macros_par(put, ns, chave, cmp)
        put(ns, chave, "n", lote._milhar(cmp["n"]))
        put(ns, chave, "diff1", report._f(cmp["dif_f1"]))           # os nomes do plano (= diff, icdiff)
        put(ns, chave, "icdiff1", f"{report._f(cmp['ic_dif_f1'][0])} a {report._f(cmp['ic_dif_f1'][1])}")
    for k, d in r["decomposicao"].items():
        n = d.get("n", 0)
        put(ns, k, "decn", lote._milhar(n))
        if not n:
            continue
        put(ns, k, "primeira", fmt(d.get("primeira", 0) / n))
        put(ns, k, "primeiran", lote._razao(d.get("primeira", 0), n))
        put(ns, k, "final", fmt(d.get("final", 0) / n))
        put(ns, k, "finaln", lote._razao(d.get("final", 0), n))
        put(ns, k, "ganhoretorno", lote._pp((d.get("final", 0) - d.get("primeira", 0)) / n))
        put(ns, k, "consertou", str(d.get("consertou", 0)))
        put(ns, k, "estragou", str(d.get("estragou", 0)))
        put(ns, k, "comretorno", str(d.get("com_retorno", 0)))
        for cat in (*CATEGORIAS_RETORNO, SEM_MENSAGEM, "remover_forma"):
            v = d.get("consertou_" + cat, 0)
            put(ns, k, "consertou" + cat.replace("_", ""), str(v))
            put(ns, k, "consertou" + cat.replace("_", "") + "pct",
                fmt(v / d["consertou"]) if d.get("consertou") else "---")
        put(ns, k, "estragouerroinfra", str(d.get("estragou_erro_infra", 0)))
        for cat in CATEGORIAS_RETORNO:
            put(ns, k, "recebeu" + cat, str(d.get("recebeu_" + cat, 0)))


def macros(res: dict[str, Any], sufixo: str = SUFIXO_PADRAO, rotulo_310: str = ROTULO_310) -> str:
    defs: dict[str, str] = {}

    def put(rodada: str, chave: str, medida: str, valor: str) -> None:
        defs[f"res@{rodada}@{chave}@{medida}"] = valor

    if res.get("n_conjunto") is not None:
        put(sufixo, "conjunto", "n", lote._milhar(res["n_conjunto"]))
    _macros_conjunto(put, sufixo, res)
    d = res.get("desenvolvimento_310")
    if d:
        put(rotulo_310, "conjunto", "n", lote._milhar(d["n_conjunto"]))
        _macros_conjunto(put, rotulo_310, d)
    return lote.texto_macros(defs, "pfc_busca.evaluation.lote2")


# ---------------------------------------------------------------------------
# Tabelas
# ---------------------------------------------------------------------------

def _tex(s: str) -> str:
    return s.replace("\\", "/").replace("_", r"\_").replace("%", r"\%").replace("&", r"\&").replace("#", r"\#")


def _eh_lote2(res: dict[str, Any]) -> bool:
    return (res.get("dataset") or "").endswith("lote_validacao_2.json")


def _simulacao(res: dict[str, Any]) -> str:
    """Aviso no título quando o conjunto não é o lote 2 (teste do código com dados de desenvolvimento)."""
    return "" if _eh_lote2(res) else f"[SIMULAÇÃO com {_tex(Path(res.get('dataset') or '').name)}, não é o lote 2] "


def _conjunto_tex(res: dict[str, Any]) -> str:
    n = res.get("n_conjunto")
    n_txt = f"n = {lote._milhar(n)} consultas" if n is not None else "sem rodadas"
    if _eh_lote2(res):
        return f"Lote 2 ({n_txt}; conjunto de teste, nenhuma consulta lida no desenvolvimento)"
    return (f"Conjunto simulado ({n_txt} de \\texttt{{{_tex(Path(res.get('dataset') or '').name)}}}; dados de "
            f"desenvolvimento, só para testar o código)")


def _rotulo(k: str, m: dict, n_conjunto: int | None) -> str:
    return nome(k) + (f", n={lote._milhar(m['n'])}" if n_conjunto is not None and m["n"] != n_conjunto else "")


def _linha_degrau(k: str, m: dict, rotulo_degrau: str, n_conjunto: int | None) -> str:
    fmt, f = report._pct, report._f
    e = m["subespecificadas"]
    cham = report._num(m["chamadas"], 2) if m.get("chamadas") is not None else "---"
    return (f"{rotulo_degrau} & {_rotulo(k, m, n_conjunto)} & {fmt(m['acuracia'])} & "
            f"{fmt(m['ic'][0])}--{fmt(m['ic'][1])} & {fmt(m['accdominio'])} & {f(m['recusa']['f1'])} & "
            f"{fmt(m['recusa']['falsa'])} & {fmt(e['acuracia']) if e['n'] else '---'} & {f(m['f1'])} & "
            f"{report._num((m['latmed'] or 0) / 1000, 2)} & {cham} \\\\")


def tabela_degraus(res: dict[str, Any]) -> str:
    med, n = res["medidas"], res.get("n_conjunto")
    L = [r"\begin{table}[htbp!]", r"\centering",
         r"\caption{" + _simulacao(res) + r"Degraus da v3, controle e referências v1/v2 com o Gemma 4 E4B "
         r"no lote 2 (teste)}", r"\label{tab:lote2_degraus}", r"\footnotesize", r"\ajustartabela{%",
         r"\begin{tabular}{|l|l|c|c|c|c|c|c|c|c|c|}", r"\hline",
         r"\textbf{Degrau} & \textbf{Configuração} & \textbf{Acurácia} & \textbf{IC 95\%} & \textbf{Domínio} & "
         r"\textbf{F1 recusa} & \textbf{Falsa recusa} & \textbf{E} & \textbf{F1 campos} & \textbf{Latência (s)} & "
         r"\textbf{Chamadas} \\", r"\hline"]
    blocos = [["tc1", "tc2", "tc3d", "tc3a", "tc3"], ["se3"], ["se1", "se2", HIB]]
    for bloco in blocos:
        linhas = [_linha_degrau(k, med[k], CONFIGS[k][3] if k in CONFIGS else NOME_HIB[2], n)
                  for k in bloco if k in med]
        if linhas:
            L += linhas + [r"\hline"]
    d = res.get("desenvolvimento_310")
    if d and d["medidas"]:
        n310 = d["n_conjunto"]
        L += [_linha_degrau(k, d["medidas"][k], "310 (desenv.)", n310) for k in CONFIGS_310 if k in d["medidas"]]
        L.append(r"\hline")
    ausentes = [nome(k) for k in CONFIGS if k not in med]
    fonte = (r"Elaborado pelos autores. Gemma 4 E4B (\texttt{gemma4:e4b-it-qat}), GPU T4, uma repetição, data de "
             rf"referência 2026-09-24. {_conjunto_tex(res)}: rodadas em \texttt{{{_tex(res['dir'])}}}, repontuadas "
             rf"contra \texttt{{{_tex(Path(res['dataset']).name)}}}, uma execução por consulta; n=\ldots{{}} ao lado "
             r"do nome: rodada com menos consultas que o conjunto. Degraus: cada configuração acrescenta uma peça à "
             r"anterior (0: v1; "
             r"1: v2; 2: descrições v3; 3: ferramentas auxiliares e usuário simulado; 4: retorno do validador e "
             r"recusa contestada). Controle: Saída Estruturada com as descrições v3 e o mesmo retorno, sem as "
             r"ferramentas no meio da resposta. Duas etapas: simulação \textit{post hoc} com as rodadas do próprio "
             r"lote 2 (o \textit{Tool Calling} v2 decide se busca; quando busca, valem os parâmetros da Saída "
             r"Estruturada v1; latência somada). Acurácia por consulta, com IC de Wilson. Domínio: acurácia fora das "
             r"categorias F e E. F1 recusa: média harmônica da precisão e do recall da recusa em F. Falsa recusa: "
             r"proporção das consultas do domínio sem busca. E: acurácia nas subespecificadas (buscar sem filtros "
             r"ou não buscar). F1 campos: F1 ponderado dos campos. Latência: mediana por consulta, com todas as "
             r"chamadas ao modelo. Chamadas: média de chamadas ao modelo por consulta (v1 e v2: uma por "
             r"construção; duas etapas: uma ou duas).")
    if d and d["medidas"]:
        fonte += (rf" As linhas 310 (desenv.) são de desenvolvimento: as 310 consultas "
                  rf"(n = {lote._milhar(d['n_conjunto'])}; rodadas em \texttt{{{_tex(d['dir'])}}}) orientaram o "
                  r"desenho das descrições, das ferramentas e do validador, e o resultado nelas é de dentro da "
                  r"amostra, otimista por construção.")
    if ausentes:
        fonte += " Sem rodada: " + "; ".join(ausentes) + "."
    L += [r"\end{tabular}}", r"\fonte{" + fonte + "}", r"\end{table}", ""]
    return "\n".join(L)


def _nome_par(cmp: dict[str, Any], melhor: str | None) -> str:
    def lado(k: str) -> str:
        if k == "melhor":
            return f"Melhor v1/v2 isolada ({nome(melhor, True)})" if melhor else "Melhor v1/v2 isolada"
        return nome(k, True)
    return f"{lado(cmp['a'])} $\\times$ {lado(cmp['b'])}"


def _linha_par(grupo: str, cmp: dict[str, Any], melhor: str | None) -> str:
    return (f"{grupo} & {_nome_par(cmp, melhor)} & {lote._milhar(cmp['n'])} & {cmp['so_a']} & {cmp['so_b']} & "
            f"{lote._p(cmp['p'])} & {lote._pp(cmp['dif_acc'])} p.p. ({lote._ic_pp(cmp['ic_dif_acc'])}) & "
            f"{report._f(cmp['dif_f1'])} ({report._f(cmp['ic_dif_f1'][0])} a {report._f(cmp['ic_dif_f1'][1])}) \\\\")


def tabela_pares(res: dict[str, Any]) -> str:
    melhor = (res.get("melhor_isolada") or {}).get("config")
    rotulos = {"principal": "Principal", "degraus": "Degraus", "secundarios": "Secundárias"}
    L = [r"\begin{table}[htbp!]", r"\centering",
         r"\caption{" + _simulacao(res) + r"Comparações pareadas no lote 2 (Gemma 4 E4B)}",
         r"\label{tab:lote2_pares}", r"\footnotesize", r"\ajustartabela{%",
         r"\begin{tabular}{|l|l|c|c|c|c|c|c|}", r"\hline",
         r"\textbf{Comparação} & \textbf{Par (A $\times$ B)} & \textbf{n} & \textbf{Só A} & \textbf{Só B} & "
         r"\textbf{\textit{p}} & \textbf{B $-$ A, acurácia (IC)} & \textbf{B $-$ A, F1 (IC)} \\", r"\hline"]
    for grupo, _ in GRUPOS_PARES:
        linhas = [_linha_par(rotulos[grupo], c, melhor) for c in res["pares"].values() if c["grupo"] == grupo]
        if linhas:
            L += linhas + [r"\hline"]
    d = res.get("desenvolvimento_310")
    if d and d["pares"]:
        L += [_linha_par("310 (desenv.)", c, None) for c in d["pares"].values()] + [r"\hline"]
    fonte = (r"Elaborado pelos autores. Plano de análise fixado antes da rodada (\texttt{docs/v3.md}). "
             rf"{_conjunto_tex(res)}: rodadas em \texttt{{{_tex(res['dir'])}}}; n: consultas presentes nas duas "
             r"configurações (as "
             r"comparações usam só essas). Só A / Só B: consultas em que só uma das configurações acerta. "
             r"\textit{p}: McNemar exato, uma observação por consulta. IC: bootstrap pareado (2.000 reamostragens "
             r"das consultas, semente 42), percentis 2,5 e 97,5; F1: F1 ponderado dos campos. Melhor v1/v2 isolada: "
             r"a de maior acurácia no lote 2 entre TC v1, SE v1, TC v2 e SE v2"
             + (f" ({nome(melhor)})" if melhor else "") + r". Duas etapas: simulação \textit{post hoc} (TC v2 "
             r"decide, SE v1 extrai). TC: \textit{Tool Calling}; SE: Saída Estruturada.")
    if d and d["pares"]:
        fonte += (r" 310 (desenv.): as 310 consultas de desenvolvimento, dentro da amostra que orientou a v3 "
                  r"(não é resultado de teste).")
    L += [r"\end{tabular}}", r"\fonte{" + fonte + "}", r"\end{table}", ""]
    return "\n".join(L)


_LINHAS_DECOMPOSICAO = [
    ("Consultas com traço", lambda d, n: lote._milhar(n)),
    ("Acurácia da primeira decisão", lambda d, n: report._pct(d.get("primeira", 0) / n)),
    ("Acurácia final", lambda d, n: report._pct(d.get("final", 0) / n)),
    ("Final $-$ primeira (p.p.)", lambda d, n: lote._pp((d.get("final", 0) - d.get("primeira", 0)) / n)),
    ("Consertadas pelo retorno", lambda d, n: str(d.get("consertou", 0))),
    (r"\quad dando o valor", lambda d, n: str(d.get("consertou_valor", 0))),
    (r"\quad mandando remover um campo", lambda d, n: str(d.get("consertou_remover", 0))),
    (r"\quad corrigindo a forma", lambda d, n: str(d.get("consertou_forma", 0))),
    (r"\quad apontando o campo, sem o valor", lambda d, n: str(d.get("consertou_aponta", 0))),
    (r"\quad contestando a recusa", lambda d, n: str(d.get("consertou_contestada", 0))),
    ("Estragadas pelo retorno", lambda d, n: str(d.get("estragou", 0))),
]


def tabela_decomposicao(res: dict[str, Any]) -> str:
    colunas = [(nome(k, True), res["decomposicao"][k]) for k in DECOMPOSTAS if k in res["decomposicao"]]
    d310 = res.get("desenvolvimento_310") or {}
    colunas += [(nome(k, True) + " (310, desenv.)", d310["decomposicao"][k])
                for k in CONFIGS_310 if k in (d310.get("decomposicao") or {})]
    colunas = [(c, d) for c, d in colunas if d.get("n")]
    L = [r"\begin{table}[htbp!]", r"\centering",
         r"\caption{" + _simulacao(res) + r"Decomposição do acerto no lote 2 entre a primeira decisão do modelo e "
         r"a correção pelo retorno do código}", r"\label{tab:lote2_decomposicao}", r"\footnotesize",
         r"\ajustartabela{%", r"\begin{tabular}{|l|" + "c|" * max(1, len(colunas)) + "}", r"\hline",
         r"\textbf{Medida} & " + (" & ".join(rf"\textbf{{{c}}}" for c, _ in colunas) or "---") + r" \\", r"\hline"]
    for rotulo, f in _LINHAS_DECOMPOSICAO:
        L.append(f"{rotulo} & " + (" & ".join(f(d, d["n"]) for _, d in colunas) or "---") + r" \\")
        if rotulo in ("Final $-$ primeira (p.p.)", r"\quad contestando a recusa"):
            L.append(r"\hline")
    if any(d.get("estragou_erro_infra") for _, d in colunas):
        L.append(r"\quad por erro de infraestrutura (não pelo retorno) & "
                 + " & ".join(str(d.get("estragou_erro_infra", 0)) for _, d in colunas) + r" \\")
    L.append(r"\hline")
    fonte = (r"Elaborado pelos autores. Gemma 4 E4B. " + _conjunto_tex(res) + r": rodadas em \texttt{"
             + _tex(res["dir"]) + r"}. "
             r"Primeira decisão: os parâmetros da primeira chamada a \texttt{buscar\_catalogo}, ou a recusa, se veio "
             r"antes de qualquer busca (no \textit{Tool Calling}, pelo traço gravado; na Saída Estruturada, o "
             r"primeiro objeto do histórico de tentativas), pontuada com o mesmo gabarito da resposta final. "
             r"Consertadas: primeira decisão errada e final certa; estragadas: o contrário. Cada consertada é "
             r"atribuída ao retorno mais informativo que recebeu antes da decisão final, pelas mensagens gravadas "
             r"do validador: dando o valor (a UF ou o município citados, as datas pela tabela do manual, o código "
             r"ou a escala na forma canônica, o município do IBGE); mandando remover um campo sem evidência na "
             r"consulta; corrigindo a forma (valor fora do enumerado, período malformado, objeto fora do "
             r"\textit{schema}); apontando o campo a preencher ou a trocar, sem o valor; contestando a recusa de uma "
             r"consulta que cita critério do catálogo. No TC v3a não há validação: o retorno é só o da chamada "
             r"malformada.")
    if any("310" in c for c, _ in colunas):
        fonte += (r" Colunas 310: consultas de desenvolvimento, dentro da amostra que orientou a v3 (não é "
                  r"resultado de teste).")
    L += [r"\end{tabular}}", r"\fonte{" + fonte + "}", r"\end{table}", ""]
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Relatório em Markdown
# ---------------------------------------------------------------------------

def _md_medidas(med: dict[str, dict]) -> list[str]:
    pct = report._pct_md
    cols = [k for k in (*CONFIGS, HIB) if k in med]
    if not cols:
        return ["(nenhuma rodada)", ""]

    def linha(rotulo: str, f) -> str:
        return f"| {rotulo} | " + " | ".join(f(med[k]) for k in cols) + " |"

    def efeito(nome_efeito: str):
        def f(m):
            num, den = m["efeitos"][nome_efeito]
            return f"{pct(num / den) if den else '—'} ({num}/{den})"
        return f

    def v3x(chave: str):
        return lambda m: "—" if not m.get("v3") or m["v3"].get(chave) is None else str(m["v3"][chave])

    L = ["| Medida | " + " | ".join(nome(k, True) for k in cols) + " |", "|---|" + "---|" * len(cols),
         linha("Consultas", lambda m: str(m["n"])),
         linha("Acurácia [IC 95%]", lambda m: f"{pct(m['acuracia'])} [{pct(m['ic'][0])}–{pct(m['ic'][1])}]"),
         linha("Acurácia no domínio (fora de F e E)", lambda m: pct(m["accdominio"])),
         linha("Recusa em F: precisão / recall / F1", lambda m: f"{pct(m['recusa']['precisao'])} / "
               f"{pct(m['recusa']['recall'])} / {m['recusa']['f1']:.3f}"),
         linha("Falsa recusa (domínio)", lambda m: pct(m["recusa"]["falsa"])),
         linha("E: acurácia (buscou sem filtros / não buscou / com filtro)", lambda m: (
             f"{pct(m['subespecificadas']['acuracia'])} ({m['subespecificadas']['sem_parametros']} / "
             f"{m['subespecificadas']['nao_buscou']} / {m['subespecificadas']['com_parametros']})")
             if m["subespecificadas"]["n"] else "—"),
         linha("F1 ponderado dos campos", lambda m: f"{m['f1']:.3f}"),
         linha("Efeito: sigla em state", efeito("sigla")),
         linha("Efeito: prefixo no código", efeito("prefixo")),
         linha("Efeito: limit sem pedido", efeito("limite")),
         linha("Efeito: productType sem pedido", efeito("tipo")),
         linha("Latência mediana / p95 (s)", lambda m: f"{(m['latmed'] or 0) / 1000:.2f} / {(m['latp95'] or 0) / 1000:.2f}"),
         linha("Chamadas ao modelo por consulta", lambda m: "—" if m.get("chamadas") is None else f"{m['chamadas']:.2f}"),
         linha("Consultas com pergunta", v3x("com_pergunta")),
         linha("Consultas com pergunta em texto", v3x("com_pergunta_em_texto")),
         linha("Recusas contestadas", v3x("contestadas")),
         linha("Consultas com chamada escrita como texto (v3: interpretada)", lambda m: (
             str(m["v3"]["com_chamada_em_texto"]) if m.get("v3") and m["v3"].get("com_chamada_em_texto") is not None
             else str(m["chamadas_em_texto_nao_interpretadas"]) + " (não interpretada)"
             if "chamadas_em_texto_nao_interpretadas" in m else "—")),
         linha("Respostas fora do schema / erros de infraestrutura",
               lambda m: f"{m['fora_do_schema']} / {m['erros_infra']}"), ""]
    return L


def _md_pares(pares: dict[str, dict], melhor: str | None) -> list[str]:
    if not pares:
        return ["(nenhum par)", ""]
    L = ["| Grupo | Par (A × B) | n | Só A | Só B | p (McNemar) | B − A, acurácia [IC] | B − A, F1 [IC] |",
         "|---|---|---|---|---|---|---|---|"]
    for c in pares.values():
        a = f"melhor isolada ({nome(melhor, True)})" if c["a"] == "melhor" and melhor else nome(c["a"], True)
        L.append(f"| {c['grupo']} | {a} × {nome(c['b'], True)} | {c['n']} | {c['so_a']} | {c['so_b']} | {c['p']:.4g} | "
                 f"{100 * c['dif_acc']:+.1f} p.p. [{100 * c['ic_dif_acc'][0]:+.1f}, {100 * c['ic_dif_acc'][1]:+.1f}] | "
                 f"{c['dif_f1']:+.3f} [{c['ic_dif_f1'][0]:+.3f}, {c['ic_dif_f1'][1]:+.3f}] |")
    return L + [""]


def _md_decomposicao(dec: dict[str, dict]) -> list[str]:
    cols = [k for k in dec if dec[k].get("n")]
    if not cols:
        return ["(sem traço para decompor)", ""]
    chaves = [("n (com traço)", "n"), ("sem traço", "sem_traco"), ("primeira decisão certa", "primeira"),
              ("final certa", "final"), ("consertadas", "consertou"), ("  dando o valor", "consertou_valor"),
              ("  mandando remover", "consertou_remover"), ("  corrigindo a forma", "consertou_forma"),
              ("  apontando o campo", "consertou_aponta"), ("  recusa contestada", "consertou_contestada"),
              ("  remover ou forma (o agregado do plano)", "consertou_remover_forma"),
              ("  sem mensagem", "consertou_sem_mensagem"), ("estragadas", "estragou"),
              ("  por erro de infraestrutura (não pelo retorno)", "estragou_erro_infra"),
              ("execuções com erro de infraestrutura", "erro_infra"),
              ("consertadas que receberam valor", "recebeu_valor"),
              ("consertadas que receberam remover", "recebeu_remover"),
              ("consertadas que receberam forma", "recebeu_forma"),
              ("consertadas que receberam aponta", "recebeu_aponta"),
              ("consultas com algum retorno", "com_retorno"), ("recusas contestadas", "contestadas"),
              ("mensagens do traço refeitas pelo validador", "refeitas"),
              ("mensagens do traço truncadas sem reconstrução", "truncadas_sem_reconstrucao")]
    L = ["| Contagem | " + " | ".join(nome(k, True) for k in cols) + " |", "|---|" + "---|" * len(cols)]
    for rotulo, ch in chaves:
        L.append(f"| {rotulo} | " + " | ".join(str(dec[k].get(ch, 0)) for k in cols) + " |")
    L.append("| acurácia: primeira → final | " + " | ".join(
        f"{report._pct_md(dec[k].get('primeira', 0) / dec[k]['n'])} → {report._pct_md(dec[k].get('final', 0) / dec[k]['n'])}"
        for k in cols) + " |")
    return L + [""]


def relatorio_md(res: dict[str, Any]) -> str:
    melhor = (res.get("melhor_isolada") or {}).get("config")
    titulo = f"# Lote 2 — teste da v3 ({MODELO})"
    if not _eh_lote2(res):
        titulo += f" — SIMULAÇÃO com {Path(res['dataset']).name}, não é o lote 2"
    L = [titulo, "", "Gerado por `python -m pfc_busca.evaluation.lote2`. Plano de análise: `docs/v3.md`, seção 3 "
         "(fixado antes da rodada). Regras da decomposição: `pfc_busca/evaluation/lote2.py`.", "",
         f"- Conjunto: `{res['dataset']}` ({res.get('n_conjunto')} consultas, fora as observacionais).",
         f"- Rodadas: `{res['dir']}` — presentes: {', '.join(res['presentes']) or 'nenhuma'}; "
         f"ausentes: {', '.join(res['ausentes']) or 'nenhuma'}.",
         f"- Melhor configuração v1/v2 isolada (maior acurácia): "
         f"{nome(melhor) + f' ({melhor})' if melhor else '—'}.", ""]
    if res["rodadas"]:
        L += ["| Rodada | Pasta | Consultas | Cobertura | Descartadas na repontuação |", "|---|---|---|---|---|"]
        for k, r in res["rodadas"].items():
            L.append(f"| {k} | `{r['pasta']}` | {r['n']} | {report._pct_md(r['cobertura'])} | {r['descartadas']} |")
        L.append("")
    if res.get("avisos"):
        L += ["Avisos:", ""] + [f"- {a}" for a in res["avisos"]] + [""]
    L += ["## Medidas por configuração", ""] + _md_medidas(res["medidas"])
    L += ["## Pares (só as consultas presentes nas duas configurações)", ""] + _md_pares(res["pares"], melhor)
    L += ["## Decomposição do acerto", ""] + _md_decomposicao(res["decomposicao"])
    d = res.get("desenvolvimento_310")
    if d:
        L += ["## 310 consultas — desenvolvimento (dentro da amostra; não é resultado de teste)", "",
              f"- Conjunto: `{d['dataset']}` ({d['n_conjunto']} consultas); rodadas: `{d['dir']}` "
              f"({', '.join(d['presentes'])}).", ""]
        L += _md_medidas(d["medidas"]) + _md_pares(d["pares"], None) + _md_decomposicao(d["decomposicao"])
    return "\n".join(L)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--dir", type=Path, default=DIR_RESULTADOS / "lote2", help="pasta das rodadas do lote 2")
    p.add_argument("--dataset", type=Path, default=RAIZ_REPO / "data" / "lote_validacao_2.json",
                   help="dataset contra o qual as rodadas são repontuadas")
    p.add_argument("--dir-310", type=Path, default=DIR_RESULTADOS / "v3_310",
                   help="pasta das rodadas tc3-/se3- nas 310 consultas (desenvolvimento)")
    p.add_argument("--paper", type=Path,
                   help="diretório do texto (grava as .tex também em DIR/tabelas; só com o dataset do lote 2)")
    p.add_argument("--sufixo-macro", default=SUFIXO_PADRAO,
                   help="rótulo das macros \\res{<sufixo>}{...}; o das 310 é v3base + o que vier depois de 'lote2'")
    p.add_argument("--modelo", default=None,
                   help="tag de outro modelo (extensão; ex.: gemma4:e2b-it-qat): só a comparação principal, o ganho "
                        "sobre a v1 e o A/B da v1; grava só numeros_<sufixo>.tex, sem as tabelas do teste principal")
    args = p.parse_args(argv)
    global MODELO
    extensao = bool(args.modelo) and slug(args.modelo) != lote.MODELO
    if extensao:
        MODELO = slug(args.modelo)
        if args.sufixo_macro == SUFIXO_PADRAO:
            args.sufixo_macro = sufixo_extensao(args.modelo)
        args.dir_310 = None
    if not args.dataset.exists():
        print(f"dataset não encontrado: {args.dataset}")
        return 2
    sufixo = args.sufixo_macro
    rotulo_310 = ROTULO_310 + (sufixo[len(SUFIXO_PADRAO):] if sufixo.startswith(SUFIXO_PADRAO) else sufixo)
    res = gerar(args.dir, args.dataset, args.dir_310, extensao=extensao)
    for a in res["avisos"]:
        print(f"aviso: {a}")
    if args.paper and not _eh_lote2(res):
        # as tabelas tab_lote2_*.tex têm nome fixo: uma simulação não pode sobrescrever as do texto
        print(f"aviso: --paper ignorado (o dataset {args.dataset.name} não é o lote 2; saída só em DIR/consolidado)")
        args.paper = None
    if not res["medidas"] and not res.get("desenvolvimento_310"):
        print(f"nenhuma rodada encontrada em {args.dir} nem em {args.dir_310}")
        return 0
    saida = args.dir / "consolidado"
    saida.mkdir(parents=True, exist_ok=True)
    arquivos = {f"numeros_{sufixo}.tex": macros(res, sufixo, rotulo_310)}
    if not extensao:
        arquivos |= {"tab_lote2_degraus.tex": tabela_degraus(res), "tab_lote2_pares.tex": tabela_pares(res),
                     "tab_lote2_decomposicao.tex": tabela_decomposicao(res)}
    for nome_arq, conteudo in arquivos.items():
        (saida / nome_arq).write_text(conteudo, encoding="utf-8")
        if args.paper:
            (args.paper / "tabelas").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(saida / nome_arq, args.paper / "tabelas" / nome_arq)
    base = "lote2" if not extensao else sufixo
    (saida / f"{base}.md").write_text(relatorio_md(res), encoding="utf-8")
    (saida / f"{base}.json").write_text(json.dumps(lote._serializavel(res), ensure_ascii=False, indent=1),
                                        encoding="utf-8")
    resumo = ", ".join(f"{k} {m['n']}" for k, m in res["medidas"].items())
    d = res.get("desenvolvimento_310")
    if d:
        resumo += " | 310: " + ", ".join(f"{k} {m['n']}" for k, m in d["medidas"].items())
    print(f"lote2 ({resumo}) -> {saida}" + (f" e {args.paper / 'tabelas'}" if args.paper else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
