#SQLite is a serverless, self-contained database 
import sqlite3
import pandas as pd
from transform import tracks_db,users_db,history_db

# Create an in-memory SQLite database
conn = sqlite3.connect(':memory:')  # For testing, in-memory database
cursor = conn.cursor()
# Create tracks table
tracks_df = tracks_db()
if not tracks_df.empty:
    cursor.execute("DROP TABLE IF EXISTS tracks")
    cursor.execute('''
    CREATE TABLE tracks (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        artist TEXT,
        songwriters TEXT,
        duration TEXT,
        genres TEXT,
        album TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    # Insert data into the table
    for _, row in tracks_df.iterrows():
        print(row)
        cursor.execute('''
        INSERT INTO tracks (id, name, artist, songwriters, genres, album, created_at, updated_at, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(row))
    # Commit and query data
    conn.commit()

#user table
users_df = users_db()
if not users_df.empty:
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT UNIQUE,
        gender TEXT,
        favorite_genres TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    # Insert data into the table
    for _, row in users_df.iterrows():
        cursor.execute('''
            INSERT INTO users (id, first_name, last_name, email, gender, favorite_genres, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(row))
    # Commit and query data
    conn.commit()

#listen_history table
history_df = history_db()
cursor.execute("DROP TABLE IF EXISTS listen_history")
cursor.execute('''
CREATE TABLE listen_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item_id INTEGER,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (item_id) REFERENCES tracks(id)
)
''')
# Insert data into the table
for _, row in history_df.iterrows():
    cursor.execute('''
    INSERT INTO listen_history (user_id, item_id, created_at, updated_at)
    VALUES (?, ?, ?, ?)
    ''', tuple(row))
# Commit and query data
conn.commit()
# Close the connection

#tests
'''
print('we are here')
cursor.execute('SELECT count(*) FROM tracks')
rows = cursor.fetchall()
for row in rows:
    print(row)
cursor.execute('SELECT  count(*)  FROM users')
rows = cursor.fetchall()
for row in rows:
    print(row)
cursor.execute('SELECT count(*) FROM listen_history')
rows = cursor.fetchall()
for row in rows:
    print(row)
'''
conn.close()
