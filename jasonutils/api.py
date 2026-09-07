from typing import Optional, Any, List, Dict
from jason import Jason
from jasonutils.bootstrap import (
    build_batch_pipeline,
    build_single_yaml_pipeline,
    build_single_json_pipeline,
    build_execute_command_use_case
)
from jasonutils.domain.entities import CommandPayload

class JasonUtils:
    """
    Фасад для удобного программного использования.
    Делегирует всю работу Use Cases, не нарушая границ слоев.
    """
    def run_yaml(self, yaml_path: str, schema: Optional[dict] = None) -> None:
        use_case = build_single_yaml_pipeline(yaml_path, schema)
        use_case.execute()

    def run_folder(self, input_dir: str, output_dir: str) -> None:
        use_case = build_batch_pipeline(input_dir, output_dir)
        use_case.execute()

    def run_json_file(self, file_path: str, schema: Optional[dict] = None) -> None:
        use_case = build_single_json_pipeline(file_path, schema)
        use_case.execute()

    def execute_command(self, command_dict: Dict[str, Any]) -> Any:
        """
        Выполняет одну команду из словаря и возвращает результат.
        Пример: execute_command({"command": "add", "params": {"a": 2, "b": 3}}) -> 5
        
        Не создаёт временных файлов, результат возвращается напрямую в Python-объект.
        """
        use_case = build_execute_command_use_case()
        payload = CommandPayload(
            name=command_dict["command"],
            params=command_dict.get("params", {})
        )
        return use_case.execute_single(payload)

    def execute_commands(self, commands: List[Dict[str, Any]]) -> List[Any]:
        """
        Выполняет список команд и возвращает список результатов.
        """
        use_case = build_execute_command_use_case()
        payloads = [
            CommandPayload(
                name=cmd["command"],
                params=cmd.get("params", {})
            )
            for cmd in commands
        ]
        return use_case.execute_batch(payloads)