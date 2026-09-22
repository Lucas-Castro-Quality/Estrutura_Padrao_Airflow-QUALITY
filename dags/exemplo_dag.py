"""
### exemplo_dag

Fluxo de referência: extrai um dado de origem, transforma e entrega o resultado. A lógica de
cada etapa está em `include/exemplo.py` — esta DAG só declara as tarefas e a ordem entre elas.
O objetivo não é automatizar nada de útil, e sim mostrar a forma que toda DAG deste padrão
segue, independente do que ela automatiza de verdade (planilha, portal web, SAP, AD, API,
PDF, OCR...).

1. **extrair**: obtém o dado de origem.
2. **transformar**: valida/processa o que foi extraído. O multiplicador usado vem de
   `include/configuracao.py` (parâmetro do disparo > Variável do Airflow > `.env` > padrão).
3. **carregar**: entrega o resultado (grava, insere, notifica).
"""
from __future__ import annotations

from datetime import timedelta

import pendulum
from airflow.sdk import DAG, Param, get_current_context, task

from include import exemplo

PARAMS = {
    "multiplicador": Param(
        "", type="string", title="Multiplicador",
        description="Sobrescreve o valor usado nesta execução. Vazio = usar a configuração.",
    ),
}

with DAG(
    dag_id="exemplo_dag",
    description="Fluxo de referência: extrair -> transformar -> carregar",
    doc_md=__doc__,
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    params=PARAMS,
    default_args={
        "owner": "automacoes",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["exemplo"],
):

    @task
    def extrair() -> dict:
        return exemplo.extrair()

    @task
    def transformar(dado: dict) -> dict:
        contexto = get_current_context()
        return exemplo.transformar(dado, params=contexto["params"])

    @task
    def carregar(resultado: dict) -> None:
        exemplo.carregar(resultado)

    carregar(transformar(extrair()))
