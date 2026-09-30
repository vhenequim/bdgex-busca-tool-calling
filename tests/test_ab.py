"""Teste A/B (Tool Calling × Saída Estruturada): pares, medidas, macros, tabela e conferência (linhas sintéticas)."""

import json
import re

from pfc_busca.evaluation import ab, lote

GOIAS = {"state": "Goiás"}
T4 = {"provedor": "ollama", "hardware": {"gpu": "Tesla T4, 15360 MiB, 580.82.07", "maquina": "a"},
      "software": {"ollama_servidor": "0.34.4"}, "sessoes": [{"ollama_ps": {"fracao_na_gpu": 1.0}}]}


def _linha(i: str, predito, rep: int = 1, fora: bool = False, lat: float = 100.0) -> dict:
    return {"id": i, "origem": "G", "familia": "VS", "categorias": ["F"] if fora else ["S"], "consulta": f"consulta {i}",
            "observacional": False, "espera_tool_call": not fora, "aceita_nao_chamar": False, "repeticao": rep,
            "hoje": "2026-09-24", "esperado": {} if fora else GOIAS, "esperado_resolvido": {} if fora else GOIAS,
            "alternativas_resolvidas": [], "predito": predito, "chamou_ferramenta": predito is not None,
            "texto_resposta": None, "latencia_llm_ms": lat, "erro": None, "classe_erro": None}


def _rodadas() -> tuple[list[dict], list[dict]]:
    """TC com três repetições (D1..D6, F1, F2) e SE com uma, sem D6 (rodada incompleta).

    TC: D1 certa em 2 de 3 (maioria certa, média 2/3); D2 não busca (falsa recusa); D4 busca a UF errada;
    D6 sempre errada; F1 e F2 recusadas. SE: D1..D5 certas; F1 e F2 buscadas (erradas)."""
    tc = []
    for rep in (1, 2, 3):
        tc += [_linha("D1", GOIAS if rep < 3 else {"state": "Bahia"}, rep), _linha("D2", None, rep),
               _linha("D3", GOIAS, rep), _linha("D4", {"state": "Bahia"}, rep), _linha("D5", GOIAS, rep),
               _linha("D6", {"state": "Bahia"}, rep), _linha("F1", None, rep, fora=True),
               _linha("F2", None, rep, fora=True)]
    se = [_linha(i, GOIAS, lat=50.0) for i in ("D1", "D2", "D3", "D4", "D5")]
    se += [_linha(i, {}, fora=True, lat=50.0) for i in ("F1", "F2")]
    return tc, se


def _par(refs=()) -> ab.Par:
    return ab.Par("base", "t4", ab.E4B, "v1", ab.DIR_RESULTADOS / "x", ab.DIR_RESULTADOS / "y", refs=tuple(refs))


def _medir(refs=(), man_se=None) -> dict:
    tc, se = _rodadas()
    return ab.medir_par(_par(refs), {"pasta": ab.DIR_RESULTADOS / "x", "linhas": tc, "casos": {}, "manifesto": T4},
                        {"pasta": ab.DIR_RESULTADOS / "y", "linhas": se, "casos": {}, "manifesto": man_se or T4})


def test_pares_declarados(tmp_path):
    ps = ab.pares(tmp_path)
    chaves = [p.chave for p in ps]
    assert len(chaves) == len(set(chaves)) == 16
    assert all(re.fullmatch(r"[A-Za-z0-9]+", k) for k in chaves)
    por_chave = {p.chave: p for p in ps}
    v3 = por_chave["lote2e4bv3"]
    assert (v3.tc.relative_to(tmp_path).as_posix(), v3.se.relative_to(tmp_path).as_posix()) == \
        ("lote2/tc3-gemma4-e4b-it-qat", "lote2/se3-gemma4-e4b-it-qat")
    assert por_chave["basegroqgptoss20v1"].se.name == "groq-se-openai-gpt-oss-20b"
    assert por_chave["baseestacaoe2bv1"].tc.relative_to(tmp_path).as_posix() == "estacao/gemma4-e2b-it-qat"
    assert {p.chave for p in ps if p.desenvolvimento} == {"basee4bv2", "basee4bv3"}


