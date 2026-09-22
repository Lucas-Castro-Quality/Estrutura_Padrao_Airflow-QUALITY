"""Testes de include/. Rodam sem Docker e sem Airflow instalado — ver README, seção "Convenção de testes".

Funções e dados compartilhados entre módulos de teste também vivem aqui, como qualquer pacote Python comum.
"""
from __future__ import annotations


def dado_de_exemplo(valor: int = 21) -> dict:
    """Constrói um dado de entrada para os testes de include/exemplo.py."""
    return {"valor": valor}
