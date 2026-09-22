"""Testes de include/configuracao.py: cobrem as camadas de resolução, na ordem de precedência."""
from include.configuracao import resolver


def test_parametro_do_disparo_tem_prioridade():
    valor, origem = resolver("x", "exemplo", padrao="0", params={"x": "99"})
    assert valor == "99"
    assert origem == "parâmetro do disparo"


def test_variavel_de_ambiente_e_usada_sem_parametro(monkeypatch):
    monkeypatch.setenv("EXEMPLO_X", "55")
    valor, origem = resolver("x", "exemplo", padrao="0")
    assert valor == "55"
    assert origem == "variável de ambiente (.env)"


def test_usa_padrao_quando_nada_mais_esta_definido():
    valor, origem = resolver("x", "exemplo", padrao="0")
    assert valor == "0"
    assert origem == "padrão do código"


def test_valor_em_branco_e_tratado_como_ausente(monkeypatch):
    monkeypatch.setenv("EXEMPLO_X", "   ")
    valor, origem = resolver("x", "exemplo", padrao="0")
    assert valor == "0"
    assert origem == "padrão do código"
