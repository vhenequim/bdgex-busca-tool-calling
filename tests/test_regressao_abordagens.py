"""Regressão do registro de abordagens: nomes, prefixos e hashes do manifesto não podem mudar.

Os valores abaixo foram capturados do `run_evaluation` ANTES de ele passar a ler o registro
(`pfc_busca.abordagens`). Cada rodada em results/ é identificada pelo prefixo da pasta e pelos hashes
de prompt e de ferramenta gravados no manifesto; se um deles mudar, `pfc-conferir` passa a acusar as
rodadas da tese e uma retomada deixa de reconhecer a própria pasta.

Os hashes de prompt da v3 dependem de `src/pfc_busca/dados/indice_folhas.json` (entra no texto do hash;
não é versionado): sem ele, só essa parte do teste é pulada.
"""

import json
from pathlib import Path

import pytest

from pfc_busca import ferramentas
from pfc_busca.evaluation import run_evaluation as rv

RAIZ = Path(__file__).resolve().parents[1]
V3 = {"tool_calling_v3d", "tool_calling_v3a", "tool_calling_v3", "saida_estruturada_v3"}
SEM_INDICE = not (ferramentas.DADOS / "indice_folhas.json").exists()

# abordagem: (prefixo, hash_prompt, hash_ferramenta), na ordem de --abordagem
ESPERADO = {
    "tool_calling": ("", "7163a8817c2443a21b4da74fd72438245aa46e9f6e7f947e0ce6b3e950cdacef",
                     "10a0108d671fa358496d925f281d42b42b4b54c0ff4da4c1be4509caa95ef4f6"),
    "saida_estruturada": ("se-", "70d651a6a248145ba13354ed58674ab15329406b89cf491e98d99d4ff50240b8",
                          "10a0108d671fa358496d925f281d42b42b4b54c0ff4da4c1be4509caa95ef4f6"),
    "prototipo": ("prototipo-", "d65c76609dcbd06cfa11718791b26e59460d8fad316b8ba95301052a8bcbb272",
                  "10a0108d671fa358496d925f281d42b42b4b54c0ff4da4c1be4509caa95ef4f6"),
    "tool_calling_v2": ("tc2-", "5f3731599ce274854b64ffcef26176a3dd5e3a69bf54ce0526d4ffbc11c8955d",
                        "3b45572c149fd791d66e88fd68ba5472d826a4cae0eb377cf45e8b535d8abd39"),
    "saida_estruturada_v2": ("se2-", "c6cef658e94aa13a518aae8295edd6f6f0f5167bf8802c109e902cbe5710ab93",
                             "da5592d693a4db0791fbd3c98ccaee3a55f1f016a14910b8e73c5979a7d97d69"),
    "tool_calling_v3d": ("tc3d-", "9723e508ea82ce7edd60d4853cec4a2c701835a8bf2c91fcdcc90cb433c98b39",
                         "1af9423399abb1d0fc972d5602f8bc6fe271ff60a4243c45fac51f9d65e891fe"),
    "tool_calling_v3a": ("tc3a-", "bb38c7ecd8a3e67a71732bef5a6d37a5644a374d4b45d3fc19001f1fc597184d",
                         "dd75578bc312fecf4d0a6608021e9517e966646f21add5ff7864d2542f1e3404"),
    "tool_calling_v3": ("tc3-", "c6bfce53a1f6d566d22a24ea84fc786984ecb9b67ea48619661622743ffaea37",
                        "fc57b33412d7318333f2a05122a4fac99addcfabb7c24289ab3c55c54e492376"),
    "saida_estruturada_v3": ("se3-", "fb71acc6fdde7dbf3db18466b9ec3ac2caabd7f6a84050f752d24fe4530e8b5e",
                             "9f4513fa57c62c1512c635a384e7596e4e1dbb7ba944fcb82bc7bae8e23e446f"),
}
SO_OLLAMA = ("prototipo", "tool_calling_v2", "saida_estruturada_v2", "tool_calling_v3d", "tool_calling_v3a",
             "tool_calling_v3", "saida_estruturada_v3")


