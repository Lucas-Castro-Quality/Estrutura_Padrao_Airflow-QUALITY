# Imagem base do Airflow + dependências do projeto (requirements.txt).
FROM apache/airflow:3.3.2

COPY requirements.txt /requirements.txt
# AIRFLOW_VERSION já vem definida pela imagem base, com o mesmo valor da tag acima.
# Fixá-la aqui evita que a instalação de dependências extras troque a versão do Airflow.
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
