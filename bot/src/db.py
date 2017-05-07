import psycopg2
import psycopg2.extras
import psycopg2.pool
import logging
from typing import Any, List, Generator


class DB:
    def __init__(self, config):
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            1,
            10,
            host=config['host'],
            port=config.getint('port'),
            dbname=config['name'],
            user=config['user'],
            password=config['password']
        )
        self.transaction = False
        self.transaction_conn = None
        self.__init_schema()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.closeall()

    def connection(self, key=None):
        if self.transaction:
            if self.transaction_conn is None:
                self.transaction_conn = self.pool.getconn(key)
            return self.transaction_conn
        return self.pool.getconn(key)

    def execute(self, callback, transaction=False):
        conn = self.connection()
        cur = conn.cursor()

        try:
            callback(cur)
        except:
            conn.rollback()
            raise
        else:
            if transaction:
                conn.commit()
        finally:
            cur.close()

    def execute_in_transaction(self, callback) -> Any:
        self.transaction = True
        conn = self.connection()

        try:
            result = callback()
        except:
            conn.rollback()
            raise
        else:
            conn.commit()
            return result
        finally:
            self.transaction = False

    def get_all(self, callback, mapper=None) -> List[Any]:
        conn = self.connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            callback(cur)
            result = [dict(row) if mapper is None else mapper(dict(row)) for row in cur.fetchall()]
        except:
            raise
        else:
            return result
        finally:
            cur.close()

    def get_lazy(self, callback, mapper=None) -> Generator[Any, None, None]:
        conn = self.connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            callback(cur)
        except:
            raise
        else:
            for row in cur:
                yield dict(row) if mapper is None else mapper(dict(row))
        finally:
            cur.close()

    def get_one(self, callback, mapper=None) -> Any:
        conn = self.connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        try:
            callback(cur)
            result = cur.fetchone()
        except:
            raise
        else:
            if result is None:
                return None

            return mapper(result) if mapper is not None else result
        finally:
            cur.close()

    def __init_schema(self):
        logging.info("[DB] IMPORTING SCHEMA")
        schema_file = 'resources/sql/schema.sql'
        with open(schema_file, 'r') as file:
            self.execute(lambda cur: cur.execute(file.read()))
        logging.info("[DB] SUCCESSFULLY IMPORTED")