def test_hardware_comparavel():
    ok, desc, mesma = ab.hardware_comparavel(T4, T4)
    assert ok and mesma and "Ollama 0.34.4" in desc and "100% na GPU" in desc
    ok, _, mesma = ab.hardware_comparavel(T4, {**T4, "hardware": {**T4["hardware"], "maquina": "b"}})
    assert ok and not mesma                                      # outra sessão, mesma GPU: comparável
    assert not ab.hardware_comparavel(T4, {"provedor": "groq", "hardware": {"gpu": None}})[0]
    assert not ab.hardware_comparavel(T4, {**T4, "sessoes": [{"ollama_ps": {"fracao_na_gpu": 0.66}}]})[0]
    assert not ab.hardware_comparavel(T4, {**T4, "software": {"ollama_servidor": "0.34.0"}})[0]


def test_medir_par_maioria_consultas_comuns_e_latencia():
    r = _medir()
    assert (r["n"], r["ntc"], r["nse"], r["incompleto"]) == (7, 8, 7, True)
    tc, se, c = r["tc"], r["se"], r["cmp"]
    assert abs(tc["acuracia"] - 5 / 7) < 1e-9                    # maioria: D1, D3, D5, F1, F2
    assert abs(r["tc_exec"]["acuracia"] - 14 / 21) < 1e-9        # média das execuções (critério da comparacao)
    assert abs(se["acuracia"] - 5 / 7) < 1e-9 and abs(tc["accdominio"] - 3 / 5) < 1e-9
    assert (c["so_a"], c["so_b"], c["p"]) == (2, 2, 1.0) and ab.veredito(r) == "empate"
    assert abs(tc["recusa"]["f1"] - 0.8) < 1e-9 and se["recusa"]["f1"] == 0.0   # tp 2, fp 1 (D2), fn 0
    assert tc["repeticoes"] == [1, 2, 3] and tc["chamadas"] == 1.0
    assert r["latencia_comparavel"] and (tc["latmed"], se["latmed"]) == (100.0, 50.0)
    assert r["tc_completo"]["n"] == 8
    sem = _medir(man_se={"provedor": "groq"})
    assert not sem["latencia_comparavel"]


def test_macros_e_tabela():
    r = _medir()
    tex = ab.macros([r])
    nomes = re.findall(r"\\csname res@ab@([^@]+)@([^\\]+)\\endcsname", tex)
    assert nomes and all(re.fullmatch(r"[A-Za-z0-9]+", x) for par in nomes for x in par)
    valores = ab.ler_macros(tex)
    assert valores["res@ab@basee4bv1@acctc"] == r"71,4\%" and valores["res@ab@basee4bv1@dif"] == "0,0"
    assert valores["res@ab@basee4bv1@latmedtc"] == "0,10" and valores["res@ab@basee4bv1@razaolat"] == "2,00"
    assert valores["res@ab@basee4bv1@reptc"] == "3" and valores["res@ab@basee4bv1@n"] == "7"
    assert valores["res@ab@geral@nempate"] == "1" and valores["res@ab@geral@nparessemdesenv"] == "1"
    semlat = ab.ler_macros(ab.macros([_medir(man_se={"provedor": "groq"})]))
    assert semlat["res@ab@basee4bv1@latmedse"] == "---" and semlat["res@ab@basee4bv1@razaolat"] == "---"
    tabela = ab.tabela([r])
    assert r"\label{tab:ab}" in tabela and r"7$^{*}$" in tabela and r"rodada de Saída Estruturada incompleta" in tabela
    assert r"\shortstack[l]{" in tabela and "0,10 / 0,05" in tabela and "três repetições" in tabela


