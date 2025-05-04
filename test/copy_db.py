
import sqlite3
import shutil
import os
import sys

# 1) Determine paths
# Path to your original Mixxx DB:
orig_db = r"C:\Users\Alexis\AppData\Local\Mixxx\mixxxdb.sqlite"

# Directory where this script lives:
script_dir = os.path.dirname(os.path.abspath(__file__))

# Destination: a file named "mixxxdb_subset.sqlite" next to your script
subset_db = os.path.join(script_dir, "mixxxdb_subset.sqlite")

# 2) If it already exists, remove it so we start fresh
if os.path.exists(subset_db):
    os.remove(subset_db)

# 3) Copy the original DB to the script directory
shutil.copy(orig_db, subset_db)

# 4) Open both databases
src = sqlite3.connect(orig_db)
dst = sqlite3.connect(subset_db)
dst.row_factory = sqlite3.Row

try:
    dst_cur = dst.cursor()

    # 5) Keep only the first 100 tracks by id
    dst_cur.execute("""
        DELETE FROM library
         WHERE id NOT IN (
             SELECT id FROM library ORDER BY id LIMIT 500
         )
    """)

    # 6) Clean up orphaned rows in related tables
    dst_cur.executescript("""
        DELETE FROM PlaylistTracks
         WHERE track_id NOT IN (SELECT id FROM library);
        DELETE FROM crate_tracks
         WHERE track_id NOT IN (SELECT id FROM library);
        DELETE FROM track_locations
         WHERE id NOT IN (SELECT location FROM library);
    """)

    # 7) Reclaim space
    dst_cur.execute("VACUUM;")
    dst.commit()

    print(f"✅ Subset database created: {subset_db}")

finally:
    src.close()
    dst.close()
