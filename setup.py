import sqlite3

import os

from database import DBName

def setupDB():
    if os.path.exists(DBName):
        print(f"Can't continue, please remove DB file by name {DBName} first")
        exit()

    conn = sqlite3.connect(DBName)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE posts
               (    id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                    title text NOT NULL,
                    author text NOT NULL,
                    content text,
                    image_id text,
                    inserted_at datetime DEFAULT CURRENT_TIMESTAMP)''')

    cur.execute('''CREATE TABLE comments
               (    id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
                    post_id integer NOT NULL,
                    author text NOT NULL,
                    content text NOT NULL,
                    inserted_at datetime DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setupDB()
