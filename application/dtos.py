from typing import Any, Dict

class CommandRequest:
    def __init__(self, command: str, params: Dict[str, Any]):
        self.command = command
        self.params = params