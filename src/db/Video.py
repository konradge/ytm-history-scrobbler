from typing import Optional
from sqlite3 import Cursor

from db.Channel import Channel
from utils.youtube_api import YoutubeApiMusicMetadata


class Video:
    """
    Data for a Youtube video.
    """
    video_id: str
    title: str
    description: str
    duration_seconds: int
    tags: str
    channel_id: str
    channel: Optional[Channel]

    def __init__(self, video_id: str, title: str, description: str, duration_seconds: int, tags: str, channel_id: str, channel: Optional[Channel]):
        self.video_id = video_id
        self.title = title
        self.description = description
        self.duration_seconds = duration_seconds
        self.tags = tags
        self.channel_id = channel_id
        self.channel = channel
        
    @staticmethod
    def fetch(video_ids: list[str], cur: Cursor) -> list['Video']:
        query = """
            SELECT v.video_id, v.title, v.description, v.duration_seconds, v.tags, v.channel_id, c.name
            FROM video v
            LEFT JOIN channel_metadata c ON v.channel_id = c.channel_id
            WHERE v.video_id IN (?)
        """
        cur.executemany(query, video_ids)
        return [Video(
                video_id=row[0],
                title=row[1],
                description=row[2],
                duration_seconds=row[3],
                tags=row[4],
                channel_id=row[5],
                channel=Channel(row[5], row[6]) \
                    if row[5] is not None and row[6] is not None else None
            ) for row in cur.fetchall()]
        
    @staticmethod
    def insert(metadata: list[YoutubeApiMusicMetadata], cur: Cursor):
        cur.executemany(
        """INSERT INTO video
            (video_id, title, description, duration_seconds, tags, channel_id) 
            VALUES (?, ?, ?, ?, ?, ?)""",
        [
            (it.id, it.title, it.description, it.duration, ", ".join(it.tags), it.channel_id)
            for it in metadata
        ],
    )
