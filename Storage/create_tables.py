import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE damaged_parts
          (id INTEGER PRIMARY KEY ASC,
          damage_cost VARCHAR(250) NOT NULL, 
          damage_description VARCHAR(250) NOT NULL,
          damaged_part_qty INTEGER NOT NULL,
          order_date VARCHAR(250) NOT NULL,
          order_number VARCHAR(250) NOT NULL,
          part_number INTEGER NOT NULL,
          part_type VARCHAR(250) NOT NULL,
          trace_id VARCHAR(250) NOT NULL,
          date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE receive_orders
          (id INTEGER PRIMARY KEY ASC,
            order_date VARCHAR(200) NOT NULL,
            order_number VARCHAR(250) NOT NULL,
            part_number INTEGER NOT NULL,
           part_price INTEGER NOT NULL,
           part_quantity INTEGER NOT NULL,
           part_type VARCHAR(250) NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

conn.commit()
conn.close()
