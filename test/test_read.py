import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__name__))
DB_PATH = r"C:\Users\Alexis\AppData\Local\Mixxx\mixxxdb.sqlite"
DB_PATH_test= os.path.join(BASE_DIR, 'mixxxdb_subset.sqlite')
if os.path.isfile(DB_PATH):
    dbpath = DB_PATH
else: dbpath = DB_PATH_test

print(dbpath)

conn = sqlite3.connect(dbpath)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get the first 10 tracks in the library with their comments
cur.execute(
    """
    SELECT
        lib.artist,
        lib.title,
        lib.album,
        lib.bpm,
        lib.duration,
        lib.comment,
        tl.location AS file_path
    FROM library lib
    JOIN track_locations tl
        ON lib.location = tl.id
    ORDER BY lib.id
    LIMIT 10
    """
)

tracks = cur.fetchall()
for t in tracks:
    print(
        " - {artist} – {title} ({album})  "
        "BPM:{bpm}  Duration:{duration:.2f}s  "
        "Comment: {comment!r}  "
        "File: {file_path}"
        .format(**t)
    )
