from sqlite3 import Connection


class SongHistoryEntry:
    title: str
    author: str
    timestamp: str
    listen_time_seconds: int

    def __init__(self, title: str, author: str, timestamp: str, listen_time_seconds: int):
        self.title = title
        self.author = author
        self.timestamp = timestamp
        self.listen_time_seconds = listen_time_seconds
         
    @staticmethod  
    def insert(items: list['SongHistoryEntry'], con: Connection):
        con.executemany(
            """
            INSERT INTO song_history_entry (title, author, timestamp, listen_time_seconds)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(timestamp) DO UPDATE SET
                title=excluded.title,
                author=excluded.author,
                listen_time_seconds=excluded.listen_time_seconds
            """,
            [(item.title, item.author, item.timestamp, item.listen_time_seconds) for item in items]
        )
        