import json
import sqlite3
import sys
from fetch_raw.youtube_api import fetch_metadata, parse_history_json


if len(sys.argv) < 2:
    raise RuntimeError("Please provide path to history file")

with open(sys.argv[1], "r", encoding="utf-8") as f:
    history = json.load(f)

history_entries = [
    parse_history_json(entry) for entry in history if entry.get("header") == "YouTube Music"
]

con = sqlite3.connect("data.db")
cur = con.cursor()

# Insert history entries
cur.executemany(
    "INSERT OR IGNORE INTO raw_history_entry (timestamp, video_id) VALUES (?, ?)",
    history_entries,
)

# Video IDs to fetch metadata for
cur.execute(
    """
    SELECT DISTINCT video_id
    FROM raw_history_entry
    WHERE NOT EXISTS (
        SELECT 1
        FROM video_metadata
        WHERE video_metadata.video_id = raw_history_entry.video_id
    ) AND NOT EXISTS (
        SELECT 1
        FROM unavailable_video_id
        WHERE unavailable_video_id.video_id = raw_history_entry.video_id
    )
    """
)
video_ids_to_fetch: list[str] = [row[0] for row in cur.fetchall()]


for i in range(0, len(video_ids_to_fetch), 50):
    print(
        "Processing songs", i, "to", min(i + 50, len(video_ids_to_fetch)),
        "out of", len(video_ids_to_fetch),
    )
    wanted_ids = set(video_ids_to_fetch[i : i + 50])
    received_metadata = fetch_metadata(wanted_ids)
    received_ids = set(it.id for it in received_metadata)

    cur.executemany(
        """INSERT INTO video_metadata
            (video_id, title, description, duration_seconds, tags, channel_id) 
            VALUES (?, ?, ?, ?, ?, ?)""",
        [
            (it.id, it.title, it.description, it.duration, ", ".join(it.tags), it.channel_id)
            for it in received_metadata
        ],
    )
    cur.executemany(
        """INSERT INTO channel_metadata 
            (channel_id, name) 
            VALUES (?, ?) 
            ON CONFLICT(channel_id) DO NOTHING""",
        [(it.channel_id, it.channel_title) for it in received_metadata],
    )
    cur.executemany(
        "INSERT INTO unavailable_video_id (video_id) VALUES (?)",
        [(vid,) for vid in wanted_ids.difference(received_ids)],
    )

con.commit()
con.close()
