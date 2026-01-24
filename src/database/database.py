import re
import sqlite3
import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__name__))
DB_PATH = r"C:\Users\Alexis\AppData\Local\Mixxx\mixxxdb.sqlite"
DB_PATH_test= os.path.join(BASE_DIR, 'mixxxdb_subset.sqlite')

if os.path.isfile(DB_PATH):
    dbpath = DB_PATH
else: dbpath = DB_PATH_test
     
def get_playlists():
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM Playlists")
    playlists = cur.fetchall()
    conn.close()

    result = []
    date_pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4})')
    for row in playlists:
        name = row["name"]
        match = date_pattern.match(name)
        playlist_date = None
        if match:
            date_str = match.group(1)
            for fmt in ("%m/%d/%Y", "%m/%d/%y"):
                try:
                    playlist_date = datetime.datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
        result.append({
            "id": row["id"],
            "name": name,
            "date": playlist_date
        })
    return result

def get_tracks_for_playlist(playlist_id):
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query_with_hidden = """
        SELECT lib.artist, lib.title, lib.album, lib.bpm, lib.duration, lib.rating,
               tl.location as file_path, pt.position
        FROM PlaylistTracks pt
        JOIN library lib ON pt.track_id = lib.id
        JOIN track_locations tl ON lib.location = tl.id
        WHERE pt.playlist_id = ? AND lib.hidden = 0
        ORDER BY pt.position
    """
    try:
        cur.execute(query_with_hidden, (playlist_id,))
    except sqlite3.OperationalError:
        query_without_hidden = """
            SELECT lib.artist, lib.title, lib.album, lib.bpm, lib.duration, lib.rating,
                   tl.location as file_path, pt.position
            FROM PlaylistTracks pt
            JOIN library lib ON pt.track_id = lib.id
            JOIN track_locations tl ON lib.location = tl.id
            WHERE pt.playlist_id = ?
            ORDER BY pt.position
        """
        cur.execute(query_without_hidden, (playlist_id,))
    tracks = cur.fetchall()
    conn.close()
    return [dict(track) for track in tracks]

def get_crates():
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM crates")
    crates = cur.fetchall()
    conn.close()
    return [dict(crate) for crate in crates]

def get_songs_not_in_crates():
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query_with_hidden = """
      SELECT lib.artist, lib.title, lib.album, lib.bpm, lib.duration, lib.rating
      FROM library lib
      LEFT JOIN crate_tracks ct ON lib.id = ct.track_id
      WHERE ct.track_id IS NULL AND lib.hidden = 0
    """
    try:
        cur.execute(query_with_hidden)
    except sqlite3.OperationalError:
        query_without_hidden = """
          SELECT lib.artist, lib.title, lib.album, lib.bpm, lib.duration, lib.rating
          FROM library lib
          LEFT JOIN crate_tracks ct ON lib.id = ct.track_id
          WHERE ct.track_id IS NULL
        """
        cur.execute(query_without_hidden)
    songs = cur.fetchall()
    conn.close()
    return [dict(song) for song in songs]

def get_songs_for_crate(crate_id):
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query = """
        SELECT lib.artist, lib.title, lib.album, lib.bpm, lib.duration, lib.rating
        FROM crate_tracks ct
        JOIN library lib ON ct.track_id = lib.id
        WHERE ct.crate_id = ? AND lib.hidden = 0
    """
    cur.execute(query, (crate_id,))
    songs = cur.fetchall()
    conn.close()
    return [dict(song) for song in songs]

def get_library_songs():
    conn = sqlite3.connect(dbpath)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query_with_hidden = "SELECT id, artist, title, album, bpm, rating FROM library WHERE hidden = 0"
    try:
        cur.execute(query_with_hidden)
    except sqlite3.OperationalError:
        cur.execute("SELECT id, artist, title, album, bpm, rating FROM library")
    songs = cur.fetchall()
    conn.close()
    return [dict(song) for song in songs]

def format_duration(seconds):
    seconds = int(seconds)
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"

def join_dates(x):
    dates = [d.strftime('%Y-%m-%d') for d in x if d is not None]
    return ", ".join(sorted(dates))
