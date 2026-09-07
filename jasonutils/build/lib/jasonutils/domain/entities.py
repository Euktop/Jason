from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class CommandPayload:
    """Неизменяемый объект команды (Value Object)."""
    name: str
    params: Dict[str, Any]

@dataclass(frozen=True)
class ExecutionRequest:
    """Запрос на выполнение (Value Object). Связывает источник и команду."""
    source_id: str
    payload: CommandPayload

@dataclass(frozen=True)
class ExecutionResult:
    """Результат выполнения (Value Object)."""
    request: ExecutionRequest
    result: Optional[Any] = None
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.error is None