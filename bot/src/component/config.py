# Config
import logging
import logging.config
import os.path
from configparser import ConfigParser

import os


def load_config() -> ConfigParser:
    app_config = ConfigParser()
    app_config.read_dict({
        'bot': {'token': os.getenv('CF_BOT_TOKEN')},
        'db': {'url': os.getenv('CF_DB_URL')},
        'updates': {'mode': 'polling'}
    })

    return app_config


def setup_logging():
    log_config = ConfigParser()
    log_config.read(os.path.join('resources', 'cfg', 'logging.conf'), encoding=encoding)

    user_log_config = os.getenv('LOGGING_CONFIG_PATH', './logging.conf')
    if os.path.exists(user_log_config) and os.path.isfile(user_log_config):
        log_config.read(user_log_config, encoding=encoding)

    logging.config.fileConfig(log_config)


encoding = 'utf-8'
setup_logging()
config = load_config()

# IOC
from .db import DB
db = DB(config['db'])

from src.repository import *
user_repository = UserRepository()
channel_repository = ChannelRepository()
subscription_repository = SubscriptionRepository()

from src.service import *
subscriptions = Subscriptions()
settings = Settings()
