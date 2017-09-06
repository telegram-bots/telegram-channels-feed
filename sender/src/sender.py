import logging

from telegram.ext import Updater

from src.component.config import config, updates_notifier


class Sender:
    """
    Main initializer
    """
    def __init__(self):
        self.updater = Updater(token=config['bot']['token'])

    def run(self):
        logging.info("Sender started")
        updates_notifier.instance(self.updater.bot)
        self.updater.idle()
