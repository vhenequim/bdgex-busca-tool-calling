"""Gera src/pfc_busca/prototipo_termos.py a partir do dicionário COMMON_TERMS do protótipo.

    python scripts/extrair_termos_prototipo.py [caminho/para/constants.ts]

O padrão é o clone do protótipo como pasta irmã do repositório
(../prototipo_busca_llm-main/backend/src/services/llm/constants.ts). O dicionário é
usado só pela linha de base que reproduz o método do protótipo (agent_estruturado.py).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEM_PADRAO = RAIZ.parent / "prototipo_busca_llm-main" / "backend" / "src" / "services" / "llm" / "constants.ts"
DESTINO = RAIZ / "src" / "pfc_busca" / "prototipo_termos.py"

# 'chave': 'valor',   ou   chave: 'valor',
PADRAO = re.compile(r"""^\s*(?:'([^']*)'|"([^"]*)"|([A-Za-z_][\w]*))\s*:\s*'([^']*)'\s*,?\s*$""")


def extrair(texto: str) -> list[tuple[str, str]]:
    corpo = texto.split("COMMON_TERMS", 1)[1]
    corpo = corpo[corpo.index("{") + 1: corpo.rindex("}")]
    pares = []
    for linha in corpo.splitlines():
        if not linha.strip() or linha.strip().startswith("//"):
            continue
        m = PADRAO.match(linha)
        if not m:
            raise ValueError(f"linha não reconhecida: {linha!r}")
        chave = m.group(1) if m.group(1) is not None else (m.group(2) if m.group(2) is not None else m.group(3))
        pares.append((chave, m.group(4)))
    return pares


def main() -> int:
    origem = Path(sys.argv[1]) if len(sys.argv) > 1 else ORIGEM_PADRAO
    pares = extrair(origem.read_text(encoding="utf-8"))
    linhas = [
        '"""Dicionário COMMON_TERMS do protótipo do 1º CGEO (backend/src/services/llm/constants.ts).',
        "",
        "Gerado por scripts/extrair_termos_prototipo.py; não editar à mão. Copyright do protótipo:",
        "Exército Brasileiro - Diretoria de Serviço Geográfico, licença MIT (THIRD_PARTY_NOTICES.md).",
        "Usado apenas pela linha de base que reproduz o método do protótipo (agent_estruturado.py);",
        "a solução avaliada não tem dicionário de normalização.",
        '"""',
        "",
        "COMMON_TERMS: dict[str, str] = {",
    ]
    linhas += [f"    {chave!r}: {valor!r}," for chave, valor in pares]
    linhas += ["}", ""]
    DESTINO.write_text("\n".join(linhas), encoding="utf-8")
    print(f"{len(pares)} entradas -> {DESTINO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
