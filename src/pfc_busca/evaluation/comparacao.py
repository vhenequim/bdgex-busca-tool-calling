"""Tool Calling × Saída Estruturada: tabela e macros da comparação com as linhas de base (Cap. 5).

    python -m pfc_busca.evaluation.comparacao --paper ../paper_revisado
    python -m pfc_busca.evaluation.comparacao --resultados results/estacao --sufixo _estacao --paper ...

Para cada modelo com rodada de Tool Calling e de Saída Estruturada no mesmo diretório de
resultados (`<modelo>/` e `se-<modelo>/`, locais; `groq-<modelo>/` e `groq-se-<modelo>/`, nuvem),
em ordem crescente de tamanho, e para a rodada do método do protótipo
(`prototipo-<modelo>/`), calcula: acurácia (IC de Wilson com n = consultas), acurácia sem a
categoria F, F1 ponderado, recusa nas consultas fora do domínio, proporção de execuções com
campo acrescentado e o teste de McNemar exato entre as abordagens, com uma observação por
consulta (maioria das repetições). Grava `tab_abordagens<sufixo>.tex` e
`numeros_abordagens<sufixo>.tex` (macros \\res{abordagens<sufixo>}{modelo}{medida}).
"""

from __future__ import annotations

import argparse
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any

from pfc_busca import schema
from pfc_busca.agent_estruturado import MODELO_PROTOTIPO, rotulo_modelo
from pfc_busca.evaluation import metrics, report
from pfc_busca.evaluation.run_evaluation import DIR_RESULTADOS

