from . import BaseRepository
from ..config import db


class PostgreRepository(BaseRepository):
    def __init__(self):
        self.db = db
