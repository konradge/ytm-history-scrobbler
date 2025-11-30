import sqlite3

def prepare_db(cur: sqlite3.Cursor):
    cur.execute("""CREATE TABLE IF NOT EXISTS song_history_entry(
                timestamp DATETIME NOT NULL PRIMARY KEY,
                video_id TEXT NOT NULL,
                FOREIGN KEY(video_id) REFERENCES video(video_id)
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS unavailable_video_id(
                video_id TEXT PRIMARY KEY NOT NULL
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS video(
                video_id TEXT PRIMARY KEY NOT NULL, 
                title TEXT NOT NULL,
                description TEXT,
                duration_seconds INTEGER NOT NULL,
                tags TEXT,
                channel_id TEXT NOT NULL,
                FOREIGN KEY(channel_id) REFERENCES channel(channel_id)
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS channel(
                channel_id TEXT PRIMARY KEY NOT NULL, 
                name TEXT NOT NULL
                )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS song_metadata(
                song_id TEXT PRIMARY KEY NOT NULL,
                title TEXT NOT NULL, -- parsed title of the song
                author TEXT NOT NULL, -- parsed author of the song
                safe BOOLEAN NOT NULL -- indicates if the song metadata is safe to use (no conflicts detected)
                )""")
    cur.execute("""
    CREATE VIEW IF NOT EXISTS listen_times AS
    WITH history_with_gap AS (
        SELECT 
            e.video_id AS song_id, 
            v.duration_seconds AS song_length_seconds, 
            e.timestamp, 
            LEAD(e.timestamp) OVER (ORDER BY e.timestamp ASC) as next_timestamp 
        FROM song_history_entry e 
        JOIN video as v ON v.video_id = e.video_id
    )
    SELECT
        timestamp,
        CASE
            -- 1. Handle the last song
            WHEN next_timestamp IS NULL THEN song_length_seconds

            -- 2. Calculate difference
            WHEN (strftime('%s', next_timestamp) - strftime('%s', timestamp)) < song_length_seconds
                THEN (strftime('%s', next_timestamp) - strftime('%s', timestamp))

            -- 3. Cap at song length
            ELSE song_length_seconds
        END AS listened_seconds
    FROM history_with_gap
    """)
    cur.execute("""
    DROP VIEW IF EXISTS history;
    """)
    cur.execute("""
    CREATE VIEW history AS
    SELECT 
    strftime("%d.%m.%Y %H:%M:%S", e.timestamp) AS timestamp,
    strftime("%m/%Y", e.timestamp) as month, 
    e.video_id, COALESCE(NULLIF(m.title, ""), v.title) AS title,
    COALESCE(NULLIF(m.author, ""), c.name) AS author,
    l.listened_seconds
    FROM song_history_entry e 
    LEFT JOIN song_metadata m ON e.video_id = m.song_id 
    LEFT JOIN video v ON v.video_id = e.video_id
    LEFT JOIN channel c ON c.channel_id = v.channel_id
    JOIN listen_times l ON e.timestamp = l.timestamp ORDER BY safe;
    """)
