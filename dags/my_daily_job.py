from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="run_etl_docker",
    start_date=datetime(2025, 8, 3),
    schedule_interval="0 4 * * *",  # Runs every day at 04:00
    catchup=False,
    tags=["etl"],
) as dag:

    run_etl = BashOperator(
        task_id="run_etl_job",
        bash_command="docker exec etl_job python etl/load.py"
    )