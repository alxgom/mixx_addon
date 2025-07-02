# src/db/notes_db.py
import os
import sqlite3
from datetime import datetime


DB_DIR = os.path.dirname(__file__)  # points to src/cb
DB_PATH = os.path.join(DB_DIR, "extra_features.sqlite")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS playlist_notes (
                notes_id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL UNIQUE,
                notes TEXT,
                rating INTEGER,
                date_modified DATETIME,
                date_created DATETIME
            )
        """)
        conn.commit()
def upsert_note(playlist_id, notes, rating):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    now = datetime.utcnow().isoformat()

    # Check if note exists
    cur.execute("SELECT notes_id FROM playlist_notes WHERE playlist_id = ?", (playlist_id,))
    result = cur.fetchone()

    if result:
        # Update existing
        cur.execute("""
            UPDATE playlist_notes
            SET notes = ?, rating = ?, date_modified = ?
            WHERE playlist_id = ?
        """, (notes, rating, now, playlist_id))
    else:
        # Insert new note
        cur.execute("""
            INSERT INTO playlist_notes (playlist_id, notes, rating, date_created, date_modified)
            VALUES (?, ?, ?, ?, ?)
        """, (playlist_id, notes, rating, now, now))

    conn.commit()
    conn.close()

def get_note(playlist_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("""
        SELECT notes, rating
        FROM playlist_notes
        WHERE playlist_id = ?
    """, (playlist_id,)).fetchone()
    conn.close()
    if row:
        notes, rating = row
        return notes or "", rating or None
    return "", None

