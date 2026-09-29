"""Etapa 3 do lote de validação: anotação às cegas das consultas redigidas.

    python scripts/lote_validacao/anotacao.py preparar   # consultas_redigidas.json -> anotacao/tarefa_{A,B}NN.json
    python scripts/lote_validacao/anotacao.py coletar    # anotacao/saida_*.json -> anotacao/anotacao_{A,B}.json

Cegamento: o anotador recebe só o texto da consulta, com identificador neutro (Q0001...) e em
ordem embaralhada; não recebe o alvo, a família, o gabarito nem a persona. A correspondência
identificador neutro → alvo não é gravada durante a anotação: `coletar` a recalcula a partir da
mesma semente.

Duas passadas independentes:
- A: todas as consultas (15 tarefas), a anotação que decide se a consulta entra no lote;
- B: amostra aleatória de 20% (semente fixa), anotada por outros agentes, para medir a
  concordância entre anotadores (A × B), independente do gabarito por construção.
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
DIR_ANOTACAO = DIR / "anotacao"
ARQ_REDIGIDAS = DIR / "consultas_redigidas.json"
SEMENTE_IDS = config_lote.SEMENTES["ids"]
SEMENTE_AMOSTRA_B = config_lote.SEMENTES["amostra_b"]
N_TAREFAS_A = config_lote.N_TAREFAS
FRACAO_B = 0.20
TAMANHO_TAREFA_B = 130
DATA_REFERENCIA = "2026-09-24"

INSTRUCOES_ANOTADOR = """Você é anotador independente do gabarito de um conjunto de avaliação. Cada item é a mensagem de um usuário ao assistente de busca do acervo cartográfico da DSG, que transforma a mensagem numa chamada da ferramenta buscar_catalogo. Anote, para cada mensagem, a chamada correta — ou que a ferramenta não deve ser chamada.

Referências (leia-as inteiras antes de começar e siga-as à risca; em caso de dúvida, o manual decide):
- o manual de anotação, docs/manual_de_anotacao.md (princípios P1–P6, regras por campo, seção 3 e as extensões da seção 6);
- a definição da ferramenta, FERRAMENTA_BUSCAR_CATALOGO em src/pfc_busca/schema.py (enumerados e descrições dos parâmetros).
Para saber se um nome é de município brasileiro (seções 6.3 e 6.4), você pode consultar a lista oficial do IBGE em data/lote_validacao/ibge_municipios.json (campo "nome").

Data de referência D = 2026-09-24 (quinta-feira). Escreva períodos como datas ISO concretas resolvidas com D.

Formato de cada anotação (um objeto por mensagem):
{
  "id": "<id da mensagem>",
  "chamar_ferramenta": true | false,
  "aceita_nao_chamar": true | false,   // true só na categoria E (seção 6.1): buscar sem filtros e não buscar são ambos corretos
  "observacional": true | false,       // P6
  "parametros": {<campo>: <valor canônico da leitura preferencial>},
  "valores_alternativos": [{"campo": "<campo>", "valores": [<todos os valores aceitos, o preferencial primeiro>]}],
  "campos_opcionais": ["<campo>", ...],
  "leituras_estruturais": [{<leitura completa alternativa, com todos os campos>}],
  "justificativa": "<uma frase citando a regra do manual>"
}
Omita "valores_alternativos", "campos_opcionais" e "leituras_estruturais" quando não houver. Fora do domínio: "chamar_ferramenta": false e "parametros": {}. Categoria E: "chamar_ferramenta": true, "aceita_nao_chamar": true e "parametros": {} (se não houver nenhum critério representável). Expressões de tempo com mais de uma leitura (tabelas das seções 2 e 6.2) vão em "valores_alternativos"; período sem verbo que desempate vai também em "leituras_estruturais" com o campo trocado.

Anote pelo que o TEXTO diz, não pelo que o usuário provavelmente quis. Não invente nada que o texto não sustente (P1); não deixe de fora nada que ele sustente.

