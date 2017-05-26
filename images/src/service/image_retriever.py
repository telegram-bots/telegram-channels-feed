from ..config import web_ds
from ..domain import Image


class ImageRetriever:
    def __init__(self):
        pass

    def retrieve(self, img_id: str) -> Image:
        return web_ds.get(img_id.replace('.jpg', ''))
