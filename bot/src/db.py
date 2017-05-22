import logging

from functools import wraps
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker, Session
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
        self.session.close()
        self.engine.dispose()

    def init(self):
        logging.info("[db] IMPORTING SCHEMA")
        schema_file = 'resources/sql/schema.sql'
        with open(schema_file, 'r') as file:
            self.session.execute(text(file.read()))
            self.session.commit()
        logging.info("[db] SUCCESSFULLY IMPORTED")

    def session(self) -> Session:
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

    def get_lazy(self, query, limit=100) -> Generator[Any, None, None]:
        offset = 0
        while True:
            r = False
            for elem in query.limit(limit).offset(offset):
                r = True
                yield elem
            offset += limit
            if not r:
                break
