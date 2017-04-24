import json
import time
import logging
import socket
from src.config import encoding


class TelegramCLI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.retries = 0
        self.connected = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__disconnect()

    def connect(self):
        if self.retries > 5:
            logging.error('[tg-cli] Maximum number of retries reached. Stopping')
            return

        try:
            logging.info('[tg-cli] Connecting to {0}:{1}'.format(self.host, self.port))
            self.socket.connect((self.host, self.port))
            self.connected = True
            logging.info('[tg-cli] Connected')
        except socket.error as ex:
            logging.warn('[tg-cli] Failed to connect : {0}'.format(ex))
            time.sleep(5)
            self.connect()

    def lookup_channel(self, channel_url):
        command = '{"ID": "SearchPublicChat", "username_": "%s"}'
        response = self.__send_and_receive(command % channel_url)
        json_data = json.loads(response[0], encoding=encoding)
        channel_id = json_data['id_']
        channel_name = json_data['title_']

        return channel_id, channel_name

    def subscribe_to_channel(self, channel_id, user_id):
        command = '{"ID": "AddChatMember", "chat_id_": %d, "user_id_": %d, "forward_limit_": 2}'
        response = self.__send_and_receive(command % (channel_id, user_id))
        json_data = json.loads(response[0], encoding=encoding)

        if json_data['ID'] != 'Ok':
            raise ConnectionError('Failed to subscribe: {0}'.format(json_data))

    def __disconnect(self):
        if self.connected:
            self.socket.close()
            self.connected = False

    def __send(self, command):
        if not self.connected:
            raise ConnectionError('Not connected to tg-cli!')
        if '\n' in command:
            command = str.join(' ', command.strip('\n'))
        self.socket.sendall((command + '\n').encode('utf-8'))
        time.sleep(0.5)

    def __send_and_receive(self, command):
        self.__send(command)
        return self.socket.recv(8192).decode('utf-8').strip().split('\n')[1:]
