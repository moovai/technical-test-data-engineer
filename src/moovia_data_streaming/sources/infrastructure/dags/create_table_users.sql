CREATE TABLE IF NOT EXISTS Users (
  id TEXT PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL,
  gender TEXT NOT NULL,
  favorite_genres TEXT NOT NULL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);