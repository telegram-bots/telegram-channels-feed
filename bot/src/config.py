# Config
import configparser
import os

encoding = 'utf-8'

sections = {
    'bot': ['token', 'name'],
    'logging': ['level'],
    'tg-cli': ['id', 'host', 'port'],
    'db': ['host', 'port', 'name', 'user', 'password'],
    'updates': ['mode']
}


def getlist(self, section, option, type=str):
    return list(map(lambda o: type(o), config.get(section, option).split(',')))

configparser.ConfigParser.getlist = getlist

config_path = os.environ['CONFIG_PATH']
config = configparser.ConfigParser()
config.read(config_path, encoding=encoding)

for section, options in sections.items():
    if not config.has_section(section):
        raise ValueError("Config is not valid!", 
                         "Section '{}' is missing!".format(section))
    for option in options:
        if not config.has_option(section, option):
            raise ValueError("Config is not valid!",
                             "Option '{}' in section '{}' is missing!".format(option, section))


# IOC
from .service import *
db = DB(config['db'])
tg_cli = TelegramCLI(config['tg-cli'])
tg_cli.connect()
subscription_service = SubscriptionService(db=db, tg_cli=tg_cli)
