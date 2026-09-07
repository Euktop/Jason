import os
import json
from jasonutils.domain.interfaces import IResultWriter, IOutput
from jasonutils.domain.entities import ExecutionResult

class JsonResultWriter(IResultWriter):
    def __init__(self, output_folder: str):
        self._folder = output_folder
        os.makedirs(self._folder, exist_ok=True)

    def write(self, result: ExecutionResult) -> None:
        out_data = {
            "command_id": result.request.source_id,
            "command": result.request.payload.name,
            "params": result.request.payload.params,
            "result": result.result,
            "error": result.error,
        }
        out_path = os.path.join(self._folder, f"{result.request.source_id}.out.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(out_data, f, ensure_ascii=False, indent=2)

class ConsoleResultWriter(IResultWriter):
    def __init__(self, output: IOutput):
        self._output = output

    def write(self, result: ExecutionResult) -> None:
        if result.is_success:
            self._output.write(f"[{result.request.source_id}] Успешно: {result.result}")
        else:
            self._output.write(f"[{result.request.source_id}] Ошибка: {result.error}")