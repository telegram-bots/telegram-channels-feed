from .base import Base
from .help import Help
from .subscribe import Subscribe
from .unsubscribe import Unsubscribe
from .list import List

commands = {}
for clazz in Base.__subclasses__():
    command_name = getattr(clazz, 'name')
    command_aliases = getattr(clazz, 'aliases')
    instance = clazz()

    if command_name is not None:
        commands[command_name] = instance
    for command_alias in command_aliases:
        commands[command_alias] = instance