LOCAIS = ["qwen3:4b-instruct-2507-q4_K_M", "gemma4:e4b-it-qat", "gemma4:e2b-it-qat", "mistral-nemo:12b"]
# ordem crescente de tamanho, para ler a tabela como "o que muda quando o modelo aumenta"
ORDEM = ["gemma4:e2b-it-qat", "qwen3:4b-instruct-2507-q4_K_M", "gemma4:e4b-it-qat", "mistral-nemo:12b",
         "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "openai/gpt-oss-120b"]
PARAMETROS = {"gemma4:e2b-it-qat": "2B ef.", "qwen3:4b-instruct-2507-q4_K_M": "4B", "gemma4:e4b-it-qat": "4B ef.",
              "mistral-nemo:12b": "12B", "openai/gpt-oss-20b": "21B (MoE)", "qwen/qwen3.8-27b": "27B",
              "openai/gpt-oss-120b": "117B (MoE)"}


def _principais(linhas: list[dict]) -> list[dict]:
    return [lin for lin in linhas if not lin.get("observacional")]


def _medidas(linhas: list[dict]) -> dict[str, Any]:
    principais = _principais(linhas)
    g = metrics.agregar(linhas)
    sem_f = [lin for lin in principais if "F" not in lin["categorias"]]
    com_f = [lin for lin in principais if "F" in lin["categorias"]]
    acrescentou = 0
    for lin in sem_f:
        aval = metrics.avaliar_linha(lin)
        if aval.fp - set(lin.get("esperado_resolvido") or {}):
            acrescentou += 1
    fora_enum = 0
    for lin in sem_f:
        pred = lin["predito"] or {}
        if any(c in pred and pred[c] not in (schema.valores_validos(c) or []) for c in schema.CAMPOS_ENUM):
            fora_enum += 1
    lo, hi = report.ic_acuracia(linhas)
    return {
        "foraenum": fora_enum / len(sem_f) if sem_f else None,
        "acuracia": g["acuracia"], "ic": (lo, hi), "f1": g["f1_ponderado"],
        "precisao": g["precisao_ponderada"], "recall": g["recall_ponderado"],
        "accsemf": metrics.agregar(sem_f)["acuracia"] if sem_f else None,
        "recusa": (sum(1 for lin in com_f if lin["predito"] is None) / len(com_f)) if com_f else None,
        "recusavazio": (sum(1 for lin in com_f if lin["predito"] is None or lin["predito"] == {}) / len(com_f))
        if com_f else None,
        "acrescentou": acrescentou / len(sem_f) if sem_f else None,
        "latmed": (g["latencia_llm_ms"] or {}).get("mediana"),
        "n": len({lin["id"] for lin in principais}),
    }


def _mcnemar(a: list[dict], b: list[dict], sem_f: bool = False) -> tuple[int, int, float]:
    filtro = (lambda lin: "F" not in lin["categorias"]) if sem_f else (lambda lin: True)
    ca = report.correcao_por_id([lin for lin in a if filtro(lin)])
    cb = report.correcao_por_id([lin for lin in b if filtro(lin)])
    so_a, so_b = report._discordantes(ca, cb)
    return so_a, so_b, report.mcnemar_exato(so_a, so_b)


def _nao_chamou_por_id(linhas: list[dict]) -> dict[str, bool]:
    """Consulta sem busca pela maioria das repetições."""
    votos: dict[str, list[bool]] = defaultdict(list)
    for lin in _principais(linhas):
        votos[lin["id"]].append(lin["predito"] is None)
    return {i: 2 * sum(v) > len(v) for i, v in votos.items()}


def _composicao(tc: list[dict], se: list[dict]) -> dict[str, int]:
    """De onde vêm as consultas em que só uma das abordagens acerta."""
    ctc, cse = report.correcao_por_id(tc), report.correcao_por_id(se)
    nao_chamou = _nao_chamou_por_id(tc)
    cat_f = {lin["id"] for lin in _principais(tc) if "F" in lin["categorias"]}
    so_se = [i for i in ctc if cse.get(i) and not ctc[i]]
    so_tc = [i for i in ctc if ctc[i] and i in cse and not cse[i]]
    return {"sose": len(so_se), "sosenaochamou": sum(1 for i in so_se if nao_chamou.get(i)),
            "sotc": len(so_tc), "sotcf": sum(1 for i in so_tc if i in cat_f)}


def _p(pv: float) -> str:
    return "inferior a 0,001" if pv < 0.001 else report._f(pv, 3)


def _p_tab(pv: float) -> str:
    return r"$<$\,0,001" if pv < 0.001 else report._f(pv, 3)


def _ic(ic: tuple[float, float]) -> str:
    return f"{report._pct(ic[0])} a {report._pct(ic[1])}"


def gerar(dir_resultados: Path, sufixo: str = "") -> tuple[str, str] | None:
    dados = report.carregar_modelos(dir_resultados, None)
    def ids(m: str) -> set[str]:
        return {lin["id"] for lin in dados[m]["linhas"]}

    # só entra o modelo cujas duas rodadas cobrem as mesmas consultas (rodada incompleta fica de fora)
    pares = [(m, rotulo_modelo(m, "saida_estruturada")) for m in ORDEM
             if m in dados and rotulo_modelo(m, "saida_estruturada") in dados
             and ids(m) == ids(rotulo_modelo(m, "saida_estruturada"))]
    incompletos = [m for m in ORDEM if m in dados and rotulo_modelo(m, "saida_estruturada") in dados
                   and (m, rotulo_modelo(m, "saida_estruturada")) not in pares]
    if incompletos:
        print(f"linha de base incompleta, fora da comparação: {', '.join(incompletos)}")
    prototipo = rotulo_modelo(MODELO_PROTOTIPO, "prototipo")
    tem_prototipo = prototipo in dados
    if not pares and not tem_prototipo:
        return None
    rodada = "abordagens" + sufixo.replace("_", "")
    defs: dict[str, str] = {}

    def put(chave: str, medida: str, valor: str) -> None:
        defs[f"res@{rodada}@{chave}@{medida}"] = valor

    linhas_tab = []
    for tc, se in pares:
        chave = report.CHAVES[tc]
        mtc, mse = _medidas(dados[tc]["linhas"]), _medidas(dados[se]["linhas"])
        for sufixo_medida, m in (("tc", mtc), ("se", mse)):
            put(chave, "acuracia" + sufixo_medida, report._pct(m["acuracia"]))
            put(chave, "ic" + sufixo_medida, _ic(m["ic"]))
            put(chave, "accsemf" + sufixo_medida, report._pct(m["accsemf"]))
            put(chave, "f" + sufixo_medida, report._f(m["f1"]))
            put(chave, "recusa" + sufixo_medida, report._pct(m["recusa"]))
            put(chave, "acrescentou" + sufixo_medida, report._pct(m["acrescentou"]))
        put(chave, "recusavaziose", report._pct(mse["recusavazio"]))
        put(chave, "foraenumtc", report._pct(mtc["foraenum"]))
        put(chave, "foraenumse", report._pct(mse["foraenum"]))
        for medida, valor in _composicao(dados[tc]["linhas"], dados[se]["linhas"]).items():
            put(chave, medida, str(valor))
        put(chave, "n", str(mtc["n"]))
        for nome, sem_f in (("", False), ("semf", True)):
            so_tc, so_se, pv = _mcnemar(dados[tc]["linhas"], dados[se]["linhas"], sem_f)
            put(chave, "sotc" + nome, str(so_tc))
            put(chave, "sose" + nome, str(so_se))
            put(chave, "p" + nome, _p(pv))
        diferenca = (mtc["acuracia"] or 0) - (mse["acuracia"] or 0)
        put(chave, "difpp", report._num(100 * diferenca))
        _, _, p_geral = _mcnemar(dados[tc]["linhas"], dados[se]["linhas"])
        _, _, p_semf = _mcnemar(dados[tc]["linhas"], dados[se]["linhas"], True)
        nome = report._tex(report.rotulo(tc))
        linhas_tab.append(
            f"\\multirow{{2}}{{*}}{{{nome}}} & \\multirow{{2}}{{*}}{{{PARAMETROS.get(tc, '')}}} & "
            f"Tool Calling & {report._pct(mtc['acuracia'])} & "
            f"{report._pct(mtc['accsemf'])} & {report._f(mtc['f1'])} & {report._pct(mtc['recusa'])} & "
            f"{report._pct(mtc['acrescentou'])} & \\multirow{{2}}{{*}}{{{_p_tab(p_geral)}}} & "
            f"\\multirow{{2}}{{*}}{{{_p_tab(p_semf)}}} \\\\")
        linhas_tab.append(
            f" & & Saída Estruturada & {report._pct(mse['acuracia'])} & {report._pct(mse['accsemf'])} & "
            f"{report._f(mse['f1'])} & {report._pct(mse['recusa'])} & {report._pct(mse['acrescentou'])} & & \\\\ \\hline")
    if tem_prototipo:
        linhas_p = dados[prototipo]["linhas"]
        mp = _medidas(linhas_p)
        put("prototipo", "acuracia", report._pct(mp["acuracia"]))
        put("prototipo", "ic", _ic(mp["ic"]))
        put("prototipo", "accsemf", report._pct(mp["accsemf"]))
        put("prototipo", "f", report._f(mp["f1"]))
        put("prototipo", "recusa", report._pct(mp["recusa"]))
        put("prototipo", "recusavazio", report._pct(mp["recusavazio"]))
        put("prototipo", "acrescentou", report._pct(mp["acrescentou"]))
        put("prototipo", "foraenum", report._pct(mp["foraenum"]))
        put("prototipo", "latmeds", report._num((mp["latmed"] or 0) / 1000))
        put("prototipo", "n", str(mp["n"]))
        principais = _principais(linhas_p)
        extras = [lin.get("extras") or {} for lin in principais]
        put("prototipo", "fallback", str(sum(1 for e in extras if e.get("usou_fallback"))))
        put("prototipo", "novastentativas", str(sum(1 for e in extras if (e.get("tentativas") or 1) > 1)))
        alteradas = {lin["id"] for lin, e in zip(principais, extras, strict=True)
                     if e.get("texto_preprocessado") not in (None, lin["consulta"])}
        put("prototipo", "dicionarioalterou", str(len(alteradas)))
        put("prototipo", "execucoes", str(len(principais)))
        for tc in LOCAIS:
            if tc in dados:
                chave = report.CHAVES[tc]
                so_tc, so_p, pv = _mcnemar(dados[tc]["linhas"], linhas_p)
                put(f"{chave}-prototipo", "sotc", str(so_tc))
                put(f"{chave}-prototipo", "soprototipo", str(so_p))
                put(f"{chave}-prototipo", "p", _p(pv))
        linhas_tab.append(
            f"Phi-4 14B & 14B & Método do protótipo & {report._pct(mp['acuracia'])} & {report._pct(mp['accsemf'])} & "
            f"{report._f(mp['f1'])} & {report._pct(mp['recusa'])} & {report._pct(mp['acrescentou'])} & --- & --- \\\\ \\hline")

    titulo = " --- estação de referência (camadas P e N)" if sufixo == "_estacao" else ""
    tabela = "\n".join([
        r"\begin{table}[htbp!]", r"\centering",
        rf"\caption{{Tool Calling e Saída Estruturada sobre as mesmas consultas{titulo}}}",
        rf"\label{{tab:abordagens{sufixo}}}", r"\footnotesize",
        r"\ajustartabela{%",
        r"\begin{tabular}{|l|c|l|c|c|c|c|c|c|c|}", r"\hline",
        r"\textbf{Modelo} & \textbf{Parâm.} & \textbf{Abordagem} & \textbf{Acurácia} & \textbf{Sem F} & \textbf{F1} & "
        r"\textbf{Recusa F} & \textbf{Campo a mais} & \textbf{\textit{p}} & \textbf{\textit{p} sem F} \\", r"\hline",
        *linhas_tab,
        r"\end{tabular}}",
        r"\fonte{Elaborado pelos autores. Sem F: acurácia nas consultas das métricas principais fora da categoria F. "
        r"Recusa F: proporção das execuções da categoria F sem busca; na Saída Estruturada a aplicação sempre busca. "
        r"Campo a mais: proporção das execuções fora da categoria F com algum campo ausente do gabarito. "
        r"\textit{p}: teste de McNemar exato entre as duas abordagens do mesmo modelo, com uma observação por "
        r"consulta (maioria das repetições). Parâm.: parâmetros (ef.: efetivos; MoE: mistura de especialistas, "
        r"com parte dos parâmetros ativa a cada \textit{token})."
        + (r" Modelos (Groq): execução em nuvem, uma repetição, data de referência de 24/09/2026."
           if any("/" in tc for tc, _ in pares) else "") + "}",
        r"\end{table}", ""])
    macros = [f"% AUTO-GERADO por pfc_busca.evaluation.comparacao (rodada '{rodada}') — não editar à mão",
              r"\providecommand{\res}[3]{\ifcsname res@#1@#2@#3\endcsname\csname res@#1@#2@#3\endcsname\else\textbf{??}\fi}"]
    macros += [f"\\expandafter\\def\\csname {k}\\endcsname{{{v}}}" for k, v in sorted(defs.items())]
    return tabela, "\n".join(macros) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--resultados", type=Path, default=DIR_RESULTADOS)
    p.add_argument("--sufixo", default="")
    p.add_argument("--paper", type=Path, help="diretório do texto (grava em DIR/tabelas)")
    args = p.parse_args(argv)
    gerado = gerar(args.resultados, args.sufixo)
    if gerado is None:
        print(f"sem rodadas de linha de base em {args.resultados}")
        return 0
    tabela, macros = gerado
    saida = args.resultados / "consolidado"
    saida.mkdir(parents=True, exist_ok=True)
    arquivos = {f"tab_abordagens{args.sufixo}.tex": tabela, f"numeros_abordagens{args.sufixo}.tex": macros}
    for nome, conteudo in arquivos.items():
        (saida / nome).write_text(conteudo, encoding="utf-8")
        if args.paper:
            (args.paper / "tabelas").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(saida / nome, args.paper / "tabelas" / nome)
    print(f"comparação de abordagens: {', '.join(arquivos)}" + (f" -> {args.paper / 'tabelas'}" if args.paper else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
