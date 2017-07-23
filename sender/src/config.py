# Config
import os.path
from configparser import ConfigParser

import os


def load() -> ConfigParser:
    app_config = ConfigParser()
    app_config.read(os.path.join('resources', 'cfg', 'application.conf'), encoding=encoding)

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
        'bot': ['token', 'name'],
        'tg-cli': ['id', 'host', 'port'],
        'db': ['host', 'port', 'name', 'user', 'password'],
        'rabbit': ['host', 'port', 'user', 'password', 'vh'],
        'updates': ['mode']
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


encoding = 'utf-8'
config = validate(extend(load()))

# IOC
from .service import *
notifications = Notifications()
queue_consumer = QueueConsumer(config['rabbit'])
updates_notifier = UpdatesNotifier(
    notifications=notifications,
    queue_consumer=queue_consumer
)
