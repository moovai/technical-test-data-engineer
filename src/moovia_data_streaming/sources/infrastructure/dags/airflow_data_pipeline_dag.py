import datetime as dt
from datetime import timezone
import uuid
import logging
import sqlite3
from kafka import KafkaProducer, KafkaConsumer
from json import dumps
import json

from airflow.operators.python  import PythonOperator
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.sqlite.hooks.sqlite import SqliteHook


from utils import set_full_package_path
set_full_package_path('/src/moovia_data_streaming/sources/api')
set_full_package_path('/src/moovia_data_streaming/sources/kafka_streaming')

from data_fetcher import ApiDataFetcher
from kafka_stream_producer import KafkaStreamProducer
from kafka_stream_consumer import KafkaStreamConsumer

API_BaseAddress = 'http://host.docker.internal:8000'

DAG_ID = "users_tracks_history_pipeline"

def stream_data_produce(**kwargs): 
  path = kwargs['path']      
  topic_name = kwargs['topic_name']  
  logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')    
  fetch = ApiDataFetcher(logging, 10)
  fetch.set_endpoint(f'{API_BaseAddress}/{path}')  

  producer = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda x:dumps(x).encode('utf-8'))
  prod = KafkaStreamProducer(fetch, producer, logging)  
  prod.set_topic_name(topic_name)
  prod.produce()

def stream_data_consume(topic_name):    
   consumer = KafkaConsumer(bootstrap_servers="kafka:9092", value_deserializer=lambda m: json.loads(m.decode('ascii')), auto_offset_reset='latest')
   logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p') 

   cons = KafkaStreamConsumer(consumer, logging)   
   cons.set_topic_name(topic_name)
   return cons.consume()

with DAG(
    dag_id=DAG_ID,
    schedule="@daily",
    start_date=dt.datetime(2024, 1, 1),
    tags=["moov_ia"],
    catchup=False,
) as dag:
        
         
    stream_users_data_from_api = PythonOperator(
     task_id='stream_users_data_from_api',
     python_callable=stream_data_produce,
     op_kwargs=  {'path':'users', 'topic_name':'users_topic'},
     dag = dag
   )

    stream_tracks_data_from_api = PythonOperator(
     task_id='stream_tracks_data_from_api',
     python_callable=stream_data_produce,
     op_kwargs=  {'path':'tracks', 'topic_name':'tracks_topic'},
     dag = dag
   )
    
    stream_listen_history_data_from_api = PythonOperator(
     task_id='stream_listen_history_data_from_api',
     python_callable=stream_data_produce,
     op_kwargs=  {'path':'listen_history', 'topic_name':'listen_history_topic'},
     dag = dag
   )  

    def insert_users_sqlite_from_consumer_hook():
       try:
            conn = sqlite3.connect('music_db.db')
            cur = conn.cursor()                                           
            rows = []
            users = stream_data_consume('users_topic') 
            for user in users:                        
                user_to_save = (user["id"], user["first_name"], user["last_name"], user["email"], user["gender"], user["favorite_genres"], user["created_at"], user["updated_at"])                                
                rows.append(user_to_save)
                          
            cur.executemany('INSERT INTO Users("id", "first_name", "last_name", "email", "gender", "favorite_genres", "created_at", "updated_at") VALUES (?,?,?,?,?,?,?,?)', rows)
            conn.commit()

       except Exception as e:   
          message = str(e)
          logging.error(f'An error occurred when consuming data to: kafka:9090 - topic: users_topic: {message}')  

    def insert_tracks_sqlite_from_consumer_hook():  
       try:
            conn = sqlite3.connect('music_db.db')
            cur = conn.cursor()                                           
            rows = []
            tracks = stream_data_consume('tracks_topic') 
            for track in tracks:                        
                track_to_save =  (track["id"], track["name"], track["artist"], track["songwriters"], track["duration"], track["genres"], track["album"], track["created_at"], track["updated_at"])                
                rows.append(track_to_save)
                          
            cur.executemany('INSERT INTO Tracks VALUES (?,?,?,?,?,?,?,?)', rows)
            conn.commit()

       except Exception as e:   
          message = str(e)
          logging.error(f'An error occurred when consuming data to: kafka:9090 - topic: users_topic: {message}')   

    def insert_listen_history_sqlite_from_consumer_hook():    
       try:
            conn = sqlite3.connect('music_db.db')
            cur = conn.cursor()                                           
            rows = []
            listen_histories = stream_data_consume('listen_history_topic') 
            for listen_history in listen_histories:     
                for item in  listen_history["items"]:                         
                    listen_history_to_save =   (str(uuid.uuid4()), listen_history["user_id"], item, listen_history["created_at"], listen_history["updated_at"])
                    rows.append(listen_history_to_save)
                          
            cur.executemany('INSERT INTO listen_history VALUES (?,?,?,?,?,?,?,?)', rows)
            conn.commit()

       except Exception as e:   
          message = str(e)
          logging.error(f'An error occurred when consuming data to: kafka:9090 - topic: users_topic: {message}')          

    insert_users_sqlite_from_consumer_hook_task = PythonOperator(
     task_id='insert_users_sqlite_from_consumer_hook_task',
     python_callable=insert_users_sqlite_from_consumer_hook,     
     dag = dag
   )     

    insert_tracks_sqlite_from_consumer_hook_task = PythonOperator(
     task_id='insert_tracks_sqlite_from_consumer_hook_task',
     python_callable=insert_tracks_sqlite_from_consumer_hook,     
     dag = dag
   )     

    insert_listen_history_sqlite_from_consumer_hook_task = PythonOperator(
     task_id='insert_listen_history_sqlite_from_consumer_hook_task',
     python_callable=insert_listen_history_sqlite_from_consumer_hook,     
     dag = dag
   )       

    (      
         stream_users_data_from_api
        >> stream_tracks_data_from_api
        >> stream_listen_history_data_from_api
        >> insert_users_sqlite_from_consumer_hook_task
        >> insert_tracks_sqlite_from_consumer_hook_task
        >> insert_listen_history_sqlite_from_consumer_hook_task    
    )

    