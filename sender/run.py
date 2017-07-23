import logging
import logging.config
import os
import os.path
from configparser import ConfigParser

from src.bot import Bot
from src.config import encoding


def main():
    setup_logging()

    Bot().run()


def setup_logging():
    log_config = ConfigParser()
    log_config.read(os.path.join('resources', 'cfg', 'logging.conf'), encoding=encoding)

    user_log_config = os.getenv('LOGGING_CONFIG_PATH', './logging.conf')
    if os.path.exists(user_log_config) and os.path.isfile(user_log_config):
        log_config.read(user_log_config, encoding=encoding)

    logging.config.fileConfig(log_config)

if __name__ == '__main__':
    main()