def test_conferencia_igual_explicada_divergente_e_sem_referencia():
    r = _medir(refs=[ab.Ref("comparacao", "abordagens", chave="e4b")])
    existentes = {"res@abordagens@e4b@acuraciatc": r"66,7\%",     # média das execuções: explicada
                  "res@abordagens@e4b@acuraciase": r"71,4\%",     # igual
                  "res@abordagens@e4b@n": "8",                    # todas as consultas da rodada TC: explicada
                  "res@abordagens@e4b@sotc": "3"}                 # sem explicação
    conf = {x["macro"]: x for x in ab.conferir([r], existentes)}
    assert conf["res@abordagens@e4b@acuraciase"]["situacao"] == "igual"
    assert conf["res@abordagens@e4b@acuraciatc"]["situacao"] == "explicada"
    assert "média das execuções" in conf["res@abordagens@e4b@acuraciatc"]["causa"]
    assert conf["res@abordagens@e4b@n"]["situacao"] == "explicada" and "todas as consultas" in \
        conf["res@abordagens@e4b@n"]["causa"]
    assert conf["res@abordagens@e4b@sotc"]["situacao"] == "divergente"
    assert conf["res@abordagens@e4b@p"]["situacao"] == "sem_referencia"
    assert conf["res@abordagens@e4b@accsemftc"]["campo"] == "domtc"
    novos = ab.sem_equivalente([r], list(conf.values()))["basee4bv1"]
    assert "acctc" not in novos and "n" not in novos and "recusaftc" in novos and "p" in novos


def test_campo_e_ler_macros():
    assert ab.campo("p95 SE (s)") == "latp95se" and ab.campo("domínio (sem F) TC") == "domtc"
    assert ab.campo("n do par") == "n" and ab.campo("n TC") == "n" and ab.campo("IC SE − TC") == "icdif"
    assert ab.campo("latência TC (ms)") == "latmedtc" and ab.campo("TC − SE") == "dif"
    linha = r"\expandafter\def\csname res@lote2@tc3se3@p\endcsname{$<$\,0,001}"
    assert ab.ler_macros("% comentário\n" + linha) == {"res@lote2@tc3se3@p": r"$<$\,0,001"}


def test_main_ponta_a_ponta_com_carga_simulada(tmp_path, monkeypatch, capsys):
    tc, se = _rodadas()
    par = next(p for p in ab.pares(tmp_path) if p.chave == "basee4bv1")
    for pasta in (par.tc, par.se):
        pasta.mkdir(parents=True)
        (pasta / "execucoes.jsonl").write_text("{}\n", encoding="utf-8")
        (pasta / "manifesto.json").write_text(json.dumps({**T4, "modelo": ab.E4B}), encoding="utf-8")
    monkeypatch.setattr(lote, "carregar_pasta", lambda p, dataset=None: (tc if p == par.tc else se, {}))
    tabelas = tmp_path / "paper" / "tabelas"
    tabelas.mkdir(parents=True)
    (tabelas / "numeros_abordagens.tex").write_text(
        "\\expandafter\\def\\csname res@abordagens@e4b@acuraciase\\endcsname{71,4\\%}\n"
        "\\expandafter\\def\\csname res@abordagens@e4b@sose\\endcsname{9}\n", encoding="utf-8")
    argv = ["--resultados", str(tmp_path), "--saida", str(tmp_path / "ab"), "--paper", str(tmp_path / "paper")]
    assert ab.main(argv) == 0
    saida = capsys.readouterr().out
    assert "A/B: 1 pares" in saida and "sem rodada" in saida and "NÃO EXPLICADA" in saida
    for nome in ("tab_ab.tex", "numeros_ab.tex", "ab.md", "ab.json"):
        assert (tmp_path / "ab" / nome).exists()
    assert (tabelas / "tab_ab.tex").exists() and (tabelas / "numeros_ab.tex").exists()
    md = (tmp_path / "ab" / "ab.md").read_text(encoding="utf-8")
    assert "iguais: 1" in md and "não explicadas: 1" in md and str(tmp_path) not in md
    dados = json.loads((tmp_path / "ab" / "ab.json").read_text(encoding="utf-8"))
    assert dados["pares"][0]["chave"] == "basee4bv1" and dados["pares"][0]["incompleto"] is True
    # a segunda execução não lê o próprio numeros_ab.tex como referência; --estrito falha com a divergência
    assert ab.main(argv + ["--estrito"]) == 1
    assert "iguais: 1" in (tmp_path / "ab" / "ab.md").read_text(encoding="utf-8")


def test_main_sem_rodadas(tmp_path, capsys):
    assert ab.main(["--resultados", str(tmp_path), "--saida", str(tmp_path / "ab")]) == 0
    assert "nenhum par" in capsys.readouterr().out
    assert not (tmp_path / "ab").exists()
