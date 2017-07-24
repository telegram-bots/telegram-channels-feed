# Config
import logging
import logging.config
import os.path
from configparser import ConfigParser

import os


def load() -> ConfigParser:
    app_config = ConfigParser()
    app_config.read_dict({
        'bot': {
          'token': os.getenv('CF_BOT_TOKEN')
        },
        'db': {
            'url': os.getenv('CF_DB_URL')
        },
        'rabbit': {
            'url': os.getenv('CF_RABBIT_URL')
        },
        'tg-cli': {
            'url': os.getenv('CF_TGCLI_URL')
        }
    })

    user_app_config = os.getenv('CONFIG_PATH', './application.conf')
    if os.path.exists(user_app_config) and os.path.isfile(user_app_config):
        app_config.read(user_app_config, encoding=encoding)

    return app_config


def extend(conf: ConfigParser) -> ConfigParser:
    def getlist(self, section, option, type=str):
        return list(map(lambda o: type(o), conf.get(section, option).split(',')))

    ConfigParser.getlist = getlist

    return conf


def validate(conf: ConfigParser) -> ConfigParser:
    sections = {
        'bot': ['token'],
        'tg-cli': ['url'],
        'db': ['url'],
        'rabbit': ['url']
    }

    for section, options in sections.items():
        if not conf.has_section(section):
            raise ValueError("Config is not valid!",
                             "Section '{}' is missing!".format(section))
        for option in options:
            if not conf.has_option(section, option):
                raise ValueError("Config is not valid!",
                                 "Option '{}' in section '{}' is missing!".format(option, section))

    return conf


def setup_logging():
    log_config = ConfigParser()
    log_config.read(os.path.join('resources', 'cfg', 'logging.conf'), encoding=encoding)

    user_log_config = os.getenv('LOGGING_CONFIG_PATH', './logging.conf')
    if os.path.exists(user_log_config) and os.path.isfile(user_log_config):
        log_config.read(user_log_config, encoding=encoding)

    logging.config.fileConfig(log_config)


encoding = 'utf-8'
setup_logging()
config = validate(extend(load()))

# IOC
from .service import *
notifications = Notifications()
queue_consumer = QueueConsumer(config['rabbit'])
updates_notifier = UpdatesNotifier(
    notifications=notifications,
    queue_consumer=queue_consumer
)
