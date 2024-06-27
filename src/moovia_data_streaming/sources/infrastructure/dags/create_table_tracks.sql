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
);