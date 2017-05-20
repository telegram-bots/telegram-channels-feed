# Config
import os
import os.path
from configparser import ConfigParser


def load() -> ConfigParser:
    app_config = ConfigParser()
    app_config.read(os.path.join('resources', 'application.conf'), encoding=encoding)

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
notifications = Notifications()
queue_consumer = QueueConsumer(config['rabbit'])
post_formatter = PostFormatter()
updates_notifier = UpdatesNotifier(
    notifications=notifications,
    queue_consumer=queue_consumer,
    post_formatter=post_formatter
)
