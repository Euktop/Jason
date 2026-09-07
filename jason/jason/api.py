from jason.domain.interfaces import ICommandHandler, IOutput, IFileReader
from jason.domain.exceptions import DomainError
from jason.infrastructure.console_output import ConsoleOutput
from jason.infrastructure.file_reader import FileReader
from jason.infrastructure.command_registry import SimpleCommandRegistry
from jason.adapters.json_parser import JsonCommandParser
from jason.adapters.file_loader import FileCommandLoader
from jason.application.dtos import CommandRequest
from jason.application.use_cases import ProcessCommandUseCase

class Jason:
    def __init__(self, output: IOutput = None, file_reader: IFileReader = None):
        self._output = output or ConsoleOutput()
        self._file_reader = file_reader or FileReader()
        self._parser = JsonCommandParser()
        self._loader = FileCommandLoader(self._file_reader, self._parser)
        self._registry = SimpleCommandRegistry()
        self._use_case = ProcessCommandUseCase(self._registry, self._output)

    def register(self, command_name: str, handler: ICommandHandler) -> None:
        """Регистрирует обработчик для команды."""
        self._registry.register(command_name, handler)

    def run_file(self, file_path: str) -> None:
        """Загружает JSON из файла и выполняет команду."""
        request = self._loader.load(file_path)
        self._use_case.execute(request)

    def run_json(self, json_str: str) -> None:
        """Парсит JSON-строку и выполняет команду."""
        request = self._parser.parse(json_str)
        self._use_case.execute(request)