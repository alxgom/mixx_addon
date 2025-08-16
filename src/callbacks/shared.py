import datetime
import re
from src.database.database import get_playlists, get_library_songs

def _custom_title(name):
    """A smarter title-casing function to handle names with apostrophes."""
    # First, fix spacing issues like "o' day" by turning it into "o'day"
    name = re.sub(r"'\s+(\w)", r"'\1", name)
    # Then, apply the standard title case
    return name.title()

def clean_and_split_artists(artist_str):
    if not isinstance(artist_str, str):
        return []
    
    # Lowercase for uniform processing
    s = artist_str.lower()

    s = re.sub(r",\s*(jr|sr)\.?\b", r" \1", s, flags=re.IGNORECASE)
    s = re.sub(r"[\/,&;]|\s+(feat\.?|ft\.?|with|vs\.?)\s+", " and ", s, flags=re.IGNORECASE)

    # Step 3: Now that all connectors are standardized, run the removal patterns.
    # This will now correctly catch " and her handsome devils" even if the original was "& her..."
    remove_patterns = [
        r"\s+and\s+(his|her|the)\s+[\w\s]+", # Simplified and combined pattern
        r"\bvocal\sby\b",
        r"\b's\sspacemen\b",
        r"\bbig\sband\b",
        r"\s+\b(trio|quartet|quintet|sextet|septet)\b"
    ]

    for pat in remove_patterns:
        s = re.sub(pat, "", s, flags=re.IGNORECASE)

    artists = [_custom_title(a.strip()) for a in s.split(" and ") if a.strip()]
    return artists


def _initialize_data():
    """
    An expensive function that runs only ONCE when the app starts.
    It queries the database and prepares all the data needed by the callbacks.
    """
    print("Initializing shared data... (This should only appear once in your console!)")

    # --- 1. Process Playlist Data ---
    all_playlists = get_playlists()
    party_sets = [pl for pl in all_playlists if pl.get("date") is not None]
    playlist_id_to_date = {pl["id"]: pl["date"] for pl in party_sets}
    party_set_options = sorted(
        [{"label": pl["name"], "value": pl["id"]} for pl in party_sets],
        key=lambda x: playlist_id_to_date[x["value"]]
    )

    if party_sets:
        earliest_date = min(pl["date"] for pl in party_sets)
        default_start = earliest_date.date().isoformat()
    else:
        default_start = None
    default_end = datetime.datetime.now().date().isoformat()

    # --- 2. Process Full Artist Library ---
    all_library_songs = get_library_songs()
    all_library_artists = set()
    for song in all_library_songs:
        if song.get('artist'): # Safely handle songs that might not have an artist
            cleaned_names = clean_and_split_artists(song['artist'])
            for name in cleaned_names:
                all_library_artists.add(name)

    # --- 3. Return a single dictionary with all the prepared data ---
    return {
        "party_sets": party_sets,
        "playlist_id_to_date": playlist_id_to_date,
        "party_set_options": party_set_options,
        "default_start": default_start,
        "default_end": default_end,
        "all_library_artists": all_library_artists,
    }

# This crucial line runs the expensive initialization once and stores the result.
_shared_data = _initialize_data()

def get_shared_data():
    """
    This function is now extremely fast. It just returns the data that was
    already prepared when the app started.
    """
    return _shared_data




