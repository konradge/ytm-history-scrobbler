from typing import Optional
from sqlite3 import Cursor

from ChannelMetadata import ChannelMetadata



class VideoMetadata:
    video_id: str
    title: str
    description: str
    duration_seconds: int
    tags: str
    channel_id: str
    channel: Optional[ChannelMetadata]

    def __init__(self, video_id: str, title: str, description: str, duration_seconds: int, tags: str, channel_id: str, channel: Optional[ChannelMetadata]):
        self.video_id = video_id
        self.title = title
        self.description = description
        self.duration_seconds = duration_seconds
        self.tags = tags
        self.channel_id = channel_id
        self.channel = channel
        
    @staticmethod
    def fetch(video_ids: list[str], cur: Cursor) -> list['VideoMetadata']:
        query = """
            SELECT vm.video_id, vm.title, vm.description, vm.duration_seconds, vm.tags, vm.channel_id, cm.name
            FROM video_metadata vm
            LEFT JOIN channel_metadata cm ON vm.channel_id = cm.channel_id
            WHERE vm.video_id IN (?)
        """
        cur.executemany(query, video_ids)
        return [VideoMetadata(
                video_id=row[0],
                title=row[1],
                description=row[2],
                duration_seconds=row[3],
                tags=row[4],
                channel_id=row[5],
                channel=ChannelMetadata(row[5], row[6]) \
                    if row[5] is not None and row[6] is not None else None
            ) for row in cur.fetchall()]
