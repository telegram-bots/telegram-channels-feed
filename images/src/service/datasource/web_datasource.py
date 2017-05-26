import json
import logging
from typing import Optional, Tuple
from urllib.request import urlopen

import magic

from . import BaseDataSource
from ...config import encoding, config
from ...domain import Image


class WebDataSource(BaseDataSource):
    RESOLVE_IMG_API_URL = "https://api.telegram.org/bot%s/getFile?file_id=%s"
    DOWNLOAD_IMG_API_URL = "https://api.telegram.org/file/bot%s/%s"

    def __init__(self):
        self.token = config['bot']['token']

    def get(self, img_id: str) -> Image:
        img_path = self.__resolve_img_path(img_id)
        img_mine, img_content = self.__get_image_content(img_path)

        return Image(img_mine, img_content)

    def store(self, img_id: str, content: bytes):
        raise NotImplementedError()

    def __resolve_img_path(self, img_id: str) -> Optional[str]:
        logging.info(f"Resolving image path: {img_id}")

        try:
            with urlopen(self.RESOLVE_IMG_API_URL % (self.token, img_id)) as response:
                data = json.loads(response.read().decode(encoding))
                if data['ok'] is not True:
                    return None
                return data['result']['file_path']
        except Exception as e:
            logging.warn(f"Failed to resolve image path: {e}")
            return None

    def __get_image_content(self, path: str) -> Tuple[Optional[str], Optional[bytes]]:
        if path is None:
            return None, None

        logging.info(f"Downloading image from path: {path}")

        try:
            with urlopen(self.DOWNLOAD_IMG_API_URL % (self.token, path)) as response:
                data = response.read()
                mime = magic.from_buffer(data, mime=True)
                return mime, data
        except Exception as e:
            logging.warn(f"Failed to download image: {e}")
            return None, None
