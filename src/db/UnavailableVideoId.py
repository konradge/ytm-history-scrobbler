from sqlite3 import Cursor


class UnavailableVideoId:
    def __init__(self, video_id: str):
        self.video_id = video_id
        
    @staticmethod
    def insert(ids: list[str], cur: Cursor):
        cur.executemany(
            "INSERT INTO unavailable_video_id (video_id) VALUES (?)",
            [(vid,) for vid in ids],
        )