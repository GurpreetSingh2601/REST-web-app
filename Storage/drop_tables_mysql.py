import mysql.connector
db_conn = mysql.connector.connect(host="lab6a.eastus2.cloudapp.azure.com", user="python",
password="password", database="events",auth_plugin='mysql_native_password')
db_cursor = db_conn.cursor()
db_cursor.execute('''
DROP TABLE damaged_parts, receive_orders
''')
db_conn.commit()
db_conn.close()