import psycopg2
import psycopg2.extras
import logging


class DB:
    def __init__(self, config):
        self.conn = psycopg2.connect(
            host=config['host'],
            port=config.getint('port'),
            dbname=config['name'],
            user=config['user'],
            password=config['password']
        )
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

    def get_all(self, callback, mapper=None):
        conn = self.connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        callback(cur)

        result = [dict(row) if mapper is None else mapper(dict(row)) for row in cur.fetchall()]
        cur.close()

        return result

    def get_lazy(self, callback, mapper=None):
        conn = self.connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        callback(cur)

        for row in cur:
            yield dict(row) if mapper is None else mapper(dict(row))

        cur.close()

    def get_one(self, callback, mapper=None):
        conn = self.connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        callback(cur)

        result = cur.fetchone()
        cur.close()

        if result is None:
            return None

        return mapper(result) if mapper is not None else result

    def __init_schema(self):
        logging.info("[DB] IMPORTING SCHEMA")
        schema_file = 'resources/sql/schema.sql'
        with open(schema_file, 'r') as file:
            self.execute(lambda cur: cur.execute(file.read()))
        logging.info("[DB] SUCCESSFULLY IMPORTED")
