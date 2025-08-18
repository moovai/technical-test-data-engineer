from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from data_ingestion.load_data import incremental_load

default_args = {
    "owner": "data-eng",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="daily_ingest",
    default_args=default_args,
    schedule_interval="30 2 * * *",  # Daily at 2:30 AM
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["data-engineering", "music-data-ingestion"],
) as dag:

    load_tracks = PythonOperator(
        task_id="incremental_load_tracks",
        python_callable=incremental_load,
        op_args=["tracks", "tracks"], # endpoint and table_name
    )
    load_users = PythonOperator(
        task_id="incremental_load_users",
        python_callable=incremental_load,
        op_args=["users", "users"],
    )
    load_listen_history = PythonOperator(
        task_id="incremental_load_listen_history",
        python_callable=incremental_load,
        op_args=["listen_history", "listen_history"],
    )
