import logging
import os
import os.path


class DiskStorage:
    def __init__(self, config):
        self.storage_path = config['path']

    def contains(self, file_id):
        is_exists = os.path.exists(self.__resolve(file_id))
        logging.debug('File {} exists: {}'.format(file_id, is_exists))

        return is_exists

    def get_path(self, file_id):
        return self.__resolve(file_id)

    def store(self, file_id, content):
        with open(self.__resolve(file_id), mode='wb') as fp:
            fp.write(content)

    def __resolve(self, file_id):
        path = os.path.join(self.storage_path, file_id + '.jpg')
        logging.debug('Resolved path for {}: {}'.format(file_id, path))

        return path
