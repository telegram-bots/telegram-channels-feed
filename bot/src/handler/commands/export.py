from . import Base
import os
import csv
from typing import List
from src.config import subscriptions
from src.domain.entities import Channel


class Export(Base):
    name = 'export'
    aliases = ['e']

    def execute(self, command):
        rows = subscriptions.list(command)
        if len(rows) == 0:
            self.reply(command, "You don't have active subscriptions.")

        file = f"{command.chat_id}_export.csv"
        self.__create_csv(file, subscriptions.list(command))
        self.bot.send_document(chat_id=command.chat_id,
                               document=open(file, 'rb'))
        os.remove(file)

    @staticmethod
    def __create_csv(file: str, rows: List[Channel]):
        with open(file, 'x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['SHORT_URL', 'URL', 'TITLE'])
            for row in rows:
                writer.writerow([f"@{row.url}", f"https://t.me/{row.url}", row.name])
