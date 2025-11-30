from datetime import datetime
import json
import re
from typing import Optional

from youtube_music_video_metadata import YoutubeMusicVideoMetadata

class HistoryEntry:
    song_id: str
    title: str
    author: str
    timestamp: datetime
    song_duration: int

    def __init__(self, data: json, metadata: Optional[YoutubeMusicVideoMetadata], title_author_builder: 'TitleAuthorBuilder'):
        self.song_id = HistoryEntry.extract_id(data)
        self.title, self.author = title_author_builder.build_title_author(data, metadata)
        self.timestamp = datetime.fromisoformat(data.get("time"))
        self.song_duration = 0 if metadata is None else metadata.duration

    @staticmethod
    def extract_id(data: json) -> str:
        return data.get("titleUrl").split("v=")[-1]
    
    @staticmethod
    def is_ytm_json(data: json) -> bool:
        return data.get("header") == "YouTube Music" and HistoryEntry.is_public_video(data)
    
    @staticmethod
    def is_public_video(data: json) -> bool:
        return data.get("subtitles") is not None
    
    @staticmethod
    def build_dict_for_csv(history_entry: 'HistoryEntry', next_entry: Optional['HistoryEntry']) -> dict:
        video_length_seconds = history_entry.song_duration
        if video_length_seconds is None:
            video_length_seconds = 0

        watchtime_seconds: float
        if next_entry is None:
            watchtime_seconds = video_length_seconds
        else:
            watchtime_seconds = min(round((next_entry.timestamp - history_entry.timestamp).total_seconds()), video_length_seconds)

        return {
            'song_id': history_entry.song_id,
            'title': history_entry.title,
            'author': history_entry.author,
            'timestamp': history_entry.timestamp,
            'song_length_seconds': video_length_seconds,
            'listen_time_seconds': watchtime_seconds
        }
    
class TitleAuthorBuilder:
    ignore_channel: set[str]
    # (author_from_title, channel_name) -> video_titles
    conflicts : dict[tuple[str, str], set[str]]
    def __init__(self):
        with open('data/ignore_channel_as_author.csv', 'r', encoding="utf-8") as f:
            self.ignore_channel = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
        self.conflicts = {}

    def build_title_author(self, data: json, metadata: Optional[YoutubeMusicVideoMetadata]) -> tuple[str, str]:
        video_title = metadata.title if metadata is not None else data.get("title").replace(" angesehen", "")
        video_title = data.get("title").replace(" angesehen", "")
        video_title = re.sub(r"Lyrics|Official (Music )?Video|HD|\d* Remaster(ed)?|(Official )?Audio|Remastered \d*|Remaster(ed)?|Instrumental|Mono|(New )?Stereo( (Version|Mix))?", "", video_title, flags=re.IGNORECASE)
        video_title = re.sub(r"(\(\s*\)|\[\s*\])", "", video_title).strip()

        channel_name = metadata.channel_title if metadata is not None else data.get("subtitles")[0].get("name")
        channel_name = channel_name.replace(" - Topic", "").replace("VEVO", "").replace("vevo", "").replace("music", "").replace("official", "").strip()
        channel_name = re.sub(r"Official|Music", "", channel_name).strip()

        special_case = self.special_cases(video_title, channel_name)
        if special_case is not None:
            return special_case

        if len(video_title.split(" - ")) > 1:
            author_from_video_title, title_from_video_title = video_title.split(" - ", 1)
            author_from_video_title = author_from_video_title.strip()
            author_from_video_title = author_from_video_title.strip()
            if channel_name.replace(" ", "").lower() in self.ignore_channel:
                # ok: Channel is some generic channel and the author is always in front of the title
                return title_from_video_title, author_from_video_title

            if author_from_video_title == channel_name:
                # ok: Channel and video title's author match
                return title_from_video_title, author_from_video_title
            normalized_author_from_video_title = re.sub(r"( |\&|\.|\\|'|-)", "", author_from_video_title)
            normalized_author_from_video_title = normalized_author_from_video_title.replace("&", "and")
            if normalized_author_from_video_title.lower() == channel_name.lower():
                # ok: Channel and video title's author match
                return title_from_video_title, author_from_video_title
            
            if channel_name.replace(" ", "").lower() in normalized_author_from_video_title.lower():
                # ok: Channel and video title's author match partially (e.g. "Elton John, Britney Spears" vs "EltonJohn")
                return title_from_video_title, author_from_video_title

            else:
                # conflict
                conflict_key = (author_from_video_title, channel_name)
                if conflict_key in self.conflicts:
                    self.conflicts[conflict_key].add(video_title)
                else:
                    self.conflicts[conflict_key] = {video_title}
                return video_title, channel_name
        else:
            # ok, video title does not contain any author
            return video_title, channel_name

    def special_cases(self, title: str, channel: str) -> Optional[tuple[str, str]]:
        if channel == "CookieAdventures" and "The Social Network" in title:
            return f"{title.split("-")[0].strip()} (From The Social Network)", "Trent Reznor & Atticus Ross"
        elif channel == "zombiphile68" and "Death Proof" in title:
            a, t = title.split(" - ")
            return t.replace("Death Proof", "From Death Proof").strip(), a.split(" ", 1)[1].strip()
        elif channel == "SonySoundtracks":
            # TODO
            return "", ""
        elif channel == "Nicholas Britell":
            return title, channel
        elif channel == "Linkin Park":
            return title.split(" - ")[0].strip(), channel
        elif channel == "Horror Lover" and "Carrie 1976" in title:
            # TODO
            return "", ""
        else:
            return None