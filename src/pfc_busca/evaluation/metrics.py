"""Métricas do protocolo (Cap. 2, §Métricas; Cap. 3, §Cálculo das Métricas).

Definições, na letra do texto:

- **Acurácia por consulta**: 1 se TODOS os parâmetros extraídos correspondem
  exatamente ao gabarito (nem a mais, nem a menos); 0 caso contrário. Para
  consultas em que o gabarito é "não chamar ferramenta", correta = não chamou.
- **Por campo**: TP quando o campo é extraído e corresponde; FP quando é
  extraído mas não corresponde OU não deveria ter sido extraído; FN quando
  está no gabarito e não foi extraído. Um valor errado conta, portanto,
  como FP (e não como FN) — é a definição do Cap. 3 e é reportada assim.
- **Comparação** (Cap. 2, "Nota sobre o critério de comparação"): enums e
  ordenação exigem igualdade exata; strings livres (keyword, state, city) são
  normalizadas (minúsculas, sem acento, sem pontuação); períodos exigem
  coincidência exata dos limites ISO; limit é inteiro.
- **F1 médio ponderado**: peso de cada campo = nº de ocorrências do campo no
  gabarito do conjunto avaliado.
- **Latência**: mín, máx, média, mediana, desvio-padrão (e p95), decomposta
  em tempo do LLM e tempo da ferramenta.
- **Leituras múltiplas** (manual de anotação, P3): um campo pode aceitar mais de um
  valor (`$um_de`), pode ser opcional (`$opcional`) e o caso pode ter leituras
  estruturais alternativas. A resposta é comparada com cada leitura aceita e avaliada
  contra a de melhor casamento: correta se coincidir com alguma. Campos opcionais
  ausentes não contam como FN.

Diagnósticos adicionais (fora das tabelas principais, úteis na análise de
erros): IoU de períodos, taxa de campos inventados fora do schema, taxa de
tool calls rejeitadas/malformadas.
"""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from pfc_busca import schema
from pfc_busca.evaluation.gabarito import eh_opcional, valores_aceitos

CAMPO_FORA_DO_SCHEMA = "__fora_do_schema__"

# Classes de erro de INFRAESTRUTURA (a chamada não completou): só estas excluem a
# linha das estatísticas de latência. `args_invalidos` e `ferramenta_inexistente`
# são erros DO MODELO -- a chamada completou e a latência é real.
CLASSES_ERRO_INFRA = frozenset({"timeout", "indisponivel", "falha"})


def erro_de_infra(linha: dict[str, Any]) -> bool:
    return bool(linha.get("erro")) and linha.get("classe_erro") in CLASSES_ERRO_INFRA


# ---------------------------------------------------------------------------
# Comparação campo a campo
# ---------------------------------------------------------------------------

def _periodo_ok(valor: Any) -> bool:
    return isinstance(valor, dict) and set(valor) <= {"start", "end"} and bool(valor)


def campo_igual(campo: str, esperado: Any, predito: Any) -> bool:
    """Igualdade de um campo segundo o critério do Cap. 2."""
    if campo in schema.CAMPOS_TEXTO_LIVRE:
        return (isinstance(predito, str) and isinstance(esperado, str)
                and schema.normalizar_texto(predito) == schema.normalizar_texto(esperado))
    if campo in schema.CAMPOS_PERIODO:
        if not (_periodo_ok(esperado) and _periodo_ok(predito)):
            return False
        return {k: str(v) for k, v in esperado.items()} == {k: str(v) for k, v in predito.items()}
    if campo in schema.CAMPOS_INTEIRO:
        return isinstance(predito, int) and not isinstance(predito, bool) and predito == esperado
    # enums e ordenação: exato
    return isinstance(predito, str) and predito == esperado


def iou_periodo(esperado: Any, predito: Any) -> float | None:
    """Interseção sobre união, em dias, de dois intervalos fechados.

    None quando algum lado não tem os dois limites (não dá para medir).
    """
    if not (_periodo_ok(esperado) and _periodo_ok(predito)):
        return None
    try:
        e0, e1 = date.fromisoformat(esperado["start"]), date.fromisoformat(esperado["end"])
        p0, p1 = date.fromisoformat(str(predito["start"])), date.fromisoformat(str(predito["end"]))
    except (KeyError, ValueError):
        return None
    inter = (min(e1, p1) - max(e0, p0)).days + 1
    uniao = (max(e1, p1) - min(e0, p0)).days + 1
    if uniao <= 0:
        return None
    return max(0, inter) / uniao


