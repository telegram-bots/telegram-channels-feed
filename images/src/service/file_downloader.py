import logging
import json
from urllib.request import urlopen
from src.config import config, encoding


class FileDownloader:
    RESOLVE_API_URL = "https://api.telegram.org/bot%s/getFile?file_id=%s"
    DOWNLOAD_API_URL = "https://api.telegram.org/file/bot%s/%s"

    def __init__(self):
        self.token = config['bot']['token']

    def download(self, file_id):
        path = self.__resolve_path(file_id)
        return self.__get_content(path)

    def __resolve_path(self, file_id):
        logging.info('Resolving file path: {}'.format(file_id))

        try:
            with urlopen(self.RESOLVE_API_URL % (self.token, file_id)) as response:
                data = json.loads(response.read().decode(encoding))
                if data['ok'] is not True:
                    return None
                return data['result']['file_path']
        except Exception as e:
            logging.warn('Failed to resolve image path: {}'.format(e))
            return None

    def __get_content(self, path):
        if path is None:
            return None

        logging.info('Downloading image from path: {}'.format(path))

        try:
            with urlopen(self.DOWNLOAD_API_URL % (self.token, path)) as response:
                return response.read()
        except Exception as e:
            logging.warn('Failed to download file: {}'.format(e))
            return None
