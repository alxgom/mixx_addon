import sqlite3

db_path = r"C:\Users\Alexis\AppData\Local\Mixxx\mixxxdb.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get all playlists and their tracks
cur.execute("SELECT id, name FROM Playlists")
for playlist in cur.fetchall():
    pid, name = playlist["id"], playlist["name"]
    print(f"Playlist: {name}")
    cur2 = conn.cursor()
    cur2.execute(f"""SELECT lib.artist, lib.title, lib.album, lib.bpm, lib.duration, lib.comment, tl.location as file_path
                     FROM PlaylistTracks pt 
                     JOIN library lib ON pt.track_id = lib.id 
                     JOIN track_locations tl ON lib.location = tl.id
                     WHERE pt.playlist_id = ? 
                     ORDER BY pt.position""", (pid,))
    tracks = cur2.fetchall()
    for track in tracks:
        print(" - {artist} – {title} ({album}) BPM:{bpm}".format(**track))  # example output format

# Get all crates and their tracks
cur.execute("SELECT id, name FROM crates")
for crate in cur.fetchall():
    cid, name = crate["id"], crate["name"]
    print(f"Crate: {name}")
    cur2 = conn.cursor()
    cur2.execute(f"""SELECT lib.artist, lib.title, lib.album, lib.bpm, lib.comment, tl.location as file_path
                     FROM crate_tracks ct 
                     JOIN library lib ON ct.track_id = lib.id 
                     JOIN track_locations tl ON lib.location = tl.id
                     WHERE ct.crate_id = ?""", (cid,))
    tracks = cur2.fetchall()
    for track in tracks:
        print(" - {artist} – {title} (BPM:{bpm})".format(**track))
