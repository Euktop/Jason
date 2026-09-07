from typing import Any, List
from jasonutils.domain.interfaces import ICommandSource, ICommandExecutor, IResultWriter, IOutput
from jasonutils.domain.entities import ExecutionResult, CommandPayload

class BatchProcessingUseCase:
    """Пакетная обработка. Единственная причина для изменения - бизнес-правила батча."""
    def __init__(self, source: ICommandSource, executor: ICommandExecutor, writer: IResultWriter):
        self._source = source
        self._executor = executor
        self._writer = writer

    def execute(self) -> None:
        for request in self._source.load():
            try:
                result = self._executor.execute(request.payload)
                self._writer.write(ExecutionResult(request, result=result))
            except Exception as e:
                self._writer.write(ExecutionResult(request, error=str(e)))

class SingleCommandUseCase:
    """Выполнение команд из источника с выводом результата."""
    def __init__(self, source: ICommandSource, executor: ICommandExecutor, output: IOutput):
        self._source = source
        self._executor = executor
        self._output = output

    def execute(self) -> None:
        for request in self._source.load():
            try:
                result = self._executor.execute(request.payload)
                self._output.write(f"[{request.source_id}] Успешно: {result}")
            except Exception as e:
                self._output.write(f"[{request.source_id}] Ошибка: {e}")

class ExecuteCommandUseCase:
    """
    Use Case для выполнения команд из памяти (Python-объектов)
    и возврата сырых результатов. Не зависит от файлов или консоли.
    """
    def __init__(self, executor: ICommandExecutor):
        self._executor = executor

    def execute_single(self, payload: CommandPayload) -> Any:
        """Выполняет одну команду и возвращает результат."""
        return self._executor.execute(payload)

    def execute_batch(self, payloads: List[CommandPayload]) -> List[Any]:
        """Выполняет список команд и возвращает список результатов."""
        results = []
        for payload in payloads:
            results.append(self._executor.execute(payload))
        return results