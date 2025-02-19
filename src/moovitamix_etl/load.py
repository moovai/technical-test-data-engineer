import os
import logging

import psycopg2
from psycopg2.extras import execute_batch
import pandas as pd

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "moovitamix")

def create_db_connection(db_name=DB_NAME):
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error connecting to database: {e}")
        return None
    
def init_database(db_name=DB_NAME):
    logging.info("Initializing database")
    conn = create_db_connection(db_name)
    if conn is None:
        logging.error("Failed to connect to the database.")
        return
    
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            name VARCHAR(255) PRIMARY KEY,
            artist VARCHAR(255) NOT NULL,
            songwriters VARCHAR(255),
            duration VARCHAR(255),
            album VARCHAR(255),
            genres VARCHAR(255),
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            run_id VARCHAR(255)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            email VARCHAR(255) NOT NULL,
            gender VARCHAR(255),
            favorite_genres VARCHAR(255),
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            run_id VARCHAR(255)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listen_history (
            user_id INT,
            items JSONB,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            run_id VARCHAR(255)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Database initialized successfully")

def delete_database(db_name=DB_NAME):
    logging.info("Deleting database")
    conn = create_db_connection(db_name)
    if conn is None:
        logging.error("Failed to connect to the database.")
        return
    
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS listen_history")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS tracks")
    
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Database deleted successfully")

def load_tracks(tracks, conn=None):
    logging.info("Loading tracks")
    if conn is None:
        logging.error("Failed to connect to the database.")
        return
    
    # Ensure 'tracks' is a pandas DataFrame
    if not isinstance(tracks, pd.DataFrame):
        logging.error("Provided tracks is not a DataFrame.")
        return

    # Convert the DataFrame to a list of tuples
    track_data = [tuple(x) for x in tracks[['name', 'artist', 'songwriters', 'duration', 'album', 'genres', 'created_at', 'updated_at', 'run_id']].values]

    cursor = conn.cursor()
    query = """
        INSERT INTO tracks (name, artist, songwriters, duration, album, genres, created_at, updated_at, run_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    
    execute_batch(cursor, query, track_data)
    
    conn.commit()
    cursor.close()

def load_users(users, conn=None):
    logging.info("Loading users")
    if conn is None:
        logging.error("Failed to connect to the database.")
        return
    
    # Ensure 'users' is a pandas DataFrame
    if not isinstance(users, pd.DataFrame):
        logging.error("Provided users is not a DataFrame.")
        return

    # Convert the DataFrame to a list of tuples
    user_data = [tuple(x) for x in users[["id", "first_name", "last_name", "email", "gender", "favorite_genres", "created_at", "updated_at", "run_id"]].values]

    cursor = conn.cursor()
    query = """
        INSERT INTO users (id, first_name, last_name, email, gender, favorite_genres, created_at, updated_at, run_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    
    execute_batch(cursor, query, user_data)
    
    conn.commit()
    cursor.close()
    
def load_listen_history(listen_history, conn=None):
    logging.info("Loading listen history")
    if conn is None:
        logging.error("Failed to connect to the database.")
        return
    
    # Ensure 'listen_history' is a pandas DataFrame
    if not isinstance(listen_history, pd.DataFrame):
        logging.error("Provided listen history is not a DataFrame.")
        return

    # Convert the DataFrame to a list of tuples
    listen_history_data = [tuple(x) for x in listen_history[['user_id', 'items', 'created_at', 'updated_at', 'run_id']].values]

    cursor = conn.cursor()
    query = """
        INSERT INTO listen_history (user_id, items, created_at, updated_at, run_id)
        VALUES (%s, to_jsonb(%s::int[]), %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    
    execute_batch(cursor, query, listen_history_data)
    
    conn.commit()
    cursor.close()
    