from argparse import ArgumentParser

from src.bot import Bot
from src.config import db


def main():
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

if __name__ == '__main__':
    main()
