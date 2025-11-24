from __future__ import annotations
import pendulum
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

# 1. Parâmetros e Argumentos Padrão (Opcional, mas recomendado)
# Define o proprietário, número de retentativas, etc.
default_args = {
    "owner": "airflow_admin",
    "retries": 1,
}

# 2. Definição do Objeto DAG
with DAG(
    dag_id="etl_simples",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 0 * * *", # Agendamento diário à meia-noite (cron syntax)
    catchup=False,
    default_args=default_args,
    tags=["etl", "primeiro_teste"],
) as dag:
    # 3. Definição das Tarefas (Tasks)
    
    iniciar_processamento = BashOperator(
        task_id="iniciar_processamento",
        bash_command='echo "Iniciando o fluxo ETL..."',
    )
    
    finalizar_processamento = BashOperator(
        task_id="finalizar_processamento",
        bash_command='echo "Fluxo concluído."',
    )

    # 4. Definição da Ordem (Linhagem)
    # Define a ordem de execução das tarefas
    iniciar_processamento >> finalizar_processamento