import sqlite3

db_path = r"C:\DEV\mixx_addon\test\mixxxdb_subset.sqlite"
conn = sqlite3.connect(db_path)
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
