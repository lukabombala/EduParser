import sqlite3 as sl
import config

con = sl.connect(config.database_name)

with con:
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE MESSAGE (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            sender TEXT,
            date DATE,
            content TEXT
        );
    """)