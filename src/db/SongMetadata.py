from sqlite3 import Cursor


class SongMetadata:
    song_id: str
    title: str
    author: str
    safe: bool
    
    def __init__(self, song_id: str, title: str, author: str, safe: bool):
        self.song_id = song_id
        self.title = title
        self.author = author
        self.safe = safe
    
    @staticmethod
    def insert(songs: list['SongMetadata'], cur: Cursor):
        cur.executemany(
            """INSERT INTO song_metadata
                (song_id, title, author, safe) 
                VALUES (?, ?, ?, ?) ON CONFLICT(song_id) DO UPDATE SET
                    title=excluded.title,
                    author=excluded.author,
                    safe=excluded.safe
            """,
            [
                (
                    it.song_id,
                    it.title,
                    it.author,
                    it.safe,
                )
                for it in songs
            ],
        )
        
class RawSongMetadata:
    song_id: str
    song_title: str
    channel_name: str
    
    def __init__(self, song_id: str, song_title: str, channel_name: str):
        self.song_id = song_id
        self.song_title = song_title
        self.channel_name = channel_name
    
    @staticmethod
    def fetch(cur: Cursor) -> list['RawSongMetadata']:
        cur.execute("""
            SELECT video.video_id, video.title, channel.name
            FROM video
            LEFT JOIN channel ON video.channel_id = channel.channel_id
        """)
        return [RawSongMetadata(
                song_id=row[0],
                song_title=row[1],
                channel_name=row[2],
            ) for row in cur.fetchall()]