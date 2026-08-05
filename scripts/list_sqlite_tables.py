import sqlite3
import sys

DB = 'db.sqlite3'

try:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name")
    rows = cur.fetchall()
    if not rows:
        print('No tables or views found in', DB)
    else:
        print('Type\tName')
        for name, typ in rows:
            print(f"{typ}\t{name}")
    conn.close()
except Exception as e:
    print('Error:', e)
    sys.exit(1)
