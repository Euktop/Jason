import sys
from domain.exceptions import DomainError
from infrastructure.console_output import ConsoleOutput
from infrastructure.file_reader import FileReader
from infrastructure.command_handlers import (
    PrintCommandHandler,
    AddCommandHandler,
    EchoCommandHandler,
    SumCommandHandler,
)
from infrastructure.command_registry import SimpleCommandRegistry
from adapters.json_parser import JsonCommandParser
from adapters.file_loader import FileCommandLoader
from application.use_cases import ProcessCommandUseCase

def main():
    if len(sys.argv) < 2:
        print("Использование: python main.py <путь_к_json_файлу>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Сборка зависимостей
    output = ConsoleOutput()
    file_reader = FileReader()
    parser = JsonCommandParser()
    loader = FileCommandLoader(file_reader, parser)

    # Регистрация команд
    registry = SimpleCommandRegistry()
    registry.register("print", PrintCommandHandler())
    registry.register("add", AddCommandHandler())
    registry.register("echo", EchoCommandHandler())
    registry.register("sum", SumCommandHandler())

    use_case = ProcessCommandUseCase(registry, output)

    # Загрузка и выполнение
    try:
        request = loader.load(file_path)
        use_case.execute(request)
    except DomainError as e:
        output.write(f"Ошибка: {e}")
    except Exception as e:
        output.write(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()