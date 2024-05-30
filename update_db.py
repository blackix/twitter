import sqlite3

def update_db():
    conn = sqlite3.connect('tweets.db')
    c = conn.cursor()
    try:
        c.execute('ALTER TABLE tweets ADD COLUMN date_posted TEXT')
    except sqlite3.OperationalError:
        print("Column 'date_posted' already exists, skipping...")

    try:
        c.execute('ALTER TABLE tweets ADD COLUMN image_path TEXT')
    except sqlite3.OperationalError:
        print("Column 'image_path' already exists, skipping...")
    
    conn.commit()
    conn.close()

update_db()
