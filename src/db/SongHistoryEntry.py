from sqlite3 import Connection, Cursor


class SongHistoryEntry:
    """
    Data for an entry in the listening history.
    """
    timestamp: str
    video_id: str

    def __init__(self, video_id: str, timestamp: str):
        self.video_id = video_id
        self.timestamp = timestamp
         
    @staticmethod  
    def insert(items: list['SongHistoryEntry'], con: Connection):
        con.executemany(
            """
            INSERT INTO song_history_entry (video_id, timestamp)
            VALUES (?, ?)
            ON CONFLICT(timestamp) DO UPDATE SET
                timestamp=excluded.timestamp
            """,
            [(item.video_id, item.timestamp) for item in items]
        )
        
    @staticmethod
    def from_json(data: dict) -> 'SongHistoryEntry':
        timestamp = data.get("time")
        video_id = data.get("titleUrl").split("v=")[-1]
        return SongHistoryEntry(video_id, timestamp)
    
    @staticmethod
    def get_video_ids_to_fetch_metadata_for(cur: Cursor) -> list[str]:
        cur.execute(
            """
            SELECT DISTINCT video_id
            FROM song_history_entry
            WHERE NOT EXISTS (
                SELECT 1
                FROM video
                WHERE video.video_id = song_history_entry.video_id
            ) AND NOT EXISTS (
                SELECT 1
                FROM unavailable_video_id
                WHERE unavailable_video_id.video_id = song_history_entry.video_id
            )
            """
        )
        return [row[0] for row in cur.fetchall()]
        
        