import json
import time
import logging
import socket
from src.config import encoding
from typing import Tuple


class TelegramCLI:
    EOL = '\n'
    BUFFER_SIZE = 8192

    def __init__(self, config):
        self.config = config
        self.user_id = config.getint('id')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.retries = 0
        self.connected = False
        self.__connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__disconnect()

    def lookup_channel(self, channel_url: str) -> Tuple[str, str]:
        command = '{"ID": "SearchPublicChat", "username_": "%s"}'
        response = self.__send_and_receive(command % channel_url)
        json_data = json.loads(response[0], encoding=encoding)
        channel_id = json_data['id_']
        channel_name = json_data['title_']

        return channel_id, channel_name

    def subscribe_to_channel(self, id_: int):
        command = '{"ID": "AddChatMember", "chat_id_": %d, "user_id_": %d, "forward_limit_": 2}'
        response = self.__send_and_receive(command % (id_, self.user_id))
        json_data = json.loads(response[0], encoding=encoding)

        if json_data['ID'] != 'Ok':
            raise ConnectionError(f"Failed to subscribe: {json_data}")

    def unsubscribe_from_channel(self, id_: int):
        command = '{"ID": "ChangeChatMemberStatus", "chat_id_": %d, "user_id_": %d, "status_": {"ID": "ChatMemberStatusLeft"}}'
        response = self.__send_and_receive(command % (id_, self.user_id))
        json_data = json.loads(response[0], encoding=encoding)

        if json_data['ID'] != 'Ok':
            raise ConnectionError(f"Failed to unsubscribe: {json_data}")

    def __connect(self):
        if self.retries > 5:
            logging.error('[tg-cli] Maximum number of retries reached. Stopping')
            return

        try:
            logging.info(f"[tg-cli] Connecting to {self.config['host']}:{self.config['port']}")
            self.socket.connect((self.config['host'], self.config.getint('port')))
            self.connected = True
            logging.info('[tg-cli] Connected')
        except socket.error as e:
            logging.warn(f"[tg-cli] Failed to connect : {str(e)}")
            time.sleep(5)
            self.__connect()

    def __disconnect(self):
        if self.connected:
            self.socket.close()
            self.connected = False

    def __send(self, command):
        if not self.connected:
            raise ConnectionError('Not connected to tg-cli!')
        if self.EOL in command:
            command = str.join(' ', command.strip(self.EOL))
        self.socket.sendall((command + self.EOL).encode(encoding))
        time.sleep(0.5)

    def __send_and_receive(self, command):
        self.__send(command)
        return self.socket.recv(self.BUFFER_SIZE).decode(encoding).strip().split(self.EOL)[1:]
