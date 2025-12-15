import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

source_db = "TestDB_Petabytz_corrupted.sqlite3"
target_db = "TestDB_Petabytz_rescued.sqlite3"

def rescue_db():
    conn_src = sqlite3.connect(source_db)
    conn_tgt = sqlite3.connect(target_db)
    
    cursor_src = conn_src.cursor()
    cursor_tgt = conn_tgt.cursor()
    
    # Get all tables
    try:
        cursor_src.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
        tables = cursor_src.fetchall()
    except sqlite3.DatabaseError as e:
        print(f"Critical error reading sqlite_master: {e}")
        return

    for table_name, create_sql in tables:
        print(f"Processing table: {table_name}")
        
        # Create table in target
        try:
            cursor_tgt.execute(create_sql)
        except sqlite3.Error as e:
            print(f"  Error creating table {table_name}: {e}")
            # If it exists (e.g. from previous run), ignore or drop? 
            # We'll assume fresh start
            
        # Rescue data
        # Try bulk first
        try:
            cursor_src.execute(f"SELECT * FROM \"{table_name}\"")
            rows = cursor_src.fetchall()
            if rows:
                placeholders = ','.join(['?'] * len(rows[0]))
                cursor_tgt.executemany(f"INSERT INTO \"{table_name}\" VALUES ({placeholders})", rows)
                conn_tgt.commit()
                print(f"  Recovered {len(rows)} rows (Bulk)")
            continue
        except sqlite3.DatabaseError:
            print(f"  Bulk read failed for {table_name}, attempting row-by-row...")

        # Row by row rescue
        # We need to know column count for SELECT *
        # We can get it from PRAGMA table_info, or just try to fetch one by one
        
        # Re-query cursor to reset state?
        # Actually standard cursor iteration might fail mid-way.
        # We can try reading by limits/offsets if standard iteration crashes hard.
        
        recovered_count = 0
        try:
            # We can't easily iterate if the query failed.
            # let's try selecting via rowid if possible, or just standard cursor
            c_iter = conn_src.cursor()
            c_iter.execute(f"SELECT * FROM \"{table_name}\"")
            
            while True:
                try:
                    row = c_iter.fetchone()
                    if row is None:
                        break
                    
                    placeholders = ','.join(['?'] * len(row))
                    try:
                        cursor_tgt.execute(f"INSERT INTO \"{table_name}\" VALUES ({placeholders})", row)
                        recovered_count += 1
                    except sqlite3.Error as insert_err:
                        # Should not happen if data is valid
                        pass
                        
                except sqlite3.DatabaseError:
                    # Found a bad row?
                    print("  Skipping malformed row block")
                    # In some python sqlite versions, fetchone might raise error and we can't continue easily.
                    # But we can try to continue or break.
                    # Often once it errors, the cursor is dead.
                    break
        except Exception as e:
            print(f"  Row iteration init failed: {e}")
            
        print(f"  Recovered {recovered_count} rows (Row-by-Row)")
        conn_tgt.commit()

    conn_src.close()
    conn_tgt.close()
    print("Rescue complete.")

if __name__ == "__main__":
    rescue_db()