def valor_aceito(campo: str, esperado: Any, predito: Any) -> bool:
    """`predito` coincide com algum valor aceito do campo (desembrulha $um_de/$opcional)."""
    return any(campo_igual(campo, e, predito) for e in valores_aceitos(esperado))


def melhor_iou(esperado: Any, predito: Any) -> float | None:
    valores = [iou_periodo(e, predito) for e in valores_aceitos(esperado)]
    valores = [v for v in valores if v is not None]
    return max(valores) if valores else None


@dataclass
class AvaliacaoCaso:
    correto: bool
    tp: set[str] = field(default_factory=set)
    fp: set[str] = field(default_factory=set)
    fn: set[str] = field(default_factory=set)
    fora_do_schema: set[str] = field(default_factory=set)
    iou_periodos: dict[str, float] = field(default_factory=dict)
    # campos que contam como ocorrência no gabarito (obrigatórios + opcionais emitidos)
    ocorrencias: set[str] = field(default_factory=set)
    # índice da leitura aceita contra a qual a resposta foi avaliada (0 = preferencial)
    leitura: int = 0
    # rótulo curto para a análise de erros
    tipo_erro: str | None = None


def _tipo_erro(aval: AvaliacaoCaso, esperado: dict[str, Any]) -> str | None:
    if aval.correto:
        return None
    if aval.fora_do_schema:
        return "campo_fora_do_schema"
    if aval.fp and aval.fn:
        return "misto"
    if aval.fp and aval.fp - set(esperado):
        return "campo_inventado"
    if aval.fp:
        return "valor_errado"
    return "campo_omitido"


def avaliar_leitura(esperado: dict[str, Any], predito: dict[str, Any]) -> AvaliacaoCaso:
    """Avalia uma resposta (houve tool call) contra UMA leitura do gabarito."""
    aval = AvaliacaoCaso(correto=True)
    for campo in set(esperado) | set(predito):
        if campo not in schema.CAMPOS:
            if campo in predito:
                aval.fora_do_schema.add(campo)
                aval.correto = False
            continue
        esp = esperado.get(campo)
        if campo in esperado and campo in predito:
            aval.ocorrencias.add(campo)
            if valor_aceito(campo, esp, predito[campo]):
                aval.tp.add(campo)
            else:
                aval.fp.add(campo)
                aval.correto = False
            if campo in schema.CAMPOS_PERIODO:
                iou = melhor_iou(esp, predito[campo])
                if iou is not None:
                    aval.iou_periodos[campo] = iou
        elif campo in predito:
            aval.fp.add(campo)
            aval.correto = False
        elif not eh_opcional(esp):
            aval.ocorrencias.add(campo)
            aval.fn.add(campo)
            aval.correto = False
    aval.tipo_erro = _tipo_erro(aval, esperado)
    return aval


def _obrigatorios(esperado: dict[str, Any]) -> set[str]:
    return {c for c, v in esperado.items() if not eh_opcional(v)}


def avaliar_caso(esperado: dict[str, Any], predito: dict[str, Any] | None,
                 espera_tool_call: bool = True,
                 alternativas: list[dict[str, Any]] | None = None,
                 aceita_nao_chamar: bool = False) -> AvaliacaoCaso:
    """Avalia UMA execução contra todas as leituras aceitas do gabarito.

    `predito=None` significa que não houve tool call. Entre as leituras aceitas
    vale a de melhor casamento: primeiro a que torna a resposta correta; depois a
    de maior (TP - FP - FN); empate, a preferencial.
    """
    chamou = predito is not None

    # Gabarito "não chamar ferramenta"
    if not espera_tool_call:
        if not chamou:
            return AvaliacaoCaso(correto=True)
        aval = AvaliacaoCaso(correto=False, tipo_erro="chamou_sem_dever")
        for campo in predito:
            (aval.fp if campo in schema.CAMPOS else aval.fora_do_schema).add(campo)
        return aval

    # Consulta subespecificada (categoria E): não buscar (pedir esclarecimento) também é aceito
    if not chamou and aceita_nao_chamar:
        return AvaliacaoCaso(correto=True)

    if not chamou:
        obrig = _obrigatorios(esperado)
        return AvaliacaoCaso(correto=False, fn=set(obrig), ocorrencias=set(obrig),
                             tipo_erro="nao_chamou")

    leituras = [esperado] + list(alternativas or [])
    melhor: AvaliacaoCaso | None = None
    melhor_chave: tuple | None = None
    for indice, leitura in enumerate(leituras):
        aval = avaliar_leitura(leitura, predito)
        aval.leitura = indice
        chave = (aval.correto, len(aval.tp) - len(aval.fp) - len(aval.fn) - len(aval.fora_do_schema))
        if melhor_chave is None or chave > melhor_chave:
            melhor, melhor_chave = aval, chave
    assert melhor is not None
    return melhor


