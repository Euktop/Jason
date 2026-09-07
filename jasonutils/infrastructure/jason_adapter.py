from typing import Any
from jason import Jason
from jasonutils.domain.interfaces import ICommandExecutor
from jasonutils.domain.entities import CommandPayload
from jasonutils.domain.exceptions import ExecutionError


class JasonCommandExecutor(ICommandExecutor):
    """Адаптер к ядру Jason. Инкапсулирует работу с внутренним реестром Jason."""

    def __init__(self, jason_instance: Jason):
        self._jason = jason_instance

    def execute(self, payload: CommandPayload) -> Any:
        # Обработка пакетной команды (batch)
        if payload.name == "batch":
            commands = payload.params.get("commands", [])
            results = []
            for cmd in commands:
                try:
                    # Каждая команда – словарь с полями "command" и "params"
                    handler = self._jason._registry.get_handler(cmd["command"])
                    res = handler.execute(cmd.get("params", {}))
                    results.append({
                        "command": cmd["command"],
                        "result": res,
                        "error": None
                    })
                except Exception as e:
                    results.append({
                        "command": cmd["command"],
                        "result": None,
                        "error": str(e)
                    })
            return results

        # Обычная команда
        try:
            handler = self._jason._registry.get_handler(payload.name)
            return handler.execute(payload.params)
        except Exception as e:
            raise ExecutionError(f"Ошибка при выполнении команды '{payload.name}': {e}") from e