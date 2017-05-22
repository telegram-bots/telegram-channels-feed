import logging
import logging.config
import os
import os.path
from argparse import ArgumentParser
from configparser import ConfigParser

from src.bot import Bot
from src.config import encoding, db


def main():
    setup_logging()

    if is_init():
        init()
    else:
        Bot().run()


def is_init():
    parser = ArgumentParser(description="Is init mode")
    parser.add_argument('--init', action='store_true')
    return vars(parser.parse_args())['init']


def init():
    db.init()


def setup_logging():
    log_config = ConfigParser()
    log_config.read(os.path.join('resources', 'cfg', 'logging.conf'), encoding=encoding)

    user_log_config = os.getenv('LOGGING_CONFIG_PATH', './logging.conf')
    if os.path.exists(user_log_config) and os.path.isfile(user_log_config):
        log_config.read(user_log_config, encoding=encoding)

    logging.config.fileConfig(log_config)

if __name__ == '__main__':
    main()
