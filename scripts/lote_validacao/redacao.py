"""Etapa 2 do lote de validação: redação das consultas a partir dos alvos.

    python scripts/lote_validacao/redacao.py preparar    # alvos.json -> redacao/tarefa_NN.json
    python scripts/lote_validacao/redacao.py coletar     # redacao/saida_NN.json -> consultas_redigidas.json

Cada tarefa leva ~130 alvos embaralhados (semente fixa), de todas as famílias, para que cada
redator escreva consultas variadas. O redator recebe só o que precisa para escrever: registro de
linguagem, persona, o que a consulta deve dizer (`pedido`) e o que não pode dizer (`proibido`).
O gabarito, as categorias e as notas de anotação ficam fora da tarefa.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config_lote  # noqa: E402

DIR = config_lote.DIR
DIR_REDACAO = DIR / "redacao"
ARQ_ALVOS = DIR / "alvos.json"
ARQ_SAIDA = DIR / "consultas_redigidas.json"
N_TAREFAS = config_lote.N_TAREFAS
SEMENTE_TAREFAS = config_lote.SEMENTES["tarefas"]

INSTRUCOES_REDATOR = """Você vai escrever consultas de usuários reais ao assistente de busca do acervo de produtos cartográficos do Exército Brasileiro (BDGEx, Diretoria de Serviço Geográfico). O assistente recebe a mensagem do usuário e a transforma em uma busca no catálogo. As consultas vão compor um conjunto de avaliação: cada uma precisa dizer exatamente o que o alvo pede, nem mais nem menos.

Para CADA alvo da lista, escreva UMA mensagem em português do Brasil:
1. A mensagem deve conter TODOS os itens de `pedido`. Quando o item diz "escrito como X" ou "escrita como X", o trecho X precisa aparecer literalmente na mensagem (maiúsculas, acentos e pontuação podem mudar só no registro "sem_acento"). Nomes de lugares, de cartas, códigos e números entram exatamente como dados.
2. Respeite TODOS os itens de `proibido`. Em especial, não acrescente critério de busca nenhum além dos pedidos: nenhum outro lugar, escala, tipo de produto, data, código, projeto, CGEO, ordem ou quantidade. A persona e o registro mudam só o tom e o vocabulário, nunca os critérios (um "oficial planejando uma operação" não cita a região da operação se o alvo não pede).
3. Siga o registro de linguagem (`registro_descricao`) e escreva como a persona escreveria. No registro "sem_acento", a mensagem inteira fica em minúsculas e sem acentos, inclusive os nomes. No registro "erro_digitacao", faça UM erro de digitação leve numa palavra comum, nunca num nome, código, número ou expressão de tempo.
4. Varie a construção de uma mensagem para outra: não repita a mesma abertura nem o mesmo molde. Soe como uma pessoa real digitando numa caixa de busca ou num chat — nada de texto de formulário, nada de explicar o sistema, nada de aspas em volta dos valores (a não ser que fosse natural).
5. Não escreva nomes de campos do sistema (keyword, scale, supplyArea, productType, enum...).
6. Nos alvos fora do domínio (pedido começa com "escreva uma mensagem de usuário do tipo"), a mensagem não pode pedir produto cartográfico do território brasileiro que exista num acervo.

Entregue um único arquivo JSON, no caminho indicado na tarefa, no formato {"<id>": "<mensagem>", ...}, com uma entrada para cada id da tarefa, na mesma ordem. Não escreva nada além do JSON no arquivo."""


def preparar() -> int:
    alvos = json.loads(ARQ_ALVOS.read_text(encoding="utf-8"))["alvos"]
    ordem = list(alvos)
    random.Random(SEMENTE_TAREFAS).shuffle(ordem)
    DIR_REDACAO.mkdir(parents=True, exist_ok=True)
    tamanho = -(-len(ordem) // N_TAREFAS)
    for k in range(N_TAREFAS):
        parte = ordem[k * tamanho:(k + 1) * tamanho]
        tarefa = {
            "tarefa": k + 1, "saida": (DIR_REDACAO / f"saida_{k + 1:02d}.json").relative_to(RAIZ).as_posix(),
            "instrucoes": INSTRUCOES_REDATOR,
            "alvos": [{c: a[c] for c in ("id", "registro", "registro_descricao", "persona", "pedido", "proibido")}
                      for a in parte],
        }
        (DIR_REDACAO / f"tarefa_{k + 1:02d}.json").write_text(json.dumps(tarefa, ensure_ascii=False, indent=1),
                                                             encoding="utf-8", newline="\n")
    print(f"{N_TAREFAS} tarefas de até {tamanho} alvos em {DIR_REDACAO.relative_to(RAIZ)}")
    return 0


def coletar() -> int:
    alvos = json.loads(ARQ_ALVOS.read_text(encoding="utf-8"))["alvos"]
    redigidas: dict[str, str] = {}
    problemas = []
    for k in range(1, N_TAREFAS + 1):
        tarefa = json.loads((DIR_REDACAO / f"tarefa_{k:02d}.json").read_text(encoding="utf-8"))
        arq = DIR_REDACAO / f"saida_{k:02d}.json"
        if not arq.exists():
            problemas.append(f"tarefa {k}: sem saída")
            continue
        saida = json.loads(arq.read_text(encoding="utf-8"))
        esperados = [a["id"] for a in tarefa["alvos"]]
        faltando = [i for i in esperados if not str(saida.get(i, "")).strip()]
        extras = [i for i in saida if i not in esperados]
        if faltando or extras:
            problemas.append(f"tarefa {k}: {len(faltando)} faltando, {len(extras)} ids estranhos")
        for i in esperados:
            if str(saida.get(i, "")).strip():
                redigidas[i] = " ".join(str(saida[i]).split())
    ARQ_SAIDA.write_text(json.dumps({i: redigidas[i] for i in (a["id"] for a in alvos) if i in redigidas},
                                    ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"{len(redigidas)}/{len(alvos)} consultas redigidas -> {ARQ_SAIDA.relative_to(RAIZ)}")
    for p in problemas:
        print("  ", p)
    return 0 if not problemas else 1


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else ""
    if comando == "preparar":
        raise SystemExit(preparar())
    if comando == "coletar":
        raise SystemExit(coletar())
    print(__doc__)
    raise SystemExit(2)
