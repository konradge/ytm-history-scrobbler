from datetime import datetime
import sqlite3

from db.HistoryEntry import SongHistoryEntry
from fetch_raw.title_author_builder import TitleAuthorBuilder



con = sqlite3.connect("data.db")
cur = con.cursor()
cur.execute("""
SELECT timestamp, vm.title, cm.name, vm.duration_seconds
    FROM raw_history_entry rhe
    LEFT JOIN video_metadata vm ON rhe.video_id = vm.video_id
    LEFT JOIN channel_metadata cm ON vm.channel_id = cm.channel_id
    ORDER BY timestamp ASC
""")

title_author_builder = TitleAuthorBuilder()

rows = cur.fetchall()

entries: list[SongHistoryEntry] = []
for index, row in enumerate(rows):
    timestamp: str = row[0]
    title = row[1] if row[1] is not None else ""
    author_name = row[2] if row[2] is not None else ""
    duration_seconds = row[3] if row[3] is not None else 0
    title, author_name = title_author_builder.build_title_author(title, author_name)
    next_timestamp = datetime.fromisoformat(rows[index + 1][0]) if index + 1 < len(rows) else None
    listen_time_seconds = 0
    if next_timestamp is None:
        listen_time_seconds = 0
    else:
        listen_time_seconds = min(
            round((next_timestamp - datetime.fromisoformat(timestamp)).total_seconds()),
            duration_seconds
        )
    
    entry = SongHistoryEntry(title, author_name, timestamp, listen_time_seconds)
    entries.append(entry)
    
SongHistoryEntry.insert(entries, con)
con.commit()