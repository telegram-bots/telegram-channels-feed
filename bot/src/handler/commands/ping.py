from . import Base


class Ping(Base):
    name = 'ping'
    
    @staticmethod
    def execute(bot, command):
        Ping.reply(bot, command, 'pong')
