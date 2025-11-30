import json
import sqlite3
import sys
from db.Channel import Channel
from db.SongHistoryEntry import SongHistoryEntry
from db.UnavailableVideoId import UnavailableVideoId
from db.Video import Video
from db.prepare_db import prepare_db
from utils.youtube_api import fetch_metadata
from db.SongMetadata import RawSongMetadata, SongMetadata
from utils.title_author_builder import TitleAuthorBuilder

if len(sys.argv) < 3:
    raise RuntimeError("Please provide path to history file and database file")

con = sqlite3.connect(sys.argv[2])
cur = con.cursor()

prepare_db(cur)

with open(sys.argv[1], "r", encoding="utf-8") as f:
    history = json.load(f)

history_entries = [
    SongHistoryEntry.from_json(entry) for entry in history if entry.get("header") == "YouTube Music"
]

SongHistoryEntry.insert(history_entries, con)

video_ids_to_fetch = SongHistoryEntry.get_video_ids_to_fetch_metadata_for(cur)


for i in range(0, len(video_ids_to_fetch), 50):
    print(
        "Processing songs", i, "to", min(i + 50, len(video_ids_to_fetch)),
        "out of", len(video_ids_to_fetch),
    )
    wanted_ids = set(video_ids_to_fetch[i : i + 50])
    received_metadata = fetch_metadata(wanted_ids)
    received_ids = set(it.id for it in received_metadata)

    Video.insert(received_metadata, cur)
    Channel.insert(received_metadata, cur)
    UnavailableVideoId.insert(wanted_ids.difference(received_ids), cur)

title_author_builder = TitleAuthorBuilder()

raw_metadata = RawSongMetadata.fetch(cur)

entries: list[SongMetadata] = []
for index, row in enumerate(raw_metadata):
    title = row.song_title if row.song_title is not None else ""
    author_name = row.channel_name if row.channel_name is not None else ""
    title, author_name, safe = title_author_builder.build_title_author(title, author_name)
 
    entry = SongMetadata(row.song_id, title, author_name, safe)
    entries.append(entry)
    
SongMetadata.insert(entries, cur)

con.commit()
con.close()
