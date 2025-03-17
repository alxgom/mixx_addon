# src/callbacks/shared.py
import datetime
from src.database.database import get_playlists

all_playlists = get_playlists()
party_sets = [pl for pl in all_playlists if pl["date"] is not None]
playlist_id_to_date = {pl["id"]: pl["date"] for pl in party_sets}

party_set_options = sorted(
    [{"label": pl["name"], "value": pl["id"]} for pl in party_sets],
    key=lambda x: playlist_id_to_date[x["value"]]
)

if party_sets:
    earliest_date = min(pl["date"] for pl in party_sets if pl["date"] is not None)
    default_start = earliest_date.date().isoformat()
else:
    default_start = None

default_end = datetime.datetime.now().date().isoformat()
