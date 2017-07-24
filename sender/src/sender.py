import logging

from telegram.ext import Updater

from src.config import config, updates_notifier


class Sender:
    """
    Main initializer and dispatcher of messages
    """
    def __init__(self):
        self.updater = Updater(token=config['bot']['token'])
        self.dispatcher = self.updater.dispatcher

    def run(self):
        logging.info("Sender started")
        updates_notifier.instance(self.updater.bot)
        self.updater.idle()
