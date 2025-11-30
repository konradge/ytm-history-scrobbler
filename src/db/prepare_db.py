import sqlite3

con = sqlite3.connect("data.db")
cur = con.cursor()

# Raw data
cur.execute("""CREATE TABLE IF NOT EXISTS raw_history_entry(
            timestamp DATETIME NOT NULL PRIMARY KEY,
            video_id TEXT NOT NULL,
            FOREIGN KEY(video_id) REFERENCES video_metadata(video_id)
            )""")
cur.execute("""CREATE TABLE IF NOT EXISTS unavailable_video_id(
            video_id TEXT PRIMARY KEY NOT NULL
            )""")
cur.execute("""CREATE TABLE IF NOT EXISTS video_metadata(
            video_id TEXT PRIMARY KEY NOT NULL, 
            title TEXT NOT NULL,
            description TEXT,
            duration_seconds INTEGER NOT NULL,
            tags TEXT,
            channel_id TEXT NOT NULL,
            FOREIGN KEY(channel_id) REFERENCES channel_metadata(channel_id)
            )""")
cur.execute("""CREATE TABLE IF NOT EXISTS channel_metadata(
            channel_id TEXT PRIMARY KEY NOT NULL, 
            name TEXT NOT NULL
            )""")
cur.execute("""CREATE TABLE IF NOT EXISTS song_history_entry(
            title TEXT NOT NULL, -- parsed title of the song
            author TEXT NOT NULL, -- parsed author of the song
            timestamp DATETIME NOT NULL PRIMARY KEY,
            listen_time_seconds INTEGER NOT NULL,
            FOREIGN KEY(timestamp) REFERENCES raw_history_entry(timestamp)
            )""")