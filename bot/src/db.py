import logging

from functools import wraps
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from typing import Any, Generator

from src.domain.entities import *


class DB:
    def __init__(self, config):
        self.engine = create_engine(
            f"postgresql://{config['user']}@{config['host']}:{config.getint('port')}/{config['name']}"
        )
        Base.metadata.bind = self.engine
        self.session = sessionmaker(bind=self.engine)()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def session(self):
        return self.session

    def execute_in_transaction(self, callback) -> Any:
        session = self.session

        try:
            result = callback()
            session.commit()
        except:
            session.rollback()
            raise
        else:
            return result

    def get_lazy(self, callback, mapper=None) -> Generator[Any, None, None]:
        pass
        # conn = self.connection()
        # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #
        # try:
        #     callback(cur)
        # except:
        #     raise
        # else:
        #     for row in cur:
        #         yield dict(row) if mapper is None else mapper(dict(row))
        # finally:
        #     cur.close()

    def __init_schema(self):
        logging.info("[DB] IMPORTING SCHEMA")
        schema_file = 'resources/sql/schema.sql'
        with open(schema_file, 'r') as file:
            self.session.execute(text(file.read()))
            self.session.commit()
        logging.info("[DB] SUCCESSFULLY IMPORTED")


def transactional(db):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(self, *f_args, **f_kwargs):
            return db.execute_in_transaction(callback=lambda: fn(self, *f_args, **f_kwargs))
        return wrapped
    return wrapper
