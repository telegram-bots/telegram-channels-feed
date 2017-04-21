# Config
import configparser
import os

encoding = 'utf-8'

sections = {
    'bot': ['token', 'name', 'anchors', 'purge_interval', 'default_chance', 'spam_stickers'],
    'logging': ['level'],
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


