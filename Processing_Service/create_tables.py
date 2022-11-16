import sqlite3
import datetime

conn = sqlite3.connect('data.sqlite')
c = conn.cursor()
def create_database():

    c = conn.cursor()
    c.execute('''
        CREATE TABLE stats
        (id INTEGER PRIMARY KEY ASC,
        num_orders INTEGER NOT NULL,
        max_part_number INTEGER NOT NULL,
        max_part_price INTEGER,
        num_damaged_part INTEGER,
        last_updated STRING(100) NOT NULL)
    ''')
    conn.commit()
    conn.close()

print('Check if STUDENT table exists in the database:')
listOfTables = c.execute(
  """SELECT name FROM sqlite_master WHERE type='table'
  AND name='stats'; """).fetchall()
 
if listOfTables == []:
    create_database()
    print("Table was not found")
    print("table created")
else:
    print('Table found!')
 