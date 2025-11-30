import json
import os
import re

import requests
from dotenv import load_dotenv


API_URL = "https://www.googleapis.com/youtube/v3"
load_dotenv()
YOUR_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUR_API_KEY:
    raise RuntimeError("YOUTUBE_API_KEY not set in .env")

class YoutubeApiMusicMetadata:
    id: str
    title: str
    description: str
    tags: list[str]
    duration: int
    channel_id: str
    channel_title: str

def fetch_metadata(ids: set[str]) -> list[YoutubeApiMusicMetadata]:
    """Queries the YouTube Data API for video durations."""
    result: list[YoutubeApiMusicMetadata] = []
    print("Querying for", len(ids), "videos")
    params = {
        "part": "contentDetails,snippet",
        "id": ",".join(ids),
        "key": YOUR_API_KEY,
    }
    response = requests.get(API_URL + "/videos", params=params, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            for item in data["items"]:
                metadata = __parse_result(item)
                result.append(metadata)
    return result

def parse_history_json(data: json) -> tuple[str, str]:
    """Parses a history entry from the data exported by Google Takeout."""
    timestamp = data.get("time")
    video_id = data.get("titleUrl").split("v=")[-1]
    return timestamp, video_id

def __parse_result(data: json):
    metadata = YoutubeApiMusicMetadata()
    metadata.id = data['id']
    metadata.title = data['snippet']['title']
    metadata.description = data['snippet']['description']
    metadata.tags = data['snippet'].get('tags', [])
    metadata.duration = __to_seconds(data['contentDetails']['duration'])
    metadata.channel_id = data['snippet']['channelId']
    metadata.channel_title = data['snippet']['channelTitle']
    return metadata

def __to_seconds(iso_duration: str) -> int:
    """Converts ISO 8601 duration format to total seconds."""
    pattern = re.compile(
        r'PT'              # starts with 'PT'
        r'(?:(\d+)H)?'    # hours
        r'(?:(\d+)M)?'    # minutes
        r'(?:(\d+)S)?'    # seconds
    )
    match = pattern.match(iso_duration)
    if not match:
        return 0
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds
