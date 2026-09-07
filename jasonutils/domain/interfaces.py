from abc import ABC, abstractmethod
from typing import Iterable, Any
from pathlib import Path
from jasonutils.domain.entities import CommandPayload, ExecutionRequest, ExecutionResult


class ICommandSource(ABC):
    @abstractmethod
    def load(self) -> Iterable[ExecutionRequest]:
        """Возвращает поток запросов на выполнение."""
        pass


class ICommandExecutor(ABC):
    @abstractmethod
    def execute(self, payload: CommandPayload) -> Any:
        """Выполняет команду. Не знает о Jason или JSON."""
        pass


class IResultWriter(ABC):
    @abstractmethod
    def write(self, result: ExecutionResult) -> None:
        """Записывает результат выполнения."""
        pass


class ICommandValidator(ABC):
    @abstractmethod
    def validate(self, raw_data: dict) -> None:
        """Валидирует сырые данные. Бросает ValidationError при ошибке."""
        pass


class IOutput(ABC):
    @abstractmethod
    def write(self, message: str) -> None:
        """Выводит сообщение (например, в консоль)."""
        pass


class IPathSecurityGuard(ABC):
    """Абстракция проверки доступа к файловой системе."""

    @abstractmethod
    def check_access(self, target_path: Path) -> None:
        """
        Проверяет доступ к пути.
        Бросает SecurityError, если доступ запрещён.
        """
        pass

    @abstractmethod
    def reload(self) -> None:
        """Перечитывает списки из файлов (hot-reload)."""
        pass