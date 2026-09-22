"""Lógica de negócio do fluxo de referência (ver dags/exemplo_dag.py).

Cada função é independente do Airflow — recebe dados simples, devolve dados simples, e pode
ser chamada diretamente em um teste de `tests/`, sem necessidade de iniciar nenhum container.
"""
from __future__ import annotations

import logging
from collections.abc import Mapping

from include.configuracao import resolver

log = logging.getLogger(__name__)

# Prefixo usado nos nomes de Variável/ambiente (ver include/configuracao.py). Trocar pelo
# prefixo do projeto real.
PREFIXO = "exemplo"


def extrair() -> dict:
    """Obtém o dado de origem."""
    dado = {"valor": 21}
    log.info("Extraído: %s", dado)
    return dado


def transformar(dado: dict, params: Mapping[str, object] | None = None) -> dict:
    """Valida/processa o dado extraído."""
    multiplicador, origem = resolver("multiplicador", PREFIXO, padrao="2", params=params)
    resultado = {**dado, "valor": dado["valor"] * int(multiplicador)}
    log.info("Transformado (multiplicador=%s, origem=%s): %s -> %s", multiplicador, origem, dado, resultado)
    return resultado


def carregar(resultado: dict) -> None:
    """Entrega o resultado (grava, insere, notifica)."""
    log.info("Carregado: %s", resultado)
