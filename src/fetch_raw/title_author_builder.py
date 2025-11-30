import json
import re
from typing import Optional


class TitleAuthorBuilder:
    ignore_channel: set[str]
    # (author_from_title, channel_name) -> video_titles
    conflicts : dict[tuple[str, str], set[str]]
    def __init__(self):
        with open('data/ignore_channel_as_author.csv', 'r', encoding="utf-8") as f:
            self.ignore_channel = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
        self.conflicts = {}

    def build_title_author(self, video_title: str, channel_name: str) -> tuple[str, str]:
        video_title = re.sub(r"Lyrics|Official (Music )?Video|HD|\d* Remaster(ed)?|(Official )?Audio|Remastered \d*|Remaster(ed)?|Instrumental|Mono|(New )?Stereo( (Version|Mix))?", "", video_title, flags=re.IGNORECASE)
        video_title = re.sub(r"(\(\s*\)|\[\s*\])", "", video_title).strip()

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