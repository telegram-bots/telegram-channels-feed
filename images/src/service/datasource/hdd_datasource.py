from . import BaseDataSource
from ...domain import Image


class HDDDataSource(BaseDataSource):
    def __init__(self):
        pass

    def get(self, img_id: str) -> Image:
        pass

    def store(self, img_id: str, content: bytes):
        pass
