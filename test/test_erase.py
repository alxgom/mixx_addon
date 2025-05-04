import sqlite3

# Path to whichever DB you want to clean up
db_path = r"C:\Users\Alexis\AppData\Local\Mixxx\mixxxdb.sqlite"
#https://www.youtube.com/%
#https://music.youtube.com%
conn = sqlite3.connect(db_path)
try:
    cur = conn.cursor()
    # Set comment to empty string where it starts with the YouTube Music URL
    cur.execute("""
        UPDATE library
           SET comment = ''
         WHERE comment LIKE 'https://www.youtube.com/%'
    """)
    print(f"Cleared {cur.rowcount} comments.")  # feedback
    
    conn.commit()
finally:
    conn.close()
