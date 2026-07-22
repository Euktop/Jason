import json
from typing import Dict, Any
from domain.exceptions import InvalidJsonError
from application.dtos import CommandRequest

class JsonCommandParser:
    def parse(self, raw_json: str) -> CommandRequest:
        try:
            data: Dict[str, Any] = json.loads(raw_json)
        except json.JSONDecodeError as e:
            raise InvalidJsonError(f"Некорректный JSON: {e}")

        command = data.get("command")
        params = data.get("params", {})
        if not command:
            raise InvalidJsonError("Поле 'command' обязательно")
        if not isinstance(command, str):
            raise InvalidJsonError("Поле 'command' должно быть строкой")
        if not isinstance(params, dict):
            raise InvalidJsonError("Поле 'params' должно быть объектом")

        return CommandRequest(command, params)