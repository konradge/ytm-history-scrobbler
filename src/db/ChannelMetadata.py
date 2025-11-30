from sqlite3 import Cursor

class ChannelMetadata:
    channel_id: str
    name: str
        
    def __init__(self, channel_id: str, name: str):
        self.channel_id = channel_id
        self.name = name
        
    @staticmethod
    def fetch(channel_ids: list[str], cur: Cursor) -> list['ChannelMetadata']:
        cur.executemany("SELECT channel_id, name FROM channel_metadata WHERE channel_id in ?", channel_ids) 
        return [ChannelMetadata(it[0], it[1]) for it in cur.fetchall()]
