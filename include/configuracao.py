"""Resolve valores de configuração, do mais específico para o mais genérico:

1. Parâmetro do disparo (tela "Acionar Dag") — vale só para aquela execução.
2. Variável do Airflow (Admin > Variáveis) — vale a partir da próxima execução, sem reiniciar nada.
3. Variável de ambiente (arquivo .env) — padrão da máquina; mudar exige `docker compose up -d`.
4. Valor padrão, definido no código.

A primeira origem com valor não vazio vence. Os nomes seguem um padrão fixo: para uma
configuração `nome` com prefixo `projeto`, o parâmetro é `nome`, a Variável é
`projeto_nome` e a variável de ambiente é `PROJETO_NOME`.

Funciona fora do Airflow — por exemplo, durante a execução dos testes de `tests/`, sem
iniciar nenhum container: sem `airflow.sdk` instalado, a camada de Variável é ignorada e a
resolução segue para as próximas origens.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Mapping


def _variavel_airflow(chave: str) -> str | None:
    try:
        from airflow.sdk import Variable
    except ImportError:
        return None
    return Variable.get(chave, default=None)


def resolver(
    nome: str,
    prefixo: str,
    padrao: str,
    params: Mapping[str, object] | None = None,
) -> tuple[str, str]:
    """Devolve (valor, origem) de `nome`, seguindo a ordem de precedência acima."""
    origens: list[tuple[str, Callable[[], object]]] = [
        ("parâmetro do disparo", lambda: (params or {}).get(nome)),
        ("variável do Airflow", lambda: _variavel_airflow(f"{prefixo}_{nome}")),
        ("variável de ambiente (.env)", lambda: os.environ.get(f"{prefixo.upper()}_{nome.upper()}")),
    ]
    for origem, obter in origens:
        valor = obter()
        if valor is not None and str(valor).strip():
            return str(valor).strip(), origem
    return padrao, "padrão do código"
