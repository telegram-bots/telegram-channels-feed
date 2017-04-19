import psycopg2
import os

# Запуск бота
db_url = os.environ['DATABASE_URL']
conn = psycopg2.connect(db_url)
cur = conn.cursor()

cur.execute(
    """SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public'
    AND table_type='BASE TABLE';"""
)
print(">>>>>>>>>>> TABLES <<<<<<<<<<<<<<<")
print(cur.fetchall())
print(">>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<")

cur.close()
conn.close()
