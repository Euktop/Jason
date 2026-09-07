from typing import Dict
from jason.domain.interfaces import ICommandHandler, ICommandRegistry
from jason.domain.exceptions import CommandNotFoundError

class SimpleCommandRegistry(ICommandRegistry):
    def __init__(self):
        self._handlers: Dict[str, ICommandHandler] = {}

    def register(self, name: str, handler: ICommandHandler) -> None:
        self._handlers[name] = handler

    def get_handler(self, command_name: str) -> ICommandHandler:
        handler = self._handlers.get(command_name)
        if handler is None:
            raise CommandNotFoundError(f"Неизвестная команда: '{command_name}'")
        return handler