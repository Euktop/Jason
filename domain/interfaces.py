from abc import ABC, abstractmethod
from typing import Any, Dict

class ICommandHandler(ABC):
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        """Выполняет команду с заданными параметрами и возвращает результат."""
        pass

class ICommandRegistry(ABC):
    @abstractmethod
    def get_handler(self, command_name: str) -> ICommandHandler:
        """Возвращает обработчик для команды или выбрасывает исключение."""
        pass

class IOutput(ABC):
    @abstractmethod
    def write(self, message: str) -> None:
        """Выводит сообщение."""
        pass

class IFileReader(ABC):
    @abstractmethod
    def read_text(self, path: str) -> str:
        """Читает текстовое содержимое файла."""
        pass