import logging
import os
import os.path
from typing import Tuple


class ImageRetriever:
    def __init__(self, downloader, storage):
        self.downloader = downloader
        self.storage = storage

    def retrieve(self, img_id: str) -> Tuple[str, str]:
        img_id = img_id.replace('.jpg', '')

        if not self.storage.contains(file_id=img_id):
            logging.info(f"Image {img_id} not exists, downloading...")
            file = self.downloader.download(file_id=img_id)
            self.storage.store(file_id=img_id, content=file)

        return os.path.split(self.storage.get_path(file_id=img_id))
