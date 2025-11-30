from sqlite3 import Cursor

from utils.youtube_api import YoutubeApiMusicMetadata


class Channel:
    """
    Data for Youtube channel.
    """
    channel_id: str
    name: str
        
    def __init__(self, channel_id: str, name: str):
        self.channel_id = channel_id
        self.name = name
        
    @staticmethod
    def fetch(channel_ids: list[str], cur: Cursor) -> list['Channel']:
        cur.executemany("SELECT channel_id, name FROM channel WHERE channel_id in ?", channel_ids) 
        return [Channel(it[0], it[1]) for it in cur.fetchall()]

    @staticmethod
    def insert(metadata: list[YoutubeApiMusicMetadata], cur: Cursor):
        cur.executemany(
            """INSERT INTO channel
                (channel_id, name) 
                VALUES (?, ?) 
                ON CONFLICT(channel_id) DO NOTHING""",
            [(it.channel_id, it.channel_title) for it in metadata],
        )