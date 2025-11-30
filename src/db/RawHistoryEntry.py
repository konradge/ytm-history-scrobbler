class RawHistoryEntry:
    def __init__(self, timestamp: str, video_id: str):
        self.timestamp = timestamp
        self.video_id = video_id

    @staticmethod
    def from_json(data: dict) -> 'RawHistoryEntry':
        timestamp = data.get("time")
        video_id = data.get("titleUrl").split("v=")[-1]
        return RawHistoryEntry(timestamp, video_id)