import datetime
import re
from src.database.database import get_playlists, get_library_songs, get_tracks_for_playlist

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

    # --- 3. Repetition Analysis (First Time, Second Time, 3+ Times) ---
    # We must process party_sets in chronological order.
    # party_sets is already sorted by date because of how we built options? 
    # Actually, let's ensure it is sorted strictly by date.
    sorted_party_sets = sorted(party_sets, key=lambda x: x["date"])
    
    song_counts = {}  # (artist, title) -> count
    repetition_stats = []

    for pl in sorted_party_sets:
        tracks = get_tracks_for_playlist(pl["id"])
        
        count_first = 0
        count_second = 0
        count_third_plus = 0
        total_tracks = 0
        
        # Track which songs we've seen IN THIS SET to avoid double counting 
        # (though usually a song appears once per set, but good to be safe id logic changes)
        # However, the requirement is "songs played", so if it's played twice in a set, it counts twice?
        # Usually for "first time played", we care about the *track* being new.
        # Let's iterate through tracks.
        
        for track in tracks:
            key = (track.get("artist"), track.get("title"))
            current_count = song_counts.get(key, 0)
            
            if current_count == 0:
                count_first += 1
            elif current_count == 1:
                count_second += 1
            else:
                count_third_plus += 1
            
            total_tracks += 1
            
        # Update global counts AFTER processing the whole set? 
        # Or as we go? 
        # Usually "First time played" means "Before this moment". 
        # But if I play a song twice in my FIRST set, is the second time "Second time"?
        # Yes, technically.
        # So we should update counts as we go essentially, OR update them after if we consider the "Set" as the unit of time.
        # Given "first time played in a set", it usually refers to the set as a whole vs history.
        # If I play a new song twice in a set, the user probably considers it "New" for that set.
        # Let's stick to: "Status at the start of the set".
        
        # BUT, if we do that, we need to update the global counts *after* the analysis loop.
        for track in tracks:
            key = (track.get("artist"), track.get("title"))
            song_counts[key] = song_counts.get(key, 0) + 1
            
        pct_first = (count_first / total_tracks * 100) if total_tracks > 0 else 0
        pct_second = (count_second / total_tracks * 100) if total_tracks > 0 else 0
        pct_third_plus = (count_third_plus / total_tracks * 100) if total_tracks > 0 else 0
        
        repetition_stats.append({
            "id": pl["id"],
            "name": pl["name"],
            "date": pl["date"],
            "pct_first": pct_first,
            "pct_second": pct_second,
            "pct_third_plus": pct_third_plus
        })

    # --- 4. Return a single dictionary with all the prepared data ---
    return {
        "party_sets": party_sets,
        "playlist_id_to_date": playlist_id_to_date,
        "party_set_options": party_set_options,
        "default_start": default_start,
        "default_end": default_end,
        "all_library_artists": all_library_artists,
        "repetition_stats": repetition_stats
    }

# This crucial line runs the expensive initialization once and stores the result.
_shared_data = _initialize_data()

def get_shared_data():
    """
    This function is now extremely fast. It just returns the data that was
    already prepared when the app started.
    """
    return _shared_data




