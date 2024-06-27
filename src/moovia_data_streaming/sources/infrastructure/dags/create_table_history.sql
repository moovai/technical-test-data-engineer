CREATE TABLE IF NOT EXISTS listen_history(
  id TEXT PRIMARY KEY,
  user_id     TEXT, 
  track_id    TEXT, 
  created_at  TIMESTAMP,
  updated_at  TIMESTAMP,
  FOREIGN KEY(user_id) REFERENCES Users(id),
  FOREIGN KEY(track_id) REFERENCES Tracks(id)
);