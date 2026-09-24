"""Consolida `results/<modelo>/` de vários modelos nas tabelas e figuras do Cap. 5.

    pfc-relatorio                              # todos os modelos em results/
    pfc-relatorio --modelos qwen3:4b,gemma4:e4b-it-qat --saida results/consolidado

Produz em `results/consolidado/`:
    comparativo.md                 tudo, legível
    tab_comparativo.tex            Tabela "Comparativo de desempenho entre os modelos"
    tab_por_categoria.tex          Tabela "F1 por categoria de consulta e por modelo"
    tab_por_campo.tex              Tabela "F1 por campo do schema"
    tab_latencia.tex               estatísticas de latência por modelo
    fig_latencia_boxplot.pdf/.png  Figura "Distribuição de latência por modelo"
    fig_f1_por_campo.pdf/.png      barras agrupadas
    fig_acuracia_por_categoria.pdf/.png
    erros_representativos.md       amostra de falhas por tipo, para a análise de erros
    estatistica.md                 IC de Wilson (acurácia) e McNemar pareado entre modelos

Nada aqui interpreta resultado: só organiza. A interpretação é o texto do Cap. 5.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

from pfc_busca import schema
from pfc_busca.evaluation import metrics
from pfc_busca.evaluation.run_evaluation import DIR_RESULTADOS, carregar_execucoes, slug

ROTULOS = {
    "qwen3:4b-instruct-2507-q4_K_M": "Qwen 3 4B",
    "qwen3:4b": "Qwen 3 4B (build com thinking — descartado)",
    "gemma4:e4b-it-qat": "Gemma 4 E4B",
    "gemma4:e2b-it-qat": "Gemma 4 E2B",
    "mistral-nemo:12b": "Mistral Nemo 12B",
}
NOMES_CATEGORIA = {"S": "Simples", "C": "Compostas", "M": "Com código MI/INOM",
                   "T": "Com referência temporal relativa", "O": "Com ordenação",
                   "A": "Ambíguas / variações ortográficas"}


def rotulo(modelo: str) -> str:
    return ROTULOS.get(modelo, modelo)


def _tex(texto: str) -> str:
    return (texto.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
            .replace("#", r"\#").replace("—", "---"))


def _pct(v: float | None) -> str:
    return "---" if v is None else f"{100 * v:.1f}\\%"


def _pct_md(v: float | None) -> str:
    return "—" if v is None else f"{100 * v:.1f}%"


def _f(v: float | None, casas: int = 3) -> str:
    return "---" if v is None else f"{v:.{casas}f}"


# ---------------------------------------------------------------------------
# Estatística
# ---------------------------------------------------------------------------

def wilson(acertos: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confiança de Wilson (95%) para uma proporção."""
    if n == 0:
        return (0.0, 0.0)
    p = acertos / n
    denom = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / denom
    meio = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centro - meio), min(1.0, centro + meio))


