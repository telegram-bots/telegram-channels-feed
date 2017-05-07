# Config
import os
from configparser import ConfigParser


def load() -> ConfigParser:
    config_path = os.environ['CONFIG_PATH']
    config = ConfigParser()
    config.read(config_path, encoding=encoding)
    return config


def extend(conf: ConfigParser) -> ConfigParser:
    def getlist(self, section, option, type=str):
        return list(map(lambda o: type(o), conf.get(section, option).split(',')))

    ConfigParser.getlist = getlist

    return conf


def validate(conf: ConfigParser) -> ConfigParser:
    sections = {
        'bot': ['token', 'name'],
        'logging': ['level'],
        'tg-cli': ['id', 'host', 'port'],
        'db': ['host', 'port', 'name', 'user', 'password'],
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
from .db import DB
from .tg_cli import TelegramCLI
db = DB(config['db'])
tg_cli = TelegramCLI(config['tg-cli'])

from .repository import *
user_repository = UserRepository()
channel_repository = ChannelRepository()
subscription_repository = SubscriptionRepository()

from .service import *
subscriptions = Subscriptions()
notifications = Notifications(subscriptions=subscriptions)
