from typing import List, Optional
from jasonutils.domain.interfaces import IOutput

class CapturingOutput(IOutput):
    """
    Реализация IOutput, которая сохраняет вывод в память,
    а не печатает его в консоль. Полезно для программного API
    или юнит-тестирования.
    """
    def __init__(self):
        self.outputs: List[str] = []
        self.last_output: Optional[str] = None

    def write(self, message: str) -> None:
        self.outputs.append(message)
        self.last_output = message