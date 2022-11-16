import mysql.connector

db_conn = mysql.connector.connect(host="lab6a.eastus2.cloudapp.azure.com", user="python",
password="password", database="events",auth_plugin='mysql_native_password')
c = db_conn.cursor()

c.execute('''
          CREATE TABLE damaged_parts
          (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
          damage_cost VARCHAR(250) NOT NULL, 
          damage_description VARCHAR(250) NOT NULL,
          damaged_part_qty INTEGER NOT NULL,
          order_date VARCHAR(100) NOT NULL,
            order_number VARCHAR(250) NOT NULL,
            part_number INTEGER NOT NULL,
           part_type VARCHAR(250) NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE receive_orders
          (id INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT,
            order_date VARCHAR(200) NOT NULL,
            order_number VARCHAR(250) NOT NULL,
            part_number INTEGER NOT NULL,
           part_price INTEGER NOT NULL,
           part_quantity INTEGER NOT NULL,
           part_type VARCHAR(250) NOT NULL,
           trace_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL)
          ''')


db_conn.commit()
db_conn.close()