def mcnemar_exato(b: int, c: int) -> float:
    """p-valor bicaudal exato (binomial) para pares discordantes b e c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    cauda = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * cauda)


def correcao_por_consulta(linhas: list[dict]) -> dict[tuple[str, int], bool]:
    return {
        (lin["id"], lin["repeticao"]): metrics.avaliar_caso(
            lin["esperado_resolvido"], lin["predito"], lin["espera_tool_call"]).correto
        for lin in linhas if not lin.get("observacional")
    }


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

def carregar_modelos(dir_resultados: Path, modelos: list[str] | None) -> dict[str, dict]:
    """{modelo: {"resumo": ..., "linhas": [...]}} para cada diretório com resumo.json."""
    saida = {}
    if not dir_resultados.is_dir():
        return saida
    for pasta in sorted(dir_resultados.iterdir()):
        resumo = pasta / "resumo.json"
        if not pasta.is_dir() or not resumo.exists():
            continue
        r = json.loads(resumo.read_text(encoding="utf-8"))
        modelo = r["modelo"]
        if modelos and modelo not in modelos:
            continue
        saida[modelo] = {"resumo": r, "linhas": carregar_execucoes(pasta),
                         "manifesto": json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
                         if (pasta / "manifesto.json").exists() else {}}
    if modelos:  # preserva a ordem pedida
        saida = {m: saida[m] for m in modelos if m in saida}
    return saida


# ---------------------------------------------------------------------------
# Tabelas LaTeX (mesmos rótulos/labels do cap05-resultados.tex)
# ---------------------------------------------------------------------------

def tab_comparativo(dados: dict[str, dict]) -> str:
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              r"\caption{Comparativo de desempenho entre os modelos avaliados}",
              r"\label{tab:resultados_comparativo}", r"\small",
              r"\begin{tabular}{|l|c|c|c|c|c|}", r"\hline",
              r"\textbf{Modelo} & \textbf{Acurácia} & \textbf{Precisão} & \textbf{Recall} & \textbf{F1} & \textbf{Latência med. (ms)} \\",
              r"\hline"]
    for modelo, d in dados.items():
        g = d["resumo"]["geral"]
        linhas.append(f"{_tex(rotulo(modelo))} & {_pct(g['acuracia'])} & {_f(g['precisao_ponderada'])} & "
                      f"{_f(g['recall_ponderado'])} & {_f(g['f1_ponderado'])} & "
                      f"{g['latencia_llm_ms'].get('mediana', 0):.0f} \\\\")
    linhas += [r"\hline", r"\end{tabular}",
               r"\fonte{Elaborado pelo autor. Precisão, \textit{recall} e F1 ponderados pela frequência de cada campo no gabarito; latência do LLM na tradução.}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


def tab_por_categoria(dados: dict[str, dict]) -> str:
    cols = "|l|" + "c|" * len(dados)
    cab = " & ".join(rf"\textbf{{{_tex(rotulo(m))}}}" for m in dados)
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              r"\caption{F1-\textit{score} por categoria de consulta e por modelo}",
              r"\label{tab:resultados_por_categoria}", r"\small",
              rf"\begin{{tabular}}{{{cols}}}", r"\hline",
              rf"\textbf{{Categoria}} & {cab} \\", r"\hline"]
    for cat in ["S", "C", "M", "T", "O", "A"]:
        vals = " & ".join(_f(d["resumo"]["geral"]["por_categoria"][cat]["f1_ponderado"]) for d in dados.values())
        n = next(iter(dados.values()))["resumo"]["geral"]["por_categoria"][cat]["n"]
        linhas.append(f"{NOMES_CATEGORIA[cat]} (n={n}) & {vals} \\\\")
    linhas.append(r"\hline")
    vals = " & ".join(_f(d["resumo"]["geral"]["f1_ponderado"]) for d in dados.values())
    linhas.append(rf"\textbf{{Média ponderada}} & {vals} \\")
    linhas += [r"\hline", r"\end{tabular}",
               r"\fonte{Elaborado pelo autor. Uma consulta pode pertencer a mais de uma categoria; n = consultas da categoria nas métricas principais.}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


def tab_por_campo(dados: dict[str, dict]) -> str:
    cols = "|l|c|" + "c|" * len(dados)
    cab = " & ".join(rf"\textbf{{{_tex(rotulo(m))}}}" for m in dados)
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              r"\caption{F1-\textit{score} por campo do \textit{schema} de busca --- comparativo entre modelos}",
              r"\label{tab:resultados_por_campo}", r"\small",
              rf"\begin{{tabular}}{{{cols}}}", r"\hline",
              rf"\textbf{{Campo}} & \textbf{{Ocorr.}} & {cab} \\", r"\hline"]
    primeiro = next(iter(dados.values()))["resumo"]["geral"]["por_campo"]
    for campo in schema.CAMPOS:
        vals = " & ".join(_f(d["resumo"]["geral"]["por_campo"][campo]["f1"]) for d in dados.values())
        linhas.append(rf"\texttt{{{_tex(campo)}}} & {primeiro[campo]['ocorrencias']} & {vals} \\")
    linhas += [r"\hline", r"\end{tabular}",
               r"\fonte{Elaborado pelo autor. Ocorr. = vezes que o campo aparece no gabarito.}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


def tab_latencia(dados: dict[str, dict]) -> str:
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              r"\caption{Latência da tradução (LLM), em milissegundos, por modelo}",
              r"\label{tab:latencia}", r"\small",
              r"\begin{tabular}{|l|c|c|c|c|c|c|}", r"\hline",
              r"\textbf{Modelo} & \textbf{n} & \textbf{Mín.} & \textbf{Mediana} & \textbf{Média} & \textbf{p95} & \textbf{Máx.} \\",
              r"\hline"]
    for modelo, d in dados.items():
        lat = d["resumo"]["geral"]["latencia_llm_ms"]
        if not lat:
            continue
        linhas.append(f"{_tex(rotulo(modelo))} & {lat['n']} & {lat['min']:.0f} & {lat['mediana']:.0f} & "
                      f"{lat['media']:.0f} & {lat['p95']:.0f} & {lat['max']:.0f} \\\\")
    linhas += [r"\hline", r"\end{tabular}",
               r"\fonte{Elaborado pelo autor. Medido em volta da chamada ao Ollama, na estação da Seção~\ref{sec:ambiente}.}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def figuras(dados: dict[str, dict], saida: Path) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    gerados = []
    modelos = list(dados)
    nomes = [rotulo(m) for m in modelos]

    # 1) boxplot de latência
    series = [[lin["latencia_llm_ms"] for lin in dados[m]["linhas"]
               if lin.get("latencia_llm_ms") is not None and not lin.get("erro") and not lin.get("observacional")]
              for m in modelos]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.boxplot(series, tick_labels=nomes, showfliers=True, flierprops={"markersize": 2, "alpha": 0.4})
    ax.set_ylabel("latência do LLM (ms)")
    ax.set_yscale("log")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(saida / f"fig_latencia_boxplot.{ext}", dpi=200)
    plt.close(fig)
    gerados.append("fig_latencia_boxplot")

    # 2) F1 por campo, barras agrupadas
    fig, ax = plt.subplots(figsize=(9, 3.8))
    largura = 0.8 / max(1, len(modelos))
    x = list(range(len(schema.CAMPOS)))
    for i, m in enumerate(modelos):
        f1s = [dados[m]["resumo"]["geral"]["por_campo"][c]["f1"] for c in schema.CAMPOS]
        ax.bar([xi + i * largura for xi in x], f1s, width=largura, label=rotulo(m))
    ax.set_xticks([xi + largura * (len(modelos) - 1) / 2 for xi in x])
    ax.set_xticklabels(schema.CAMPOS, rotation=35, ha="right")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("F1 por campo")
    ax.legend(frameon=False, ncol=len(modelos), fontsize=8, loc="lower left", bbox_to_anchor=(0.0, 1.01))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(saida / f"fig_f1_por_campo.{ext}", dpi=200)
    plt.close(fig)
    gerados.append("fig_f1_por_campo")

    # 3) acurácia por categoria
    cats = ["S", "C", "M", "T", "O", "A"]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for i, m in enumerate(modelos):
        acc = [dados[m]["resumo"]["geral"]["por_categoria"][c]["acuracia"] or 0 for c in cats]
        ax.bar([xi + i * largura for xi in range(len(cats))], acc, width=largura, label=rotulo(m))
    ax.set_xticks([xi + largura * (len(modelos) - 1) / 2 for xi in range(len(cats))])
    ax.set_xticklabels([NOMES_CATEGORIA[c] for c in cats], rotation=20, ha="right", fontsize=8)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("acurácia por consulta")
    ax.legend(frameon=False, ncol=len(modelos), fontsize=8, loc="lower left", bbox_to_anchor=(0.0, 1.01))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(saida / f"fig_acuracia_por_categoria.{ext}", dpi=200)
    plt.close(fig)
    gerados.append("fig_acuracia_por_categoria")
    return gerados


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------

def comparativo_markdown(dados: dict[str, dict]) -> str:
    out = ["# Comparativo entre modelos", ""]
    out += ["| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, d in dados.items():
        g = d["resumo"]["geral"]
        corr = correcao_por_consulta(d["linhas"])
        lo, hi = wilson(sum(corr.values()), len(corr))
        lat = g["latencia_llm_ms"]
        out.append(f"| {rotulo(m)} | {g['n_consultas']} | {_pct_md(g['acuracia'])} | {100*lo:.1f}–{100*hi:.1f}% | "
                   f"{g['precisao_ponderada']:.3f} | {g['recall_ponderado']:.3f} | {g['f1_ponderado']:.3f} | {g['f1_macro']:.3f} | "
                   f"{lat.get('mediana', 0):.0f} | {lat.get('p95', 0):.0f} | {g['diagnosticos']['chamadas_com_erro']} |")
    out += ["", "## F1 ponderado por categoria", "",
            "| Categoria | " + " | ".join(rotulo(m) for m in dados) + " |",
            "|---|" + "---|" * len(dados)]
    for cat in ["S", "C", "M", "T", "O", "A"]:
        out.append(f"| {NOMES_CATEGORIA[cat]} | " + " | ".join(
            f"{d['resumo']['geral']['por_categoria'][cat]['f1_ponderado']:.3f}" for d in dados.values()) + " |")
    out += ["", "## Acurácia por categoria", "",
            "| Categoria | " + " | ".join(rotulo(m) for m in dados) + " |", "|---|" + "---|" * len(dados)]
    for cat in ["S", "C", "M", "T", "O", "A"]:
        out.append(f"| {NOMES_CATEGORIA[cat]} | " + " | ".join(
            _pct_md(d['resumo']['geral']['por_categoria'][cat]['acuracia']) for d in dados.values()) + " |")
    out += ["", "## F1 por campo", "",
            "| Campo | Ocorr. | " + " | ".join(rotulo(m) for m in dados) + " |", "|---|---|" + "---|" * len(dados)]
    primeiro = next(iter(dados.values()))["resumo"]["geral"]["por_campo"]
    for campo in schema.CAMPOS:
        out.append(f"| `{campo}` | {primeiro[campo]['ocorrencias']} | " + " | ".join(
            f"{d['resumo']['geral']['por_campo'][campo]['f1']:.3f}" for d in dados.values()) + " |")
    out += ["", "## Acurácia por origem do caso", "",
            "| Origem | " + " | ".join(rotulo(m) for m in dados) + " |", "|---|" + "---|" * len(dados)]
    for o in ["P", "N", "G"]:
        out.append(f"| {o} | " + " | ".join(
            _pct_md(d['resumo']['geral']['por_origem'][o]['acuracia']) for d in dados.values()) + " |")
    out += ["", "## Diagnósticos", ""]
    for m, d in dados.items():
        g = d["resumo"]["geral"]
        dg = g["diagnosticos"]
        obs = g["observacionais"]
        out += [f"### {rotulo(m)}", "",
                f"- tipos de erro: {dg['tipos_erro']}",
                f"- campos fora do schema: {dg['campos_fora_do_schema']}",
                f"- IoU médio de períodos: { {k: round(v, 3) for k, v in dg['iou_periodos_medio'].items()} }",
                f"- chamadas com erro: {dg['chamadas_com_erro']} {dg['classes_de_erro']}",
                f"- não chamou quando devia: {dg['nao_chamou_quando_devia']}",
                f"- observacionais: {obs['n']} casos, acurácia {_pct_md(obs['acuracia'])}, chamou sem dever {obs['chamou_sem_dever']}",
                f"- thinking desativado: {d['manifesto'].get('thinking_desativado')} · Ollama {d['manifesto'].get('software', {}).get('ollama_servidor')} · "
                f"repetições {d['resumo']['repeticoes']}", ""]
    return "\n".join(out) + "\n"


def estatistica_markdown(dados: dict[str, dict]) -> str:
    out = ["# Estatística", "", "## Acurácia com IC 95% (Wilson)", "",
           "| Modelo | acertos / n | acurácia | IC 95% |", "|---|---|---|---|"]
    correcoes = {m: correcao_por_consulta(d["linhas"]) for m, d in dados.items()}
    for m, corr in correcoes.items():
        n, k = len(corr), sum(corr.values())
        lo, hi = wilson(k, n)
        out.append(f"| {rotulo(m)} | {k} / {n} | {100*k/n if n else 0:.1f}% | {100*lo:.1f}–{100*hi:.1f}% |")
    out += ["", "## McNemar pareado (mesmas consultas × repetições)", "",
            "| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |", "|---|---|---|---|---|"]
    modelos = list(dados)
    for i in range(len(modelos)):
        for j in range(i + 1, len(modelos)):
            a, b = correcoes[modelos[i]], correcoes[modelos[j]]
            comuns = set(a) & set(b)
            so_a = sum(1 for k in comuns if a[k] and not b[k])
            so_b = sum(1 for k in comuns if b[k] and not a[k])
            out.append(f"| {rotulo(modelos[i])} | {rotulo(modelos[j])} | {so_a} | {so_b} | "
                       f"{mcnemar_exato(so_a, so_b):.4f} |")
    out += ["", "Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as "
            "mesmas consultas, dificilmente é obra do acaso. Repetições do mesmo modelo entram como pares "
            "independentes — é uma aproximação, declarada como tal no texto.", ""]
    return "\n".join(out)


def erros_markdown(dados: dict[str, dict], por_tipo: int = 4, semente: int = 42) -> str:
    rng = random.Random(semente)
    out = ["# Erros representativos (amostra aleatória por tipo, semente 42)", ""]
    for m, d in dados.items():
        out += [f"## {rotulo(m)}", ""]
        grupos: dict[str, list] = defaultdict(list)
        for lin in d["linhas"]:
            if lin.get("observacional") or lin["repeticao"] != min(x["repeticao"] for x in d["linhas"]):
                continue
            aval = metrics.avaliar_caso(lin["esperado_resolvido"], lin["predito"], lin["espera_tool_call"])
            if not aval.correto:
                grupos[aval.tipo_erro or "outro"].append((lin, aval))
        for tipo, itens in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
            out += [f"### {tipo} ({len(itens)} casos)", ""]
            for lin, aval in rng.sample(itens, min(por_tipo, len(itens))):
                out += [f"- **{lin['id']}** — \"{lin['consulta']}\"",
                        f"  - esperado: `{json.dumps(lin['esperado_resolvido'], ensure_ascii=False)}`",
                        f"  - predito: `{json.dumps(lin['predito'], ensure_ascii=False)}`"
                        + (f" · erro: {lin['erro']}" if lin.get("erro") else ""),
                        f"  - FP {sorted(aval.fp)} · FN {sorted(aval.fn)} · fora do schema {sorted(aval.fora_do_schema)}"]
            out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Consolida resultados de vários modelos.")
    p.add_argument("--resultados", type=Path, default=DIR_RESULTADOS)
    p.add_argument("--modelos", help="tags separadas por vírgula, na ordem das tabelas")
    p.add_argument("--saida", type=Path, default=None)
    p.add_argument("--paper", type=Path, metavar="DIR",
                   help="copia tab_*.tex para DIR/tabelas e fig_*.pdf para DIR/figuras (o Cap. 5 os inclui)")
    args = p.parse_args(argv)

    modelos = [m.strip() for m in args.modelos.split(",")] if args.modelos else None
    dados = carregar_modelos(args.resultados, modelos)
    if not dados:
        print("nenhum results/<modelo>/resumo.json encontrado", file=sys.stderr)
        return 1
    saida = args.saida or (args.resultados / "consolidado")
    saida.mkdir(parents=True, exist_ok=True)

    (saida / "comparativo.md").write_text(comparativo_markdown(dados), encoding="utf-8")
    (saida / "estatistica.md").write_text(estatistica_markdown(dados), encoding="utf-8")
    (saida / "erros_representativos.md").write_text(erros_markdown(dados), encoding="utf-8")
    (saida / "tab_comparativo.tex").write_text(tab_comparativo(dados), encoding="utf-8")
    (saida / "tab_por_categoria.tex").write_text(tab_por_categoria(dados), encoding="utf-8")
    (saida / "tab_por_campo.tex").write_text(tab_por_campo(dados), encoding="utf-8")
    (saida / "tab_latencia.tex").write_text(tab_latencia(dados), encoding="utf-8")
    figs = figuras(dados, saida)
    if args.paper:
        import shutil
        (args.paper / "tabelas").mkdir(parents=True, exist_ok=True)
        (args.paper / "figuras").mkdir(parents=True, exist_ok=True)
        for f in saida.glob("tab_*.tex"):
            shutil.copy2(f, args.paper / "tabelas" / f.name)
        for f in saida.glob("fig_*.pdf"):
            shutil.copy2(f, args.paper / "figuras" / f.name)
        print(f"tabelas e figuras copiadas para {args.paper}")
    print(f"consolidado {len(dados)} modelo(s) em {saida}: comparativo.md, estatistica.md, "
          f"erros_representativos.md, 4 tabelas .tex, figuras {figs}")
    for m in dados:
        print(f"  - {m} ({slug(m)}) → {rotulo(m)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
