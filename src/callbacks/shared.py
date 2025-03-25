import datetime
from src.database.database import get_playlists

def get_shared_data():
    all_playlists = get_playlists()
    # Filter playlists that have a valid date.
    party_sets = [pl for pl in all_playlists if pl.get("date") is not None]
    # Build a mapping from playlist id to its date.
    playlist_id_to_date = {pl["id"]: pl["date"] for pl in party_sets}
    # Build dropdown options.
    party_set_options = sorted(
        [{"label": pl["name"], "value": pl["id"]} for pl in party_sets],
        key=lambda x: playlist_id_to_date[x["value"]]
    )
    if party_sets:
        earliest_date = min(pl["date"] for pl in party_sets if pl.get("date") is not None)
        default_start = earliest_date.date().isoformat()
    else:
        default_start = None
    default_end = datetime.datetime.now().date().isoformat()
    
    return {
        "party_sets": party_sets,
        "playlist_id_to_date": playlist_id_to_date,
        "party_set_options": party_set_options,
        "default_start": default_start,
        "default_end": default_end
    }
