from .base import Base
from .help import Help
from .ping import Ping
from .subscribe import Subscribe
from .unsubscribe import Unsubscribe

commands = {}
for clazz in Base.__subclasses__():
    command_name = getattr(clazz, 'name')
    command_aliases = getattr(clazz, 'aliases')
    execute_method = getattr(clazz, 'execute')

    if command_name is not None:
        commands[command_name] = execute_method
    for command_alias in command_aliases:
        commands[command_alias] = execute_method
