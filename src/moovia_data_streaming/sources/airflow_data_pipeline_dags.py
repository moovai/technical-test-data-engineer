import datetime 
from datetime import timezone
import uuid


from airflow.operators.python  import PythonOperator
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook

from dotenv import load_dotenv
import os

from utils import set_full_package_path
set_full_package_path('src/moovia_data_streaming/sources/api')
set_full_package_path('src/moovia_data_streaming/sources/kafka_streaming')

from data_fetcher import ApiDataFetcher
from kafka_stream_producer import KafkaStreamProducer
from kafka_stream_consumer import KafkaStreamConsumer


load_dotenv('.env')
API_BaseAddress = os.getenv('API_BaseAddress')
kafka_nodes = os.getenv('kafka_nodes')
kafka_users_topic = os.getenv('kafka_users_topic')
kafka_tracks_topic = os.getenv('kafka_tracks_topic')
kafka_listen_history_topic = os.getenv('kafka_listen_history_topic')

DAG_ID = "users_tracks_history_pipeline"

def stream_data_produce(path, topic_name):     
  fetch = ApiDataFetcher()
  fetch.set_endpoint(f'{API_BaseAddress}/{path}')  

  prod = KafkaStreamProducer(fetch)
  prod.set_kafka_nodes(kafka_nodes)
  prod.set_topic_name(topic_name)
  prod.produce()

def stream_data_consume(topic_name):     
   cons = KafkaStreamConsumer()
   cons.set_kafka_nodes(kafka_nodes)
   cons.set_topic_name(topic_name)
   return cons.consume()

with DAG(
    dag_id=DAG_ID,
    schedule="@daily",
    start_date=datetime(2021, 1, 1),
    tags=["example"],
    catchup=False,
) as dag:
        
    create_tables_from_if_not_exist_sqlite_task = SQLExecuteQueryOperator(
        task_id="create_tables_from_if_not_exist_sqlite_task",
        conn_id="./sqlite/music_db.db",
        sql="./sqlite/create_tables.sql",
    )    

    @dag.task(task_id="insert_users_sqlite_task")
    def insert_users_sqlite_hook():
        sqlite_hook = SqliteHook()        
        rows = []
        users = stream_data_consume(kafka_users_topic) 
        for user in users:                        
            user_to_save = (user["id"], user["first_name"], user["last_name"], user["email"], user["gender"], user["favorite_genres"], user["favorite_genres"], user["created_at"], user["updated_at"])
            rows.push(user_to_save)
            
        target_fields = ["id", "first_name", "last_name", "email", "gender", "favorite_genres", "created_at", "updated_at"]
        sqlite_hook.insert_rows(table="Users", rows=rows, target_fields=target_fields)

    @dag.task(task_id="insert_tracks_sqlite_task")
    def insert_tracks_sqlite_hook():
        sqlite_hook = SqliteHook()        
        rows = []
        tracks = stream_data_consume(kafka_tracks_topic) 
        for track in tracks:                          
            track_to_save = (track["id"], track["name"], track["artist"], track["songwriters"], track["duration"], track["genres"], track["album"], track["created_at"], track["updated_at"])
            rows.push(track_to_save)
            
        target_fields = ["id", "first_name", "last_name", "email", "gender", "favorite_genres", "created_at", "updated_at"]
        sqlite_hook.insert_rows(table="Tracks", rows=rows, target_fields=target_fields) 

    @dag.task(task_id="insert_listen_history_sqlite_task")
    def insert_listen_history_sqlite_hook():
        sqlite_hook = SqliteHook()        
        rows = []
        listen_histories = stream_data_consume(kafka_listen_history_topic) 
        for listen_history in listen_histories:    
          for item in  listen_history["items"]:          
            history_to_save = (str(uuid.uuid4()), listen_history["user_id"], item, listen_history["created_at"], listen_history["updated_at"])
            rows.push(history_to_save)
            
        target_fields = ["id", "user_id", "track_id", "created_at", "updated_at"]
        sqlite_hook.insert_rows(table="listen_history", rows=rows, target_fields=target_fields)           

    streaming_users_task = PythonOperator(
     task_id='stream_users_data_from_api',
     python_callable=stream_data_produce("users", kafka_users_topic),
     dag = dag
   )
    
    streaming_tracks_task = PythonOperator(
     task_id='stream_tracks_data_from_api',
     python_callable=stream_data_produce("tracks", kafka_tracks_topic),
     dag = dag
   ) 
    
    streaming_listen_history_task = PythonOperator(
     task_id='stream_listen_history_data_from_api',
     python_callable=stream_data_produce("listen_history", kafka_listen_history_topic),
     dag = dag
   )     

    (
        create_tables_from_if_not_exist_sqlite_task
        >> streaming_users_task
        >> streaming_tracks_task
        >> streaming_listen_history_task
        >> insert_users_sqlite_hook()
        >> insert_tracks_sqlite_hook()
        >> insert_listen_history_sqlite_hook()
    )
