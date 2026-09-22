"""Testes de include/exemplo.py."""
import logging

from include import exemplo

from tests import dado_de_exemplo


def test_extrair_devolve_um_dado():
    assert exemplo.extrair() == {"valor": 21}


def test_transformar_usa_multiplicador_padrao():
    resultado = exemplo.transformar(dado_de_exemplo())
    assert resultado["valor"] == 42


def test_transformar_aceita_override_por_parametro():
    resultado = exemplo.transformar(dado_de_exemplo(), params={"multiplicador": "5"})
    assert resultado["valor"] == 105


def test_carregar_nao_levanta_excecao(caplog):
    # log.info() não aparece no caplog por padrão: o nível padrão de captura é WARNING.
    with caplog.at_level(logging.INFO):
        exemplo.carregar({"valor": 42})
    assert "Carregado" in caplog.text
