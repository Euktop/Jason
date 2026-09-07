from typing import Optional
from jasonutils.domain.entities import CommandPayload
from jasonutils.domain.interfaces import ICommandValidator

class CommandMapper:
    """Преобразует сырые словари в доменные объекты."""
    def __init__(self, validator: Optional[ICommandValidator] = None):
        self._validator = validator

    def map(self, raw_data: dict) -> CommandPayload:
        if self._validator:
            self._validator.validate(raw_data)
        
        if "command" not in raw_data:
            raise ValueError("Отсутствует поле 'command'")
            
        return CommandPayload(
            name=raw_data["command"],
            params=raw_data.get("params", {})
        )