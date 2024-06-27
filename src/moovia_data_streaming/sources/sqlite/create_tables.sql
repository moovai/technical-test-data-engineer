CREATE TABLE IF NOT EXISTS Users (
  id TEXT PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL,
  gender TEXT NOT NULL,
  favorite_genres TEXT NOT NULL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

CREATE TABLE IF NOT EXISTS Tracks (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  artist TEXT NOT NULL,
  songwriters TEXT NOT NULL,
  duration TEXT NOT NULL,
  genres TEXT NOT NULL,
  album TEXT NOT NULL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

CREATE TABLE IF NOT EXISTS listen_history(
  id TEXT PRIMARY KEY,
  user_id     TEXT, 
  track_id    TEXT, 
  created_at  TIMESTAMP,
  updated_at  TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES Users(id),
  FOREIGN KEY(track_id) REFERENCES Tracks(id)
)