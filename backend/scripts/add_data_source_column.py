import os
import sqlite3

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base, 'helplink.db')
    db_path = os.path.abspath(db_path)

    if not os.path.exists(db_path):
        print(f"DB not found: {db_path}")
        return 2

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info('sos_signals')")
    cols = [r[1] for r in cur.fetchall()]
    if 'data_source' in cols:
        print('data_source column already exists')
    else:
        try:
            cur.execute("ALTER TABLE sos_signals ADD COLUMN data_source TEXT;")
            conn.commit()
            print('Added data_source column to sos_signals')
        except Exception as e:
            print(f'Failed to add column: {e}')
            return 1
    conn.close()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
