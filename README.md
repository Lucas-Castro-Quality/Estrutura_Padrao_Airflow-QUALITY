# Estrutura Padrão — Projetos Airflow

Modelo de referência para novos projetos de automação em Python + Apache Airflow.

## Pré-requisitos

O Airflow roda em containers Docker — o scheduler exige Linux, então no Windows ele roda
dentro do WSL2, por baixo do Docker Desktop. Recomendação oficial de recursos para o Docker:
4 GB de RAM livre, 2 CPUs, 10 GB de disco.

**Windows**

1. Habilitar o WSL2. Num PowerShell **como Administrador**:
   ```
   wsl --install
   ```
   Reinicie o computador, caso solicitado.

2. Instalar Git e Docker Desktop:
   ```
   winget install --id Git.Git -e --source winget
   winget install --id Docker.DockerDesktop -e --source winget
   ```
   Se o `winget` falhar com um erro de índice de fontes corrompido
   (`0x8a15000f` ou semelhante), execute `winget source reset --force` em uma janela **como
   Administrador** e repita os dois comandos anteriores.

3. Abrir o Docker Desktop uma vez (aceitar os termos) e mantê-lo em execução. A integração
   com o WSL2 é automática.

**Linux**

```
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker "$USER"
```
Reabrir a sessão para que a associação ao grupo `docker` entre em vigor. Instalar o Git pelo
gerenciador de pacotes da distribuição (`apt install git`, `dnf install git`...).

**Mac**

Instalar o Docker Desktop — já inclui o motor Linux, sem precisar de WSL.

## Primeiro uso

```
git clone <url-do-repositório>
cd <pasta-do-projeto>
cp .env.example .env
```

Gerar as 3 chaves obrigatórias (uma execução por chave) e colar cada uma no `.env`:
```
docker run --rm --entrypoint python apache/airflow:3.3.2 -c "import os,base64;print(base64.urlsafe_b64encode(os.urandom(32)).decode())"
```

Iniciar o ambiente:
```
docker compose up -d --build
```

Acessar http://localhost:8080 — usuário e senha vêm do `.env` (`_AIRFLOW_WWW_USER_USERNAME`/
`_AIRFLOW_WWW_USER_PASSWORD`), padrão `airflow`/`airflow`. Os demais valores do `.env` já têm
um padrão (ver `.env.example` e "Categorias de configuração", abaixo).

## Mapa de pastas

| Pasta | Para que serve |
|---|---|
| `dags/` | As DAGs (fluxos) — só orquestração, sem lógica de negócio |
| `include/` | Código de negócio que as DAGs chamam (parsing, validação, integrações) |
| `tests/` | Testes automatizados do código em `include/` |
| `config/` | Pasta padrão do Airflow (config local); normalmente fica vazia no Git |
| `plugins/` | Pasta padrão do Airflow para plugins customizados |
| `logs/` | Onde o Airflow grava logs de execução |

## Categorias de configuração

Todo valor usado no `docker-compose.yaml` se encaixa em uma destas três categorias, reconhecíveis pela sintaxe:

| Categoria | Como aparece | Quando muda | Onde vive |
|---|---|---|---|
| Fixo | valor direto, sem `${}` | nunca | no próprio arquivo, versionado |
| Por projeto | valor direto, sem `${}` | uma vez, ao adaptar este modelo para um projeto real | no próprio arquivo, versionado (`name:`, `image:`) |
| Por ambiente | `${VAR:-padrao}` (opcional) ou `${VAR:?mensagem}` (obrigatória) | em cada máquina (dev, QA, produção) | arquivo `.env` daquela máquina, nunca versionado |

Uma variável `${VAR:?mensagem}` faz o `docker compose up` recusar iniciar se ela não estiver definida.

Serviços internos (Postgres, Redis) não são expostos fora da rede do Docker, então suas credenciais e strings de conexão são fixas.

## Convenção de DAGs

Exemplo completo em [`dags/exemplo_dag.py`](dags/exemplo_dag.py).

