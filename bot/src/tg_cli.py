import json
import logging
import socket
import time
from urllib.parse import urlparse

from typing import Tuple, List

from src.config import encoding


class TelegramCLI:
    EOL = '\n'
    BUFFER_SIZE = 8192

    def __init__(self, config):
        self.url = urlparse(config['url'])
        self.socket = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__disconnect()

    def lookup_channel(self, channel_url: str) -> Tuple[int, str]:
        command = '{"ID": "SearchPublicChat", "username_": "%s"}'
        response = self.__send(command % channel_url)
        json_data = json.loads(response[0], encoding=encoding)
        channel_id = json_data['id_']
        channel_name = json_data['title_']

        return channel_id, channel_name

    def subscribe_to_channel(self, id_: int):
        command = '{"ID": "AddChatMember", "chat_id_": %d, "user_id_": %d, "forward_limit_": 2}'
        response = self.__send(command % (id_, int(self.url.username)))
        json_data = json.loads(response[0], encoding=encoding)

        if json_data['ID'] != 'Ok':
            raise ConnectionError(f"[tg-cli] Failed to subscribe: {json_data}")

    def unsubscribe_from_channel(self, id_: int):
        command = '{"ID": "ChangeChatMemberStatus", "chat_id_": %d, "user_id_": %d, "status_": {"ID": "ChatMemberStatusLeft"}}'
        response = self.__send(command % (id_, int(self.url.username)))
        json_data = json.loads(response[0], encoding=encoding)

        if json_data['ID'] != 'Ok':
            raise ConnectionError(f"[tg-cli] Failed to unsubscribe: {json_data}")

    def __connect(self, retries=5):
        if retries == 0:
            logging.error('[tg-cli] Maximum number of retries reached. Stopping')
            return

        try:
            self.__disconnect()
            logging.debug(f"[tg-cli] Connecting to {self.url.hostname}:{self.url.port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.url.hostname, self.url.port))
            logging.debug('[tg-cli] Connected')
        except socket.error as e:
            self.__disconnect()
            logging.warning(f"[tg-cli] Failed to connect : {str(e)}")
            time.sleep(5)
            self.__connect(retries - 1)
        except Exception as e:
            self.__disconnect()
            raise e

    def __disconnect(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def __send(self, command) -> List[str]:
        try:
            self.__connect()

            if self.EOL in command:
                command = str.join(' ', command.strip(self.EOL))
            command = (command + self.EOL).encode(encoding)

            self.socket.sendall(command)
            time.sleep(0.5)
            return self.socket.recv(self.BUFFER_SIZE) \
                       .decode(encoding) \
                       .strip() \
                       .split(self.EOL)[1:]
        except socket.error:
            self.__send(command)
        finally:
            self.__disconnect()
