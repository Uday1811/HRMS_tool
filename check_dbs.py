import sqlite3
import sys
import os

files = ["TestDB_Petabytz.sqlite3", "TestDB_Petabytz_corrupted.sqlite3", "TestDB_Petabytz_broken.sqlite3"]

for f in files:
    if not os.path.exists(f):
        print(f"File {f} not found.")
        continue
    print(f"Checking {f}...")
    try:
        conn = sqlite3.connect(f)
        c = conn.cursor()
        c.execute("pragma integrity_check;")
        res = c.fetchall()
        print(f"Result for {f}: {res}")
        
        # Also check table count
        c.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
        count = c.fetchone()[0]
        print(f"Table count: {count}")

        conn.close()
    except Exception as e:
        print(f"Error checking {f}: {e}")
