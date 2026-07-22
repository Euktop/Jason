from domain.interfaces import ICommandRegistry, IOutput
from domain.exceptions import CommandNotFoundError, CommandExecutionError
from application.dtos import CommandRequest

class ProcessCommandUseCase:
    def __init__(self, registry: ICommandRegistry, output: IOutput):
        self._registry = registry
        self._output = output

    def execute(self, request: CommandRequest) -> None:
        try:
            handler = self._registry.get_handler(request.command)
            result = handler.execute(request.params)
            # Преобразуем результат в строку для вывода
            self._output.write(str(result))
        except CommandNotFoundError as e:
            self._output.write(f"Ошибка: {e}")
        except CommandExecutionError as e:
            self._output.write(f"Ошибка выполнения команды: {e}")
        except Exception as e:
            self._output.write(f"Непредвиденная ошибка: {e}")