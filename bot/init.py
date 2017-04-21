import psycopg2
import os
import os.path

# Инициализация бота и БД
db_url = os.environ['DATABASE_URL']
conn = psycopg2.connect(db_url)
cur = conn.cursor()
schema_file = '../resources/sql/schema.sql'

print("IMPORTING SCHEMA")
print("SCHEMA FILE EXISTS: " + str(os.path.isfile(schema_file)))

with open(schema_file, 'r') as file:
    cur.execute(file.read())

print("SUCCESSFULLY IMPORTED")

conn.commit()
cur.close()
conn.close()
