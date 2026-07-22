from typing import Any, Dict
from domain.interfaces import ICommandHandler
from domain.exceptions import CommandExecutionError

class PrintCommandHandler(ICommandHandler):
    def execute(self, params: Dict[str, Any]) -> Any:
        message = params.get("message", "")
        return message  # просто возвращаем для вывода

class AddCommandHandler(ICommandHandler):
    def execute(self, params: Dict[str, Any]) -> Any:
        a = params.get("a")
        b = params.get("b")
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise CommandExecutionError("Параметры 'a' и 'b' должны быть числами")
        return a + b

class EchoCommandHandler(ICommandHandler):
    def execute(self, params: Dict[str, Any]) -> Any:
        return params.get("text", "")

class SumCommandHandler(ICommandHandler):
    def execute(self, params: Dict[str, Any]) -> Any:
        numbers = params.get("numbers")
        if not isinstance(numbers, list) or not all(isinstance(n, (int, float)) for n in numbers):
            raise CommandExecutionError("Параметр 'numbers' должен быть списком чисел")
        return sum(numbers)