Entregue um único arquivo JSON, no caminho indicado na tarefa, com a lista de anotações [{...}, {...}], uma por id, na mesma ordem da tarefa."""


def _ordem(redigidas: dict[str, str]) -> list[tuple[str, str]]:
    """[(id_neutro, id_alvo)] — embaralhamento com semente fixa."""
    ids = sorted(redigidas)
    random.Random(SEMENTE_IDS).shuffle(ids)
    return [(f"Q{k + 1:04d}", i) for k, i in enumerate(ids)]


def _amostra_b(ordem: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return random.Random(SEMENTE_AMOSTRA_B).sample(ordem, round(FRACAO_B * len(ordem)))


def _tarefas(ordem: list[tuple[str, str]], redigidas: dict[str, str]) -> dict[str, list[dict]]:
    tarefas: dict[str, list[dict]] = {}
    tamanho = -(-len(ordem) // N_TAREFAS_A)
    for k in range(N_TAREFAS_A):
        parte = ordem[k * tamanho:(k + 1) * tamanho]
        tarefas[f"A{k + 1:02d}"] = [{"id": n, "consulta": redigidas[i]} for n, i in parte]
    amostra = _amostra_b(ordem)
    random.Random(SEMENTE_AMOSTRA_B + 2).shuffle(amostra)
    for k in range(-(-len(amostra) // TAMANHO_TAREFA_B)):
        parte = amostra[k * TAMANHO_TAREFA_B:(k + 1) * TAMANHO_TAREFA_B]
        tarefas[f"B{k + 1:02d}"] = [{"id": n, "consulta": redigidas[i]} for n, i in parte]
    return tarefas


def preparar() -> int:
    redigidas = json.loads(ARQ_REDIGIDAS.read_text(encoding="utf-8"))
    ordem = _ordem(redigidas)
    DIR_ANOTACAO.mkdir(parents=True, exist_ok=True)
    tarefas = _tarefas(ordem, redigidas)
    for nome, itens in tarefas.items():
        (DIR_ANOTACAO / f"tarefa_{nome}.json").write_text(json.dumps({
            "tarefa": nome, "saida": (DIR_ANOTACAO / f"saida_{nome}.json").relative_to(RAIZ).as_posix(),
            "data_referencia": DATA_REFERENCIA, "instrucoes": INSTRUCOES_ANOTADOR, "consultas": itens,
        }, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"{len(tarefas)} tarefas ({sum(1 for n in tarefas if n[0] == 'A')} A, "
          f"{sum(1 for n in tarefas if n[0] == 'B')} B) em {DIR_ANOTACAO.relative_to(RAIZ)}")
    return 0


def coletar() -> int:
    redigidas = json.loads(ARQ_REDIGIDAS.read_text(encoding="utf-8"))
    ordem = _ordem(redigidas)
    neutro_para_alvo = dict(ordem)
    tarefas = _tarefas(ordem, redigidas)
    problemas = []
    for passada in ("A", "B"):
        anot: dict[str, dict] = {}
        for nome, itens in tarefas.items():
            if nome[0] != passada:
                continue
            arq = DIR_ANOTACAO / f"saida_{nome}.json"
            if not arq.exists():
                problemas.append(f"{nome}: sem saída")
                continue
            lista = json.loads(arq.read_text(encoding="utf-8"))
            por_id = {a.get("id"): a for a in lista if isinstance(a, dict)}
            faltando = [x["id"] for x in itens if x["id"] not in por_id]
            if faltando:
                problemas.append(f"{nome}: {len(faltando)} sem anotação ({faltando[:3]})")
            for x in itens:
                if x["id"] in por_id:
                    alvo = neutro_para_alvo[x["id"]]
                    anot[alvo] = {**por_id[x["id"]], "id": alvo, "id_neutro": x["id"]}
        (DIR_ANOTACAO / f"anotacao_{passada}.json").write_text(
            json.dumps(dict(sorted(anot.items())), ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
        print(f"anotação {passada}: {len(anot)} consultas")
    (DIR_ANOTACAO / "mapa_ids.json").write_text(json.dumps(dict(ordem), ensure_ascii=False, indent=0),
                                                encoding="utf-8", newline="\n")
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
