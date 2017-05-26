import logging
import json
from typing import Optional
from urllib.request import urlopen
from ..config import config, encoding


class FileDownloader:
    RESOLVE_API_URL = "https://api.telegram.org/bot%s/getFile?file_id=%s"
    DOWNLOAD_API_URL = "https://api.telegram.org/file/bot%s/%s"

    def __init__(self):
        self.token = config['bot']['token']

    def download(self, file_id: str) -> Optional[bytes]:
        path = self.__resolve_path(file_id)
        return self.__get_content(path)

    def __resolve_path(self, file_id: str) -> Optional[str]:
        logging.info(f"Resolving file path: {file_id}")

        try:
            with urlopen(self.RESOLVE_API_URL % (self.token, file_id)) as response:
                data = json.loads(response.read().decode(encoding))
                if data['ok'] is not True:
                    return None
                return data['result']['file_path']
        except Exception as e:
            logging.warn(f"Failed to resolve image path: {e}")
            return None

    def __get_content(self, path: str) -> Optional[bytes]:
        if path is None:
            return None

        logging.info(f"Downloading image from path: {path}")

        try:
            with urlopen(self.DOWNLOAD_API_URL % (self.token, path)) as response:
                return response.read()
        except Exception as e:
            logging.warn(f"Failed to download file: {e}")
            return None