def avaliar_linha(linha: dict[str, Any]) -> AvaliacaoCaso:
    """Atalho para uma linha de `execucoes.jsonl` (usa as leituras resolvidas da linha)."""
    return avaliar_caso(linha["esperado_resolvido"], linha["predito"], linha["espera_tool_call"],
                        linha.get("alternativas_resolvidas"), bool(linha.get("aceita_nao_chamar")))


# ---------------------------------------------------------------------------
# Agregação
# ---------------------------------------------------------------------------

def precisao_recall_f1(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f1


def estatisticas_latencia(valores: list[float]) -> dict[str, float]:
    if not valores:
        return {}
    ordenados = sorted(valores)
    p95_idx = min(len(ordenados) - 1, round(0.95 * (len(ordenados) - 1)))
    return {
        "n": len(ordenados),
        "min": ordenados[0],
        "max": ordenados[-1],
        "media": statistics.fmean(ordenados),
        "mediana": statistics.median(ordenados),
        "desvio": statistics.pstdev(ordenados) if len(ordenados) > 1 else 0.0,
        "p95": ordenados[p95_idx],
    }


def agregar(linhas: list[dict[str, Any]]) -> dict[str, Any]:
    """Agrega linhas de resultado (uma por consulta × execução) de UM modelo.

    Cada linha precisa de: `esperado_resolvido`, `predito` (dict ou None),
    `espera_tool_call`, `observacional`, `categorias`, `origem`,
    `latencia_llm_ms`, `latencia_tool_ms`, `latencia_total_ms`, `erro`.
    Linhas observacionais entram só no bloco `observacionais`.
    """
    principais = [lin for lin in linhas if not lin.get("observacional")]
    observacionais = [lin for lin in linhas if lin.get("observacional")]

    avaliacoes = [avaliar_linha(lin) for lin in principais]

    tp, fp, fn = Counter(), Counter(), Counter()
    ocorrencias = Counter()
    ious: dict[str, list[float]] = defaultdict(list)
    tipos_erro = Counter()
    fora_schema = Counter()
    for _linha, aval in zip(principais, avaliacoes, strict=True):
        for c in aval.tp:
            tp[c] += 1
        for c in aval.fp:
            fp[c] += 1
        for c in aval.fn:
            fn[c] += 1
        for c in aval.ocorrencias:
            ocorrencias[c] += 1
        for c, v in aval.iou_periodos.items():
            ious[c].append(v)
        for c in aval.fora_do_schema:
            fora_schema[c] += 1
        if aval.tipo_erro:
            tipos_erro[aval.tipo_erro] += 1

    por_campo = {}
    for campo in schema.CAMPOS:
        p, r, f1 = precisao_recall_f1(tp[campo], fp[campo], fn[campo])
        por_campo[campo] = {"tp": tp[campo], "fp": fp[campo], "fn": fn[campo],
                            "ocorrencias": ocorrencias[campo],
                            "precisao": p, "recall": r, "f1": f1}

    peso_total = sum(ocorrencias[c] for c in schema.CAMPOS)
    f1_ponderado = (sum(por_campo[c]["f1"] * ocorrencias[c] for c in schema.CAMPOS) / peso_total
                    if peso_total else 0.0)
    precisao_pond = (sum(por_campo[c]["precisao"] * ocorrencias[c] for c in schema.CAMPOS) / peso_total
                     if peso_total else 0.0)
    recall_pond = (sum(por_campo[c]["recall"] * ocorrencias[c] for c in schema.CAMPOS) / peso_total
                   if peso_total else 0.0)
    campos_com_ocorrencia = [c for c in schema.CAMPOS if ocorrencias[c]]
    f1_macro = (statistics.fmean(por_campo[c]["f1"] for c in campos_com_ocorrencia)
                if campos_com_ocorrencia else 0.0)
    ptp, pfp, pfn = sum(tp.values()), sum(fp.values()), sum(fn.values())
    micro_p, micro_r, micro_f1 = precisao_recall_f1(ptp, pfp, pfn)

    def _acuracia(sub: list[tuple[dict, AvaliacaoCaso]]) -> float | None:
        return (sum(a.correto for _, a in sub) / len(sub)) if sub else None

    pares = list(zip(principais, avaliacoes, strict=True))
    por_categoria = {}
    for cat in ["S", "C", "M", "T", "O", "A", "F", "E"]:
        sub = [(lin, a) for lin, a in pares if cat in lin["categorias"]]
        sub_tp, sub_fp, sub_fn, sub_occ = Counter(), Counter(), Counter(), Counter()
        for _lin, a in sub:
            sub_tp.update(a.tp)
            sub_fp.update(a.fp)
            sub_fn.update(a.fn)
            sub_occ.update(a.ocorrencias)
        peso = sum(sub_occ.values())
        f1_cat = (sum(precisao_recall_f1(sub_tp[c], sub_fp[c], sub_fn[c])[2] * sub_occ[c]
                      for c in schema.CAMPOS) / peso) if peso else 0.0
        por_categoria[cat] = {"n": len(sub), "n_consultas": len({lin["id"] for lin, _ in sub}),
                              "acuracia": _acuracia(sub), "f1_ponderado": f1_cat}

    por_origem = {}
    for origem in ["P", "N", "G"]:
        sub = [(lin, a) for lin, a in pares if lin["origem"] == origem]
        por_origem[origem] = {"n": len(sub), "n_consultas": len({lin["id"] for lin, _ in sub}),
                              "acuracia": _acuracia(sub)}

    erros = [lin for lin in principais if erro_de_infra(lin)]
    erros_modelo = [lin for lin in principais if lin.get("erro") and not erro_de_infra(lin)]
    lat_llm = [lin["latencia_llm_ms"] for lin in principais if lin.get("latencia_llm_ms") is not None and not erro_de_infra(lin)]
    lat_tool = [lin["latencia_tool_ms"] for lin in principais if lin.get("latencia_tool_ms") is not None and not erro_de_infra(lin)]
    lat_total = [lin["latencia_total_ms"] for lin in principais if lin.get("latencia_total_ms") is not None and not erro_de_infra(lin)]

    aval_obs = [(lin, avaliar_linha(lin)) for lin in observacionais]

    return {
        "n_consultas": len(principais),
        "acuracia": _acuracia(pares),
        "precisao_ponderada": precisao_pond,
        "recall_ponderado": recall_pond,
        "f1_ponderado": f1_ponderado,
        "f1_macro": f1_macro,
        "micro": {"precisao": micro_p, "recall": micro_r, "f1": micro_f1,
                  "tp": ptp, "fp": pfp, "fn": pfn},
        "por_campo": por_campo,
        "por_categoria": por_categoria,
        "por_origem": por_origem,
        "latencia_llm_ms": estatisticas_latencia(lat_llm),
        "latencia_tool_ms": estatisticas_latencia(lat_tool),
        "latencia_total_ms": estatisticas_latencia(lat_total),
        "diagnosticos": {
            "tipos_erro": dict(tipos_erro),
            "campos_fora_do_schema": dict(fora_schema),
            "iou_periodos_medio": {c: statistics.fmean(v) for c, v in ious.items()},
            "chamadas_com_erro": len(erros),
            "classes_de_erro": dict(Counter(lin.get("classe_erro") for lin in erros)),
            "respostas_fora_do_schema": len(erros_modelo),
            "classes_fora_do_schema": dict(Counter(lin.get("classe_erro") for lin in erros_modelo)),
            "nao_chamou_quando_devia": sum(1 for lin, a in pares if a.tipo_erro == "nao_chamou"),
            "acertos_em_leitura_alternativa": sum(1 for lin, a in pares if a.correto and a.leitura > 0),
        },
        "observacionais": {
            "n": len(observacionais),
            "acuracia": (sum(a.correto for _, a in aval_obs) / len(aval_obs)) if aval_obs else None,
            "chamou_sem_dever": sum(1 for _, a in aval_obs if a.tipo_erro == "chamou_sem_dever"),
            "por_caso": [{"id": lin["id"], "correto": a.correto, "tipo_erro": a.tipo_erro,
                          "predito": lin["predito"]} for lin, a in aval_obs],
        },
    }
