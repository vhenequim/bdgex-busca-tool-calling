"""Teste A/B: Tool Calling (modo A) × Saída Estruturada (modo B) em cada par comparável das rodadas.

    python -m pfc_busca.evaluation.ab [--paper ../paper_revisado] [--resultados results] [--saida results/ab]
                                      [--referencias DIR ...] [--estrito]

Um par é comparável quando as duas rodadas têm o mesmo modelo, as mesmas consultas, a mesma especificação
(v1: `agent` × `agent_estruturado`; v2: `v2`; v3: `v3`, o TC v3 completo × o controle SE v3) e o mesmo
ambiente (GPU T4, estação de referência ou Groq). Os pares estão declarados em `pares()`; um par sem rodada
fica de fora, com aviso, e uma rodada incompleta entra só com as consultas presentes nas duas (n marcado).

Nenhuma medida é calculada aqui por conta própria; tudo vem das análises que o texto já usa:

- carga e repontuação contra o gabarito vigente do dataset da rodada, sem as observacionais:
  `lote.carregar_pasta` (não grava nada; `report.carregar_modelos` reescreveria os resumo.json);
- por modo: `lote.medidas` (acurácia por consulta, pela maioria das repetições, com IC de Wilson; acurácia no
  domínio, fora de F e E; recusa como classificação, com F1; latência mediana e p95 por execução, como em
  `metrics.agregar`) e `lote2.chamadas_por_consulta`;
- por par: `lote.comparar` (McNemar exato, uma observação por consulta; diferença de acurácia SE − TC com IC
  por bootstrap pareado de 2.000 reamostragens das consultas, semente 42).

A latência só entra quando as duas rodadas têm, nos manifestos, a mesma GPU, a mesma versão do Ollama e a
mesma parcela do modelo na GPU (`hardware_comparavel`); no Groq, o hardware é do provedor e fica de fora.

Conferência: cada número da tabela é comparado com a macro já existente do mesmo par (numeros_abordagens*.tex,
numeros.tex, numeros_estacao.tex, numeros_groq.tex, numeros_lote.tex, numeros_lote2.tex). Uma divergência é
"explicada" quando o valor existente é reproduzido pelo critério da outra análise (média das execuções em vez
da maioria das repetições; todas as consultas da rodada em vez das comuns ao par); senão, "não explicada".

Saídas em RESULTADOS/ab/ (e, com --paper, as .tex também em PAPER/tabelas/): tab_ab.tex, numeros_ab.tex
(\\res{ab}{<par>}{<medida>} e \\res{ab}{geral}{<medida>}), ab.md (tabela, rodadas, avisos e conferência) e
ab.json. O lote 2 é o conjunto de teste: nada aqui imprime ou grava o texto de uma consulta.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pfc_busca.evaluation import comparacao, lote, lote2, report
from pfc_busca.evaluation.run_evaluation import DIR_RESULTADOS, RAIZ_REPO, slug

ROTULO = "ab"                      # \res{ab}{<par>}{<medida>}
ALFA = 0.05                        # nível do McNemar para "melhor" / "empate" nas contagens gerais
E4B = "gemma4:e4b-it-qat"
LOCAIS_T4 = [m for m in comparacao.ORDEM if m in comparacao.LOCAIS]
ESTACAO = [m for m in comparacao.ORDEM if m in ("gemma4:e2b-it-qat", "qwen3:4b-instruct-2507-q4_K_M")]
NUVEM = [m for m in comparacao.ORDEM if "/" in m]
# especificação -> (config TC, config SE) nos nomes de lote/lote2 e (abordagem TC, abordagem SE) de run_evaluation
ESPECS = {"v1": ("tc1", "se1", "tool_calling", "saida_estruturada"),
          "v2": ("tc2", "se2", "tool_calling_v2", "saida_estruturada_v2"),
          "v3": ("tc3", "se3", "tool_calling_v3", "saida_estruturada_v3")}
AMBIENTES = {"t4": "T4", "estacao": "Estação", "groq": "Groq"}
_NOME_VALIDO = re.compile(r"[A-Za-z0-9]+")


# ---------------------------------------------------------------------------
# Pares
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Ref:
    """Macros já existentes do mesmo par, para a conferência.

    estilo: "lote" e "lote2" (`lote.macros_config`/`macros_par`: \\res{ns}{tc|se}{...} e \\res{ns}{par}{...}),
    "comparacao" (\\res{ns}{chave}{...tc|...se}) ou "report" (\\res{ns}{chave}{...}, só o Tool Calling)."""
    estilo: str
    ns: str
    chave: str = ""
    tc: str = ""
    se: str = ""
    par: str = ""


@dataclass(frozen=True)
class Par:
    conjunto: str            # base (as 310), lote (lote 1) ou lote2
    ambiente: str            # t4, estacao ou groq
    modelo: str              # tag do modelo
    espec: str               # v1, v2 ou v3
    tc: Path                 # pasta da rodada com Tool Calling
    se: Path                 # pasta da rodada com Saída Estruturada
    desenvolvimento: bool = False   # dentro da amostra que orientou o desenho da especificação
    refs: tuple[Ref, ...] = ()

    @property
    def chave(self) -> str:
        amb = "" if self.ambiente == "t4" else self.ambiente
        modelo = report.CHAVES.get(self.modelo) or re.sub(r"[^a-z0-9]", "", slug(self.modelo).lower())
        return f"{self.conjunto}{amb}{modelo}{self.espec}"


def pares(dir_resultados: Path = DIR_RESULTADOS) -> list[Par]:
    """Os pares TC × SE comparáveis, na ordem da tabela (dentro de cada bloco, modelos em ordem de tamanho)."""
    R = dir_resultados

    def pastas(base: Path, modelo: str, espec: str, provedor: str = "ollama") -> tuple[Path, Path]:
        _, _, abordagem_tc, abordagem_se = ESPECS[espec]
        return base / slug(modelo, provedor, abordagem_tc), base / slug(modelo, provedor, abordagem_se)

    saida: list[Par] = []
    for m in LOCAIS_T4:
        c = report.CHAVES[m]
        refs = [Ref("comparacao", "abordagens", chave=c), Ref("report", "principal", chave=c)]
        if m == E4B:
            refs.append(Ref("lote", "base", tc="tc1", se="se1", par="tc1se1"))
        saida.append(Par("base", "t4", m, "v1", *pastas(R, m, "v1"), refs=tuple(refs)))
    for m in ESTACAO:
        c = report.CHAVES[m]
        saida.append(Par("base", "estacao", m, "v1", *pastas(R / "estacao", m, "v1"),
                         refs=(Ref("comparacao", "abordagensestacao", chave=c), Ref("report", "estacao", chave=c))))
    for m in NUVEM:
        c = report.CHAVES[m]
        saida.append(Par("base", "groq", m, "v1", *pastas(R, m, "v1", "groq"),
                         refs=(Ref("comparacao", "abordagens", chave=c), Ref("report", "groq", chave=c))))
    saida.append(Par("base", "t4", E4B, "v2", *pastas(R / "v2_310", E4B, "v2"), desenvolvimento=True,
                     refs=(Ref("lote", "base", tc="tc2", se="se2", par="tc2se2"),)))
    saida.append(Par("base", "t4", E4B, "v3", *pastas(R / "v3_310", E4B, "v3"), desenvolvimento=True,
                     refs=(Ref("lote2", lote2.ROTULO_310, tc="tc3", se="se3", par="tc3se3"),)))
    for espec in ("v1", "v2"):
        tc, se = ESPECS[espec][:2]
        saida.append(Par("lote", "t4", E4B, espec, *pastas(R / "lote", E4B, espec),
                         refs=(Ref("lote", "lote", tc=tc, se=se, par=tc + se),)))
    for espec in ("v1", "v2", "v3"):
        tc, se = ESPECS[espec][:2]
        saida.append(Par("lote2", "t4", E4B, espec, *pastas(R / "lote2", E4B, espec),
                         refs=(Ref("lote2", lote2.SUFIXO_PADRAO, tc=tc, se=se, par=tc + se),)))
    return saida


# ---------------------------------------------------------------------------
# Carga e medidas
# ---------------------------------------------------------------------------

def carregar_rodada(pasta: Path) -> dict[str, Any] | None:
    """Execuções repontuadas (sem as observacionais), casos do dataset e manifesto; None sem rodada válida."""
    if not (pasta / "execucoes.jsonl").exists():
        return None
    r = lote.carregar_pasta(pasta)
    if r is None or not r[0]:
        return None
    arq = pasta / "manifesto.json"
    manifesto = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    return {"pasta": pasta, "linhas": r[0], "casos": r[1], "manifesto": manifesto}


def _fracoes_gpu(manifesto: dict) -> list[int]:
    return sorted({round(100 * s["ollama_ps"]["fracao_na_gpu"]) for s in manifesto.get("sessoes") or []
                   if (s.get("ollama_ps") or {}).get("fracao_na_gpu") is not None})


def hardware_comparavel(a: dict, b: dict) -> tuple[bool, str, bool]:
    """(latência comparável, descrição, mesma máquina) de duas rodadas, pelos manifestos."""
    if any((m.get("provedor") or "ollama") != "ollama" for m in (a, b)):
        return False, "nuvem: hardware do provedor, não controlado", False
    ga, gb = ((m.get("hardware") or {}).get("gpu") for m in (a, b))
    if not ga or ga != gb:
        return False, f"GPU diferente ou não registrada ({ga or '?'} × {gb or '?'})", False
    va, vb = ((m.get("software") or {}).get("ollama_servidor") for m in (a, b))
    if va != vb:
        return False, f"versões do Ollama diferentes ({va} × {vb})", False
    fa, fb = _fracoes_gpu(a), _fracoes_gpu(b)
    if fa != fb:
        return False, f"parcela do modelo na GPU diferente ({fa} × {fb})", False
    mesma = (a.get("hardware") or {}).get("maquina") == (b.get("hardware") or {}).get("maquina")
    na_gpu = "/".join(str(x) for x in fa) + "% na GPU" if fa else "parcela na GPU não registrada"
    return (True, f"{report._gpu_curta(ga)}; Ollama {va}; {na_gpu}; "
                  + ("mesma máquina" if mesma else "sessões (máquinas) diferentes"), mesma)


def _lado(linhas: list[dict], casos: dict, config: str) -> dict[str, Any]:
    m = lote.medidas(linhas, casos)
    m["chamadas"] = lote2.chamadas_por_consulta(config, linhas)
    m["repeticoes"] = sorted({lin["repeticao"] for lin in linhas})
    return m


def medir_par(par: Par, tc: dict, se: dict) -> dict[str, Any] | None:
    """Medidas dos dois modos e do par, nas consultas presentes nas duas rodadas (None se não há nenhuma)."""
    cfg_tc, cfg_se = ESPECS[par.espec][:2]
    ids_tc = {x["id"] for x in tc["linhas"]}
    ids_se = {x["id"] for x in se["linhas"]}
    comuns = ids_tc & ids_se
    if not comuns:
        return None
    a = [x for x in tc["linhas"] if x["id"] in comuns]
    b = [x for x in se["linhas"] if x["id"] in comuns]
    comparavel, hardware, mesma = hardware_comparavel(tc["manifesto"], se["manifesto"])
    r: dict[str, Any] = {
        "par": par, "chave": par.chave, "n": len(comuns), "ntc": len(ids_tc), "nse": len(ids_se),
        "incompleto": ids_tc != ids_se, "ncasos": len(tc["casos"]),
        "pastas": (_mostrar(tc["pasta"]), _mostrar(se["pasta"])),
        "tc": _lado(a, tc["casos"], cfg_tc), "se": _lado(b, se["casos"], cfg_se), "cmp": lote.comparar(a, b),
        "latencia_comparavel": comparavel, "hardware": hardware, "mesma_maquina": mesma,
        "gpu": report._gpu_curta(g) if (g := (tc["manifesto"].get("hardware") or {}).get("gpu")) else "",
    }
    # só para a conferência: o mesmo par pelos critérios das outras análises (todas as consultas de cada rodada;
    # média das execuções, como em comparacao/report)
    r["tc_completo"] = r["tc"] if len(a) == len(tc["linhas"]) else _lado(tc["linhas"], tc["casos"], cfg_tc)
    r["se_completo"] = r["se"] if len(b) == len(se["linhas"]) else _lado(se["linhas"], se["casos"], cfg_se)
    r["tc_exec"], r["se_exec"] = comparacao._medidas(a), comparacao._medidas(b)
    r["tc_exec_completo"] = comparacao._medidas(tc["linhas"])
    r["se_exec_completo"] = comparacao._medidas(se["linhas"])
    return r


def _checar_rodadas(par: Par, tc: dict, se: dict, avisos: list[str]) -> None:
    """Avisa se as duas rodadas não são da especificação, do modelo, do dataset ou da data de referência do par."""
    _, _, abordagem_tc, abordagem_se = ESPECS[par.espec]
    esperadas = {"TC": {abordagem_tc} | ({None} if par.espec == "v1" else set()), "SE": {abordagem_se}}
    for lado, rodada in (("TC", tc), ("SE", se)):
        m = rodada["manifesto"]
        if m and m.get("abordagem") not in esperadas[lado]:
            avisos.append(f"{par.chave}: rodada {lado} com abordagem {m.get('abordagem')!r} (esperada "
                          f"{sorted(x for x in esperadas[lado] if x)})")
        if m.get("modelo") not in (None, par.modelo):
            avisos.append(f"{par.chave}: rodada {lado} do modelo {m.get('modelo')!r} (esperado {par.modelo!r})")
    datasets = {str((r["manifesto"].get("dataset") or {}).get("caminho") or "").replace("\\", "/") for r in (tc, se)}
    if len(datasets) > 1:
        avisos.append(f"{par.chave}: datasets diferentes nos manifestos ({sorted(datasets)})")
    hojes = {x["hoje"] for r in (tc, se) for x in r["linhas"]}
    if len(hojes) > 1:
        avisos.append(f"{par.chave}: datas de referência diferentes ({sorted(hojes)})")


def gerar(dir_resultados: Path = DIR_RESULTADOS) -> dict[str, Any]:
    avisos: list[str] = []
    resultados: list[dict] = []
    for par in pares(dir_resultados):
        tc, se = carregar_rodada(par.tc), carregar_rodada(par.se)
        faltam = [f"{lado} ({_mostrar(p)})" for lado, x, p in (("TC", tc, par.tc), ("SE", se, par.se))
                  if x is None]
        if faltam:
            avisos.append(f"{par.chave}: sem rodada {' e '.join(faltam)} (fora)")
            continue
        _checar_rodadas(par, tc, se, avisos)
        r = medir_par(par, tc, se)
        if r is None:
            avisos.append(f"{par.chave}: nenhuma consulta em comum entre as duas rodadas (fora)")
            continue
        if r["incompleto"]:
            avisos.append(f"{par.chave}: rodadas com consultas diferentes (TC {r['ntc']}, SE {r['nse']}); o par usa "
                          f"só as {r['n']} presentes nas duas")
        resultados.append(r)
    return {"resultados": resultados, "avisos": avisos, "dir": _mostrar(dir_resultados)}


def veredito(r: dict) -> str:
    """'se' ou 'tc' (o modo de maior acurácia, com p < ALFA no McNemar) ou 'empate'."""
    c = r["cmp"]
    if c["p"] >= ALFA or c["dif_acc"] == 0:
        return "empate"
    return "se" if c["dif_acc"] > 0 else "tc"


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------

def _s(ms: float | None, casas: int = 2) -> str:
    return "---" if ms is None else report._num(ms / 1000, casas)


def _ic(ic: tuple[float, float]) -> str:
    return f"{report._pct(ic[0])} a {report._pct(ic[1])}"


def _sem_pct(v: float | None) -> str:
    return report._pct(v).replace("\\%", "")


def nome_modelo(modelo: str) -> str:
    return report.rotulo(modelo).replace(" (Groq)", "")


def rotulo_conjunto(r: dict) -> str:
    par = r["par"]
    if par.conjunto == "lote":
        return "Lote 1"
    if par.conjunto == "lote2":
        return "Lote 2"
    return lote._milhar(r["ncasos"]) + (" (P e N)" if par.ambiente == "estacao" else "")


def _mostrar(p: Path) -> str:
    """Caminho relativo ao repositório (ou ao diretório que o contém, com '../'), nunca absoluto."""
    p = p.resolve()
    for base, prefixo in ((RAIZ_REPO, ""), (RAIZ_REPO.parent, "../")):
        try:
            return prefixo + p.relative_to(base).as_posix()
        except ValueError:
            continue
    return p.name


def _lat(r: dict, lado: str, medida: str) -> str:
    return _s(r[lado][medida]) if r["latencia_comparavel"] else "---"


def _extenso_f(n: int) -> str:
    return report.EXTENSO_F.get(n, report.EXTENSO.get(n, str(n)))


# ---------------------------------------------------------------------------
# Macros
# ---------------------------------------------------------------------------

def macros(resultados: list[dict]) -> str:
    defs: dict[str, str] = {}

    def put(chave: str, medida: str, valor: str) -> None:
        for parte in (chave, medida):
            if not _NOME_VALIDO.fullmatch(parte):
                raise ValueError(f"nome de macro com caractere fora de [A-Za-z0-9]: {parte!r}")
        defs[f"res@{ROTULO}@{chave}@{medida}"] = valor

    for r in resultados:
        k, par, c = r["chave"], r["par"], r["cmp"]
        put(k, "nome", report._tex(nome_modelo(par.modelo)))
        put(k, "conjunto", rotulo_conjunto(r))
        put(k, "espec", par.espec)
        put(k, "ambiente", AMBIENTES[par.ambiente])
        put(k, "desenvolvimento", "sim" if par.desenvolvimento else "não")
        put(k, "n", lote._milhar(r["n"]))
        put(k, "ntc", lote._milhar(r["ntc"]))
        put(k, "nse", lote._milhar(r["nse"]))
        for lado in ("tc", "se"):
            m = r[lado]
            put(k, "acc" + lado, report._pct(m["acuracia"]))
            put(k, "ic" + lado, _ic(m["ic"]))
            put(k, "dom" + lado, report._pct(m["accdominio"]))
            put(k, "recusaf" + lado, report._f(m["recusa"]["f1"]))
            put(k, "latmed" + lado, _lat(r, lado, "latmed"))
            put(k, "latp95" + lado, _lat(r, lado, "latp95"))
            put(k, "chamadas" + lado, report._num(m["chamadas"], 2) if m["chamadas"] is not None else "---")
            put(k, "rep" + lado, str(len(m["repeticoes"])))
        put(k, "dif", lote._pp(c["dif_acc"]))
        put(k, "icdif", lote._ic_pp(c["ic_dif_acc"]))
        put(k, "sotc", str(c["so_a"]))
        put(k, "sose", str(c["so_b"]))
        put(k, "p", lote._p(c["p"]))
        put(k, "veredito", {"se": "SE", "tc": "TC", "empate": "empate"}[veredito(r)])
        la, lb = r["tc"]["latmed"], r["se"]["latmed"]
        put(k, "razaolat", report._num(la / lb, 2) if r["latencia_comparavel"] and la and lb else "---")
    for sufixo, grupo in (("", resultados), ("semdesenv", [r for r in resultados if not r["par"].desenvolvimento])):
        conta = Counter(veredito(r) for r in grupo)
        put("geral", "npares" + sufixo, str(len(grupo)))
        put("geral", "nsemelhor" + sufixo, str(conta["se"]))
        put("geral", "ntcmelhor" + sufixo, str(conta["tc"]))
        put("geral", "nempate" + sufixo, str(conta["empate"]))
    put("geral", "alfa", report._f(ALFA, 2))
    return lote.texto_macros(defs, "pfc_busca.evaluation.ab")


# ---------------------------------------------------------------------------
# Tabela
# ---------------------------------------------------------------------------

def _bloco(r: dict) -> tuple[str, str, bool]:
    return r["par"].conjunto, r["par"].ambiente, r["par"].desenvolvimento


def _linha_tabela(r: dict, rotulo: str) -> str:
    par, c, tc, se = r["par"], r["cmp"], r["tc"], r["se"]
    espec = par.espec + (r"$^\dagger$" if par.desenvolvimento else "")
    n = lote._milhar(r["n"]) + (r"$^{*}$" if r["incompleto"] else "")
    cham = " / ".join(report._num(m["chamadas"], 2) if m["chamadas"] is not None else "---" for m in (tc, se))
    return (f"{rotulo} & {report._tex(nome_modelo(par.modelo))} & {espec} & {n} & "
            f"{_sem_pct(tc['acuracia'])} / {_sem_pct(se['acuracia'])} & "
            f"{lote._pp(c['dif_acc'])} ({lote._ic_pp(c['ic_dif_acc'])}) & {lote._p(c['p'])} & "
            f"{_sem_pct(tc['accdominio'])} / {_sem_pct(se['accdominio'])} & "
            f"{report._f(tc['recusa']['f1'])} / {report._f(se['recusa']['f1'])} & "
            f"{_lat(r, 'tc', 'latmed')} / {_lat(r, 'se', 'latmed')} & "
            f"{_lat(r, 'tc', 'latp95')} / {_lat(r, 'se', 'latp95')} & {cham} \\\\")


def _nota_incompleto(r: dict) -> str:
    """O lado com menos consultas é o incompleto; a linha usa só as consultas presentes nas duas rodadas."""
    nome = rf"{report._tex(nome_modelo(r['par'].modelo))} ({AMBIENTES[r['par'].ambiente]})"
    n = lote._milhar(r["n"])
    if r["nse"] < r["ntc"]:
        return (rf"$^{{*}}$ {nome}: rodada de Saída Estruturada incompleta ({lote._milhar(r['nse'])} das "
                rf"{lote._milhar(r['ntc'])} consultas pontuadas com \textit{{Tool Calling}}); a linha usa só as {n} "
                r"presentes nas duas")
    if r["ntc"] < r["nse"]:
        return (rf"$^{{*}}$ {nome}: rodada com \textit{{Tool Calling}} incompleta ({lote._milhar(r['ntc'])} das "
                rf"{lote._milhar(r['nse'])} consultas pontuadas com Saída Estruturada); a linha usa só as {n} "
                r"presentes nas duas")
    return (rf"$^{{*}}$ {nome}: rodadas com consultas diferentes ({lote._milhar(r['ntc'])} e "
            rf"{lote._milhar(r['nse'])}); a linha usa só as {n} presentes nas duas")


def _origens(resultados: list[dict]) -> list[str]:
    """De onde vem cada bloco de linhas (só os presentes), com contagens tiradas das próprias rodadas; a nota do
    desenvolvimento e a das rodadas incompletas vêm por último."""
    blocos: dict[tuple, list[dict]] = {}
    for r in resultados:
        blocos.setdefault(_bloco(r), []).append(r)
    partes, notas = [], []
    for (conjunto, ambiente, dev), rs in blocos.items():
        rotulo = rotulo_conjunto(rs[0])
        if dev:
            pastas = " e ".join(sorted({rf"\texttt{{{lote2._tex(Path(r['pastas'][0]).parent.as_posix())}/}}"
                                        for r in rs}))
            especs = " e da ".join(sorted({r["par"].espec for r in rs}))
            notas.append(rf"$^\dagger$ desenvolvimento: as {rotulo} consultas ({pastas}) orientaram o desenho da "
                         rf"{especs}, e o resultado nelas é de dentro da amostra, otimista por construção")
        elif conjunto == "base" and ambiente == "t4":
            rep_tc = sorted({len(r["tc"]["repeticoes"]) for r in rs})
            rep_se = sorted({len(r["se"]["repeticoes"]) for r in rs})
            partes.append(rf"{rotulo}, T4: rodadas completas dos modelos locais na GPU T4 (\texttt{{results/<modelo>/}} "
                          rf"e \texttt{{results/se-<modelo>/}}), \textit{{Tool Calling}} com "
                          rf"{' ou '.join(_extenso_f(x) for x in rep_tc)} repetições e Saída Estruturada com "
                          rf"{' ou '.join(_extenso_f(x) for x in rep_se)}")
        elif ambiente == "estacao":
            gpu = f" ({lote2._tex(rs[0]['gpu'])})" if rs[0]["gpu"] else ""
            partes.append(rf"{rotulo}, estação: estação de referência{gpu}, camadas P e N "
                          r"(\texttt{results/estacao/})")
        elif ambiente == "groq":
            partes.append(rf"{rotulo}, Groq: referência em nuvem (\texttt{{results/groq-<modelo>/}} e "
                          rf"\texttt{{results/groq-se-<modelo>/}})")
        elif conjunto == "lote":
            partes.append(rf"{rotulo}: lote de validação ({lote._milhar(rs[0]['n'])} consultas pontuadas; "
                          r"\texttt{results/lote/}), independente do desenho da v2")
        elif conjunto == "lote2":
            partes.append(rf"{rotulo}: conjunto de teste da v3 ({lote._milhar(rs[0]['n'])} consultas pontuadas; "
                          r"\texttt{results/lote2/}), nenhuma delas lida no desenvolvimento")
    notas += [_nota_incompleto(r) for r in resultados if r["incompleto"]]
    return partes + notas


def tabela(resultados: list[dict]) -> str:
    L = [r"\begin{table}[htbp!]", r"\centering",
         r"\caption{Teste A/B: \textit{Tool Calling} (A) e Saída Estruturada (B) com o mesmo modelo, as mesmas "
         r"consultas, a mesma especificação e o mesmo ambiente}", r"\label{tab:ab}", r"\footnotesize",
         r"\ajustartabela{%", r"\begin{tabular}{|l|l|c|r|c|c|c|c|c|c|c|c|}", r"\hline",
         r"\textbf{Conjunto} & \textbf{Modelo} & \textbf{Espec.} & \textbf{n} & "
         r"\textbf{\shortstack{Acurácia (\%)\\TC / SE}} & \textbf{\shortstack{SE $-$ TC, p.p.\\(IC 95\%)}} & "
         r"\textbf{\textit{p}} & \textbf{\shortstack{Domínio (\%)\\TC / SE}} & "
         r"\textbf{\shortstack{F1 recusa\\TC / SE}} & \textbf{\shortstack{Latência (s)\\TC / SE}} & "
         r"\textbf{\shortstack{p95 (s)\\TC / SE}} & \textbf{\shortstack{Chamadas\\TC / SE}} \\", r"\hline"]
    k = 0
    while k < len(resultados):   # blocos de linhas consecutivas do mesmo conjunto, ambiente e desenvolvimento
        j = k
        while j < len(resultados) and _bloco(resultados[j]) == _bloco(resultados[k]):
            j += 1
        bloco = resultados[k:j]
        rotulo = rf"\shortstack[l]{{{rotulo_conjunto(bloco[0])}\\{AMBIENTES[bloco[0]['par'].ambiente]}}}"
        if len(bloco) > 1:
            rotulo = rf"\multirow{{{len(bloco)}}}{{*}}{{{rotulo}}}"
        for i, r in enumerate(bloco):
            L.append(_linha_tabela(r, rotulo if i == 0 else ""))
        L.append(r"\hline")
        k = j
    comparaveis = [r for r in resultados if r["latencia_comparavel"]]
    sessoes = sum(1 for r in comparaveis if not r["mesma_maquina"])
    fonte = ("Elaborado pelos autores. Cada linha é um par de rodadas do mesmo modelo, sobre as mesmas consultas, "
             r"com a mesma especificação e no mesmo ambiente: A, \textit{Tool Calling} (TC); B, Saída Estruturada "
             r"(SE); na v3, o TC completo (descrições, ferramentas auxiliares e retorno do validador) e o controle "
             r"SE v3, com as mesmas descrições e o mesmo retorno. Linhas: " + "; ".join(_origens(resultados)) + ". "
             r"Acurácia por consulta; com repetições, cada consulta vale pela maioria delas. SE $-$ TC: diferença "
             r"de acurácia, com IC 95\% por \textit{bootstrap} pareado "
             rf"({lote._milhar(lote.REPETICOES_BOOTSTRAP)} reamostragens das consultas, semente 42). \textit{{p}}: "
             r"McNemar exato, uma observação por consulta. Domínio: acurácia fora das categorias F e E. F1 recusa: "
             r"média harmônica da precisão e do \textit{recall} da recusa nas consultas fora do domínio (na v1, a SE "
             r"não tem como recusar). Latência: mediana e percentil 95 da tradução, por execução e com todas as "
             r"chamadas ao modelo, só nos pares cujas duas rodadas têm, nos manifestos, a mesma GPU, a mesma versão "
             r"do Ollama e a mesma parcela do modelo na GPU")
    if sessoes:
        fonte += (f" (em {report.EXTENSO.get(sessoes, str(sessoes))} deles, TC e SE rodaram em sessões diferentes, "
                  "com a mesma GPU)")
    if any(r["par"].ambiente == "groq" for r in resultados):
        fonte += r"; ---: nuvem, com \textit{hardware} do provedor, não controlado"
    fonte += ". Chamadas: média de chamadas ao modelo por consulta (v1 e v2: uma, por construção)."
    L += [r"\end{tabular}}", r"\fonte{" + fonte + "}", r"\end{table}", ""]
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Conferência com as macros existentes
# ---------------------------------------------------------------------------

_RE_MACRO = re.compile(r"\\csname (res@[^\\]+)\\endcsname\{(.*)\}\s*$")


def ler_macros(texto: str) -> dict[str, str]:
    """{nome do csname: valor} das definições de um numeros*.tex."""
    saida = {}
    for linha in texto.splitlines():
        m = _RE_MACRO.search(linha)
        if m:
            saida[m.group(1)] = m.group(2)
    return saida


def diretorios_de_referencia(dir_resultados: Path) -> list[Path]:
    R = dir_resultados
    return [R / "consolidado", R / "consolidado_groq", R / "estacao" / "consolidado", R / "lote" / "consolidado",
            R / "lote2" / "consolidado"]


def macros_existentes(diretorios: list[Path]) -> tuple[dict[str, str], dict[str, str]]:
    """(valores, arquivo de origem) das macros de todos os numeros*.tex dos diretórios (o primeiro vence),
    fora o próprio numeros_ab.tex."""
    valores: dict[str, str] = {}
    origem: dict[str, str] = {}
    for d in diretorios:
        for arq in sorted(d.glob("numeros*.tex")) if d.is_dir() else []:
            if arq.name == "numeros_ab.tex":
                continue
            for k, v in ler_macros(arq.read_text(encoding="utf-8")).items():
                if k not in valores:
                    valores[k], origem[k] = v, _mostrar(arq)
    return valores, origem


def _causas(r: dict) -> dict[str, str]:
    reps = len(r["tc"]["repeticoes"])
    return {"exec": f"a fonte pontua a média das execuções (TC com {reps} repetições); a A/B, uma observação por "
                    f"consulta, pela maioria das repetições",
            "completo": f"a fonte usa todas as consultas de cada rodada (TC {r['ntc']}, SE {r['nse']}); a A/B, só "
                        f"as {r['n']} presentes nas duas",
            "ambas": f"a fonte usa a média das execuções e todas as consultas de cada rodada (TC {r['ntc']}); "
                     f"a A/B, a maioria das repetições nas {r['n']} comuns"}


def _verificacoes(r: dict, ref: Ref) -> list[dict]:
    """(medida, macro existente, valor da A/B no formato da fonte, [(causa, valor pelo critério da fonte)])."""
    V: list[dict] = []
    causas = _causas(r)
    lat = r["latencia_comparavel"]
    lados = (("tc", "TC"), ("se", "SE"))

    def v(medida: str, macro: str, nosso: str, alternativas=()) -> None:
        V.append({"medida": medida, "macro": macro, "nosso": nosso,
                  "alternativas": [(causas[c], val) for c, val in alternativas]})

    if ref.estilo in ("lote", "lote2"):
        for (lado, nome), cfg in zip(lados, (ref.tc, ref.se), strict=True):
            m, mc = r[lado], r[lado + "_completo"]
            base = f"res@{ref.ns}@{cfg}@"
            v(f"n {nome}", base + "n", lote._milhar(r["n"]), [("completo", lote._milhar(mc["n"]))])
            for rot, medida, f in (("acurácia", "acuracia", lambda x: report._pct(x["acuracia"])),
                                   ("IC", "ic", lambda x: _ic(x["ic"])),
                                   ("domínio", "accdominio", lambda x: report._pct(x["accdominio"])),
                                   ("F1 recusa", "recusaf", lambda x: report._f(x["recusa"]["f1"]))):
                v(f"{rot} {nome}", base + medida, f(m), [("completo", f(mc))])
            if lat:
                v(f"latência {nome}", base + "latmed", _s(m["latmed"]), [("completo", _s(mc["latmed"]))])
                v(f"p95 {nome}", base + "latp95", _s(m["latp95"]), [("completo", _s(mc["latp95"]))])
            if ref.estilo == "lote2" and m["chamadas"] is not None:
                v(f"chamadas {nome}", base + "chamadas", report._num(m["chamadas"], 2),
                  [("completo", report._num(mc["chamadas"], 2))])
        if ref.par:
            c, base = r["cmp"], f"res@{ref.ns}@{ref.par}@"
            v("só TC", base + "soa", str(c["so_a"]))
            v("só SE", base + "sob", str(c["so_b"]))
            v("p", base + "p", lote._p(c["p"]))
            v("SE − TC", base + "difacc", lote._pp(c["dif_acc"]))
            v("IC SE − TC", base + "icdifacc", lote._ic_pp(c["ic_dif_acc"]))
            if ref.estilo == "lote2":
                v("n do par", base + "n", lote._milhar(c["n"]))
    elif ref.estilo == "comparacao":
        base = f"res@{ref.ns}@{ref.chave}@"
        for lado, nome in lados:
            m, mc, e, ec = r[lado], r[lado + "_completo"], r[lado + "_exec"], r[lado + "_exec_completo"]
            for rot, medida, f, g in (("acurácia", "acuracia", lambda x: report._pct(x["acuracia"]),
                                       lambda x: report._pct(x["acuracia"])),
                                      ("IC", "ic", lambda x: _ic(x["ic"]), lambda x: _ic(x["ic"])),
                                      ("domínio (sem F)", "accsemf", lambda x: report._pct(x["accdominio"]),
                                       lambda x: report._pct(x["accsemf"]))):
                v(f"{rot} {nome}", base + medida + lado, f(m), [("exec", g(e)), ("completo", f(mc)), ("ambas", g(ec))])
        c = r["cmp"]
        v("n", base + "n", str(r["n"]), [("completo", str(r["tc_completo"]["n"]))])
        v("só TC", base + "sotc", str(c["so_a"]))
        v("só SE", base + "sose", str(c["so_b"]))
        v("p", base + "p", comparacao._p(c["p"]))

        def difpp(x: dict, y: dict) -> str:
            return report._num(100 * ((x["acuracia"] or 0) - (y["acuracia"] or 0)))

        v("TC − SE", base + "difpp", difpp(r["tc"], r["se"]),
          [("exec", difpp(r["tc_exec"], r["se_exec"])), ("completo", difpp(r["tc_completo"], r["se_completo"])),
           ("ambas", difpp(r["tc_exec_completo"], r["se_exec_completo"]))])
    elif ref.estilo == "report":   # rodada com Tool Calling do relatório geral (pfc-relatorio)
        base = f"res@{ref.ns}@{ref.chave}@"
        m, mc, e, ec = r["tc"], r["tc_completo"], r["tc_exec"], r["tc_exec_completo"]
        v("acurácia TC", base + "acuracia", report._pct(m["acuracia"]),
          [("exec", report._pct(e["acuracia"])), ("completo", report._pct(mc["acuracia"])),
           ("ambas", report._pct(ec["acuracia"]))])
        v("IC TC", base + "ic", _ic(m["ic"]), [("exec", _ic(e["ic"])), ("completo", _ic(mc["ic"])),
                                               ("ambas", _ic(ec["ic"]))])
        if lat and m["latmed"] is not None and mc["latmed"] is not None:
            v("latência TC (ms)", base + "latmed", f"{m['latmed']:.0f}", [("completo", f"{mc['latmed']:.0f}")])
            v("latência TC (s)", base + "latmeds", _s(m["latmed"], 1), [("completo", _s(mc["latmed"], 1))])
            v("p95 TC (s)", base + "latpnoventaecinco", _s(m["latp95"], 1), [("completo", _s(mc["latp95"], 1))])
    else:
        raise ValueError(f"estilo de referência desconhecido: {ref.estilo}")
    return V


# campos da tabela (e das macros) que cada verificação confere
CAMPOS_TABELA = ("n", "acctc", "accse", "dif", "icdif", "p", "domtc", "domse", "recusaftc", "recusafse",
                 "latmedtc", "latmedse", "latp95tc", "latp95se", "chamadastc", "chamadasse")
_CAMPOS = {"n": "n", "n do par": "n", "acurácia": "acc", "IC": "ic", "domínio": "dom", "F1 recusa": "recusaf",
           "latência": "latmed", "p95": "latp95", "chamadas": "chamadas", "só TC": "sotc", "só SE": "sose",
           "p": "p", "SE − TC": "dif", "TC − SE": "dif", "IC SE − TC": "icdif"}


def campo(medida: str) -> str:
    """Campo da tabela conferido por uma verificação ('acurácia TC' -> 'acctc', 'p95 SE (s)' -> 'latp95se')."""
    m = re.sub(r" \((ms|s|sem F)\)", "", medida)
    if m in _CAMPOS:
        return _CAMPOS[m]
    base, _, lado = m.rpartition(" ")
    if lado in ("TC", "SE") and base in _CAMPOS:
        return _CAMPOS[base] + ("" if base == "n" else lado.lower())
    raise ValueError(f"verificação sem campo conhecido: {medida!r}")


def sem_equivalente(resultados: list[dict], conf: list[dict]) -> dict[str, list[str]]:
    """Por par, os campos da tabela que nenhuma macro existente confere (números novos da A/B)."""
    conferidos: dict[str, set[str]] = {}
    for x in conf:
        if x["situacao"] != "sem_referencia":
            conferidos.setdefault(x["par"], set()).add(x["campo"])
    saida = {}
    for r in resultados:
        campos = [c for c in CAMPOS_TABELA if r["latencia_comparavel"] or not c.startswith("lat")]
        faltam = [c for c in campos if c not in conferidos.get(r["chave"], set())]
        if faltam:
            saida[r["chave"]] = faltam
    return saida


def conferir(resultados: list[dict], existentes: dict[str, str]) -> list[dict]:
    """Cada verificação com a situação: igual, explicada (com a causa), divergente ou sem_referencia."""
    saida = []
    for r in resultados:
        for ref in r["par"].refs:
            for x in _verificacoes(r, ref):
                existente = existentes.get(x["macro"])
                causa = ""
                if existente is None:
                    situacao = "sem_referencia"
                elif existente == x["nosso"]:
                    situacao = "igual"
                else:
                    causa = next((c for c, val in x["alternativas"] if val == existente), "")
                    situacao = "explicada" if causa else "divergente"
                saida.append({"par": r["chave"], "medida": x["medida"], "campo": campo(x["medida"]),
                              "macro": x["macro"], "nosso": x["nosso"], "existente": existente,
                              "situacao": situacao, "causa": causa})
    return saida


# ---------------------------------------------------------------------------
# Relatório em Markdown e JSON
# ---------------------------------------------------------------------------

def _md(v: str) -> str:
    """Um valor das macros legível em Markdown."""
    return (v.replace("\\%", "%").replace("$<$\\,", "< ").replace("$^\\dagger$", "†").replace("$^{*}$", "*")
            .replace("---", "—"))


def relatorio_md(res: dict[str, Any], conf: list[dict], referencias: list[str]) -> str:
    rs = res["resultados"]
    L = ["# Teste A/B — Tool Calling (A) × Saída Estruturada (B)", "",
         "Gerado por `python -m pfc_busca.evaluation.ab`, com as funções de `lote.py`, `lote2.py` e `comparacao.py` "
         "(nenhuma medida calculada à parte). Um par = o mesmo modelo, as mesmas consultas, a mesma especificação e "
         "o mesmo ambiente. † = desenvolvimento (dentro da amostra que orientou o desenho da especificação); "
         "* = rodadas com consultas diferentes (o par usa só as comuns).", "",
         "| Par (macro) | Conjunto | Modelo | Espec. | Amb. | n | Acurácia TC / SE | SE − TC [IC 95%] | Só TC / Só SE "
         "| p | Domínio TC / SE | F1 recusa TC / SE | Latência med. TC / SE (s) | p95 TC / SE (s) | Chamadas TC / SE |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rs:
        par, c, tc, se = r["par"], r["cmp"], r["tc"], r["se"]
        L.append(f"| `{r['chave']}` | {rotulo_conjunto(r)} | {nome_modelo(par.modelo)} | "
                 f"{par.espec}{'†' if par.desenvolvimento else ''} | {AMBIENTES[par.ambiente]} | "
                 f"{r['n']}{'*' if r['incompleto'] else ''} | "
                 f"{_md(report._pct(tc['acuracia']))} / {_md(report._pct(se['acuracia']))} | "
                 f"{lote._pp(c['dif_acc'])} [{lote._ic_pp(c['ic_dif_acc'])}] | {c['so_a']} / {c['so_b']} | "
                 f"{_md(lote._p(c['p']))} | {_md(report._pct(tc['accdominio']))} / {_md(report._pct(se['accdominio']))} | "
                 f"{report._f(tc['recusa']['f1'])} / {report._f(se['recusa']['f1'])} | "
                 f"{_md(_lat(r, 'tc', 'latmed'))} / {_md(_lat(r, 'se', 'latmed'))} | "
                 f"{_md(_lat(r, 'tc', 'latp95'))} / {_md(_lat(r, 'se', 'latp95'))} | "
                 f"{report._num(tc['chamadas'], 2)} / {report._num(se['chamadas'], 2)} |")
    conta = Counter(veredito(r) for r in rs)
    semdev = [r for r in rs if not r["par"].desenvolvimento]
    conta_sd = Counter(veredito(r) for r in semdev)
    L += ["", f"Resumo (McNemar, p < {report._f(ALFA, 2)}): {len(rs)} pares — SE melhor em {conta['se']}, TC melhor em "
          f"{conta['tc']}, empate em {conta['empate']}; fora do desenvolvimento, {len(semdev)} pares — SE melhor em "
          f"{conta_sd['se']}, TC melhor em {conta_sd['tc']}, empate em {conta_sd['empate']}.", "",
          "## Rodadas de cada par", "",
          "| Par | Rodada TC | Rodada SE | Consultas TC / SE | Repetições TC / SE | Latência: hardware |",
          "|---|---|---|---|---|---|"]
    for r in rs:
        lat = r["hardware"] if r["latencia_comparavel"] else (
            f"não comparável ({r['hardware']}); medida: {_s(r['tc']['latmed'])} / {_s(r['se']['latmed'])} s")
        L.append(f"| `{r['chave']}` | `{r['pastas'][0]}` | `{r['pastas'][1]}` | {r['ntc']} / {r['nse']} | "
                 f"{len(r['tc']['repeticoes'])} / {len(r['se']['repeticoes'])} | {lat} |")
    if res["avisos"]:
        L += ["", "Avisos:", ""] + [f"- {a}" for a in res["avisos"]]
    situacoes = Counter(x["situacao"] for x in conf)
    L += ["", "## Conferência com as macros já existentes", "",
          f"Referências: {', '.join(f'`{x}`' for x in referencias) or 'nenhuma'}.", "",
          f"- verificações: {len(conf)} — iguais: {situacoes['igual']}; divergentes explicadas: "
          f"{situacoes['explicada']}; divergentes não explicadas: {situacoes['divergente']}; sem macro "
          f"correspondente: {situacoes['sem_referencia']}.", ""]
    difs = [x for x in conf if x["situacao"] in ("explicada", "divergente")]
    if difs:
        L += ["| Par | Medida | Macro existente | A/B | Existente | Situação e causa |", "|---|---|---|---|---|---|"]
        for x in difs:
            situacao = f"explicada: {x['causa']}" if x["situacao"] == "explicada" else "**NÃO EXPLICADA**"
            L.append(f"| `{x['par']}` | {x['medida']} | `{x['macro']}` | {_md(x['nosso'])} | {_md(x['existente'])} | "
                     f"{situacao} |")
        L.append("")
    sem = Counter(x["par"] for x in conf if x["situacao"] == "sem_referencia")
    if sem:
        L += ["Verificações sem a macro correspondente na referência (o par ou a medida não existem nas análises "
              "existentes): " + "; ".join(f"`{p}` {n}" for p, n in sem.items()) + ".", ""]
    novos = sem_equivalente(rs, conf)
    if novos:
        L += ["Números da tabela sem equivalente em nenhuma macro existente (novos da A/B; os demais foram "
              "conferidos): " + "; ".join(f"`{p}`: {', '.join(cs)}" for p, cs in novos.items()) + ".", ""]
    iguais = Counter(x["par"] for x in conf if x["situacao"] == "igual")
    L += ["Iguais por par: " + ("; ".join(f"`{p}` {n}" for p, n in iguais.items()) or "nenhum") + ".", ""]
    return "\n".join(L)


def _json(res: dict[str, Any], conf: list[dict]) -> dict[str, Any]:
    def lado(m: dict) -> dict:
        return {k: m[k] for k in ("n", "acuracia", "ic", "accdominio", "n_dominio", "recusa", "f1", "latmed", "latp95",
                                  "chamadas", "repeticoes")}
    pares_json = []
    for r in res["resultados"]:
        par = r["par"]
        pares_json.append({"chave": r["chave"], "conjunto": par.conjunto, "ambiente": par.ambiente,
                           "modelo": par.modelo, "espec": par.espec, "desenvolvimento": par.desenvolvimento,
                           "pastas": list(r["pastas"]), "n": r["n"], "ntc": r["ntc"], "nse": r["nse"],
                           "incompleto": r["incompleto"], "latencia_comparavel": r["latencia_comparavel"],
                           "hardware": r["hardware"], "tc": lado(r["tc"]), "se": lado(r["se"]),
                           "par_tc_se": {k: r["cmp"][k] for k in ("n", "so_a", "so_b", "p", "dif_acc", "ic_dif_acc")},
                           "veredito": veredito(r)})
    return lote._serializavel({"dir": res["dir"], "avisos": res["avisos"], "pares": pares_json, "conferencia": conf})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--resultados", type=Path, default=DIR_RESULTADOS, help="pasta das rodadas (padrão: results/)")
    p.add_argument("--saida", type=Path, help="pasta de saída (padrão: RESULTADOS/ab)")
    p.add_argument("--paper", type=Path, help="diretório do texto: grava tab_ab.tex e numeros_ab.tex em DIR/tabelas")
    p.add_argument("--referencias", type=Path, action="append",
                   help="diretório com numeros*.tex para a conferência (repetível); padrão: PAPER/tabelas com "
                        "--paper, senão os consolidados de RESULTADOS")
    p.add_argument("--estrito", action="store_true", help="sai com código 1 se houver divergência não explicada")
    args = p.parse_args(argv)
    res = gerar(args.resultados)
    for a in res["avisos"]:
        print(f"aviso: {a}")
    if not res["resultados"]:
        print(f"nenhum par TC × SE com as duas rodadas em {args.resultados}")
        return 0
    dirs_ref = args.referencias or ([args.paper / "tabelas"] if args.paper else diretorios_de_referencia(args.resultados))
    existentes, _ = macros_existentes(dirs_ref)       # lidas antes de gravar numeros_ab.tex no texto
    conf = conferir(res["resultados"], existentes)
    saida = args.saida or (args.resultados / "ab")
    saida.mkdir(parents=True, exist_ok=True)
    arquivos_tex = {"tab_ab.tex": tabela(res["resultados"]), "numeros_ab.tex": macros(res["resultados"])}
    for nome, conteudo in arquivos_tex.items():
        (saida / nome).write_text(conteudo, encoding="utf-8")
        if args.paper:
            (args.paper / "tabelas").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(saida / nome, args.paper / "tabelas" / nome)
    refs_txt = [_mostrar(d) for d in dirs_ref if d.is_dir()]
    (saida / "ab.md").write_text(relatorio_md(res, conf, refs_txt), encoding="utf-8")
    (saida / "ab.json").write_text(json.dumps(_json(res, conf), ensure_ascii=False, indent=1), encoding="utf-8")
    s = Counter(x["situacao"] for x in conf)
    print(f"A/B: {len(res['resultados'])} pares -> {_mostrar(saida)}"
          + (f" e {args.paper / 'tabelas'}" if args.paper else ""))
    print(f"conferência: {len(conf)} verificações — {s['igual']} iguais, {s['explicada']} divergentes explicadas, "
          f"{s['divergente']} não explicadas, {s['sem_referencia']} sem macro correspondente")
    for x in conf:
        if x["situacao"] == "divergente":
            print(f"  NÃO EXPLICADA: {x['par']} {x['medida']} ({x['macro']}): A/B {x['nosso']} × {x['existente']}")
    return 1 if args.estrito and s["divergente"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
