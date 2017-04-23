import psycopg2
import logging


class DB:
    def __init__(self, db_url):
        self.conn = psycopg2.connect(db_url)
        self.__init_schema()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection().close()

    def connection(self):
        return self.conn

    def execute(self, callback):
        conn = self.connection()
        cur = conn.cursor()

        callback(cur)

        conn.commit()
        cur.close()

    def __init_schema(self):
        logging.info("[DB] IMPORTING SCHEMA")
        schema_file = '../resources/sql/schema.sql'
        with open(schema_file, 'r') as file:
            self.execute(lambda cur: cur.execute(file.read()))
        logging.info("[DB] SUCCESSFULLY IMPORTED")
