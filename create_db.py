import mysql.connector

FHdb = mysql.connector.connect(host='localhost', user='root', passwd = 'Kolade16',)

my_cursor = FHdb.cursor()

my_cursor.execute("CREATE DATABASE footballhouse_users")

my_cursor.execute("SHOW DATABASES")

for db in my_cursor:
    print(db)