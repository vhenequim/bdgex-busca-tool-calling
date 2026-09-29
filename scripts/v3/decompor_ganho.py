"""De onde vem o acerto da v3: primeira resposta do modelo × correção pelo retorno do código.

    python scripts/v3/decompor_ganho.py results/dev_v3/ciclo2/tc3-gemma4-e4b-it-qat [outra pasta ...]

Para cada execução, reconstrói a PRIMEIRA decisão do modelo (os parâmetros da primeira chamada a
buscar_catalogo, ou a recusa, se ela veio antes de qualquer busca) a partir do traço gravado, e a pontua com
o mesmo gabarito da resposta final. A diferença entre as duas é o que o retorno (validação, recusa com
retorno, resposta do usuário simulado) acrescentou. Na Saída Estruturada v3, a primeira decisão é o primeiro
objeto do histórico de tentativas.
"""

from __future__ import annotations

import ast
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

from pfc_busca.evaluation import metrics  # noqa: E402
from pfc_busca.evaluation.run_evaluation import (  # noqa: E402
    carregar_execucoes,
    dataset_da_rodada,
    repontuar,
)

_SEM = object()


def _extra(linha: dict, chave: str, padrao=None):
    v = (linha.get("extras") or {}).get(chave, padrao)
    if isinstance(v, str):
        try:
            return ast.literal_eval(v)
        except (ValueError, SyntaxError):
            return v
    return v


def primeira_decisao(linha: dict):
    """Parâmetros da primeira busca, None para recusa/não busca, ou _SEM se o traço não permite saber."""
    historico = _extra(linha, "historico")
    if isinstance(historico, list) and historico:          # Saída Estruturada v3
        h = historico[0]
        if isinstance(h, str):
            return None
        return h.get("params") if isinstance(h, dict) else _SEM
    traco = _extra(linha, "traco")
    if not isinstance(traco, list):
        return _SEM
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


def decompor(pasta: Path) -> dict:
    validas, _ = repontuar(carregar_execucoes(pasta), dataset_da_rodada(pasta))
    ids = (RAIZ / "data" / "lote_validacao" / "dev_v3_ids.txt")
    if "dev_v3" in str(pasta) and ids.exists():
        dev = set(ids.read_text(encoding="utf-8").strip().split(","))
        validas = [x for x in validas if x["id"] in dev]
    linhas = [x for x in validas if not x.get("observacional")]
    c = Counter()
    for x in linhas:
        final = metrics.avaliar_linha(x).correto
        p = primeira_decisao(x)
        if p is _SEM:
            c["sem_traco"] += 1
            continue
        primeira = correto_com(x, p)
        c["n"] += 1
        c["final"] += final
        c["primeira"] += primeira
        c["consertou"] += final and not primeira
        c["estragou"] += primeira and not final
        if _extra(x, "recusa_contestada") in (True, "True"):
            c["contestadas"] += 1
            c["contestada_" + ("F" if not x["espera_tool_call"] else "dominio") + ("_certa" if final else "_errada")] += 1
        if int(_extra(x, "avisos_recebidos", 0) or 0) > 0:
            c["com_aviso"] += 1
    return dict(c)


def main() -> int:
    for arg in sys.argv[1:]:
        c = decompor(Path(arg))
        n = c.get("n", 0) or 1
        print(f"{Path(arg).name}: n={c.get('n')}  primeira decisão {c.get('primeira', 0)}/{n} = {c.get('primeira', 0)/n:.1%}  "
              f"final {c.get('final', 0)}/{n} = {c.get('final', 0)/n:.1%}  | retorno consertou {c.get('consertou', 0)}, "
              f"estragou {c.get('estragou', 0)} | com aviso {c.get('com_aviso', 0)} | recusas contestadas "
              f"{c.get('contestadas', 0)} {({k: v for k, v in c.items() if k.startswith('contestada_')})}"
              + (f" | sem traço {c['sem_traco']}" if c.get("sem_traco") else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