- Nome do arquivo e `dag_id` iguais, em `snake_case`, descrevendo o fluxo.
- A DAG só orquestra: declara tarefas e a ordem entre elas. Qualquer lógica não trivial vai
  para `include/`.
- `schedule=None` até o fluxo estar validado de ponta a ponta; ligar o agendamento é uma
  decisão explícita, feita depois.
- `catchup=False`: sem disparos retroativos por padrão.
- `max_active_runs=1`: evita duas execuções do mesmo fluxo disputando o mesmo recurso externo
  ao mesmo tempo (arquivo, sessão de login, limite de uma API).
- `default_args`: `owner` identifica a equipe/projeto responsável; `retries` e `retry_delay`
  absorvem falhas transitórias (timeout, portal instável), comuns em automações que dependem
  de sistemas externos.
- `doc_md=__doc__`: o docstring do módulo descreve o fluxo e aparece na própria tela do
  Airflow, não só no código.

## Convenção de `include/`

Exemplo completo em [`include/exemplo.py`](include/exemplo.py), usado por
[`dags/exemplo_dag.py`](dags/exemplo_dag.py).

- Cada função recebe e devolve dados simples (dict, str...), sem `@task` nem outro import do
  `airflow.sdk` além do estritamente necessário — assim ela roda (e é testável) fora do
  Airflow, sem iniciar nenhum container.
- Logging por módulo (`log = logging.getLogger(__name__)`), nunca `print()`.
- [`include/configuracao.py`](include/configuracao.py) implementa o mecanismo de resolução
  de configuração descrito na convenção de DAGs (parâmetro > Variável > `.env` > padrão) uma
  única vez; cada módulo de negócio reaproveita a função `resolver()`, com seu próprio
  prefixo e suas próprias chaves.
- A DAG importa o módulo pelo namespace (`from include import exemplo`), não funções soltas —
  fica explícito, lendo a DAG, de qual arquivo vem cada chamada.

## Convenção de testes

Exemplo completo em [`tests/test_configuracao.py`](tests/test_configuracao.py) e
[`tests/test_exemplo.py`](tests/test_exemplo.py). Rodam sem Docker: são testes de
`include/`, não da DAG nem do Airflow.

Instalar e executar:
```
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

- `requirements-dev.txt` fica separado de `requirements.txt`: pytest não entra na imagem do
  Airflow (ver `Dockerfile`/`.dockerignore`, que só copiam `requirements.txt`).
- `pytest.ini` define `pythonpath = .`, para os testes importarem `include`/`tests` como
  pacotes normais, sem instalar o projeto.
- `tests/__init__.py` guarda dados e funções compartilhadas entre os arquivos de teste (aqui,
  `dado_de_exemplo()`), como qualquer pacote Python.
- Um arquivo de teste por módulo de `include/` (`test_configuracao.py` testa
  `configuracao.py`, e assim por diante).
- `monkeypatch` (variável de ambiente) e `caplog` (conteúdo do log) são fixtures do próprio
  pytest — não precisam de nenhuma biblioteca extra.

## `.gitignore`

- `.env`, `config/airflow.cfg`, `config/webserver_config.py`: segredos e configuração gerada
  automaticamente pelo Airflow — nunca são versionados (ver "Categorias de configuração",
  acima).
- `logs/*`, com exceção de `logs/.gitkeep`: a pasta existe no Git vazia; o que o Airflow grava
  nela a cada execução, não.
- `__pycache__/`, `*.py[cod]`: bytecode compilado pelo Python (`.pyc`/`.pyo`/`.pyd`) — nunca o
  código-fonte (`.py`). É gerado de novo sempre que o Python importa um módulo.
- `.venv/`, `.pytest_cache/`: artefatos gerados pela execução local dos testes (ver
  "Convenção de testes", acima).
- `.vscode/`, `.idea/`, `Thumbs.db`, `.DS_Store`: preferências de editor e arquivos do sistema
  operacional, específicos de cada máquina.