import logging
from uuid import uuid4  

from extract import extract_moovitamix_tracks, extract_moovitamix_users, extract_moovitamix_listen_history
from transform import transform_tracks, transform_users, transform_listen_history
from load import init_database, load_tracks, load_users, load_listen_history, create_db_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def moovitamix_etl():
    run_id = uuid4()
    logging.info(f"Starting Moovitamix ETL process (run_id: {run_id})")
    conn = create_db_connection()
    
    logging.info("Extracting data from Moovitamix API - tracks")
    tracks = extract_moovitamix_tracks()
    data_tracks = transform_tracks(tracks, run_id)
    load_tracks(data_tracks, conn)
    
    logging.info("Extracting data from Moovitamix API - users")
    users = extract_moovitamix_users()
    data_users = transform_users(users, run_id)
    load_users(data_users, conn)
    
    logging.info("Extracting data from Moovitamix API - listen history")
    listen_history = extract_moovitamix_listen_history()
    data_listen_history = transform_listen_history(listen_history, run_id)
    load_listen_history(data_listen_history, conn)
    
    logging.info(f"Moovitamix ETL process completed (run_id: {run_id})")
    
if __name__ == "__main__":
    init_database()
    
    moovitamix_etl()
    