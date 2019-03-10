import sqlite3
import psycopg2
from flask import g
from config.config import DATABASE_CONFIG

def get_db():
    g.db = psycopg2.connect(dbname=DATABASE_CONFIG["dbname"], host=DATABASE_CONFIG["host"], user=DATABASE_CONFIG["user"], 
                                password=DATABASE_CONFIG["password"], port=DATABASE_CONFIG["port"])
    return g.db.cursor()

def close_db():
    g.db.commit()
    g.db.close()
    db = g.pop('db', None)
    if db is not None:
        db.close()

"""
conn = sqlite3.connect('example.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE stocks
             (date text, trans text, symbol text, qty real, price real)''')

# Insert a row of data
c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
"""