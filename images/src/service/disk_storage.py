import logging
import os
import os.path


class DiskStorage:
    def __init__(self, config):
        self.storage_path = config['path']

    def contains(self, file_id: str) -> bool:
        is_exists = os.path.exists(self.__resolve(file_id))
        logging.debug(f"File {file_id} exists: {is_exists}")

        return is_exists

    def get_path(self, file_id: str) -> str:
        return self.__resolve(file_id)

    def store(self, file_id: str, content: bytes):
        with open(self.__resolve(file_id), mode='wb') as fp:
            fp.write(content)

    def __resolve(self, file_id: str) -> str:
        path = os.path.join(self.storage_path, file_id + '.jpg')
        logging.debug(f"Resolved path for {file_id}: {path}")

        return path