def test_nomes_ordem_e_so_ollama():
    assert rv.ABORDAGENS == list(ESPERADO)
    assert list(rv.PREFIXO_ABORDAGEM) == list(ESPERADO)
    assert tuple(rv.SO_OLLAMA) == SO_OLLAMA


@pytest.mark.parametrize("abordagem", list(ESPERADO))
def test_prefixo_slug_e_hash_da_ferramenta(abordagem):
    prefixo, _, hash_ferramenta = ESPERADO[abordagem]
    assert rv.PREFIXO_ABORDAGEM[abordagem] == prefixo
    assert rv.slug("gemma4:e4b-it-qat", "ollama", abordagem) == prefixo + "gemma4-e4b-it-qat"
    assert rv.slug("qwen/qwen3.8-27b", "groq", abordagem) == "groq-" + prefixo + "qwen-qwen3.8-27b"
    assert rv.hash_ferramenta(abordagem) == hash_ferramenta


@pytest.mark.parametrize("abordagem", list(ESPERADO))
def test_hash_do_prompt(abordagem):
    if abordagem in V3 and SEM_INDICE:
        pytest.skip("sem dados/indice_folhas.json o hash da v3 é outro (o arquivo entra no texto do hash)")
    assert rv.hash_prompt(abordagem) == ESPERADO[abordagem][1]


def test_padrao_e_nome_desconhecido_caem_na_v1():
    # conferencia.py passa o nome gravado no manifesto; um nome antigo (ex.: tc3f do desenvolvimento) cai na v1
    _, prompt_v1, ferramenta_v1 = ESPERADO["tool_calling"]
    assert rv.hash_prompt() == rv.hash_prompt("tool_calling_v3f") == prompt_v1
    assert rv.hash_ferramenta() == rv.hash_ferramenta("tool_calling_v3f") == ferramenta_v1


def _manifestos_validos():
    for m in sorted((RAIZ / "results").rglob("manifesto.json")):
        partes = m.relative_to(RAIZ / "results").parts
        if any(p.startswith("_") or p.startswith("dev_") for p in partes):
            continue   # rodadas descartadas e ciclos de desenvolvimento (outro código, de propósito)
        yield m


# rodadas da tese que, presentes, têm de estar entre as conferidas (uma por família de resultado)
CHAVE = ["results/qwen3-4b-instruct-2507-q4_K_M", "results/se-gemma4-e4b-it-qat", "results/prototipo-phi4-14b",
         "results/estacao/gemma4-e2b-it-qat", "results/groq-se-qwen-qwen3.8-27b", "results/lote/tc2-gemma4-e4b-it-qat",
         "results/v2_310/se2-gemma4-e4b-it-qat", "results/lote2/tc3-gemma4-e4b-it-qat",
         "results/v3_310/se3-gemma4-e4b-it-qat"]


@pytest.mark.skipif(not (RAIZ / "results").is_dir(), reason="sem results/")
def test_hashes_das_rodadas_gravadas_continuam_reproduzidos():
    conferidas = set()
    for m in _manifestos_validos():
        d = json.loads(m.read_text(encoding="utf-8"))
        abordagem = d.get("abordagem") or "tool_calling"
        pasta = m.parent.relative_to(RAIZ).as_posix()
        assert m.parent.name.startswith(rv.PREFIXO_ABORDAGEM[abordagem] if d.get("provedor") != "groq"
                                        else "groq-" + rv.PREFIXO_ABORDAGEM[abordagem]), pasta
        if d.get("ferramenta_sha256"):
            assert d["ferramenta_sha256"] == rv.hash_ferramenta(abordagem), pasta
        if d.get("prompt_sha256") and not (abordagem in V3 and SEM_INDICE):
            assert d["prompt_sha256"] == rv.hash_prompt(abordagem), pasta
            conferidas.add(pasta)
    if not conferidas:
        pytest.skip("nenhuma rodada com hash de prompt em results/")
    presentes = {p for p in CHAVE if (RAIZ / p / "manifesto.json").exists()
                 and not (SEM_INDICE and ("/tc3" in p or "/se3" in p))}
    assert presentes <= conferidas
