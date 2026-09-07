import argparse
import json
import os
from jasonutils.bootstrap import (
    build_batch_pipeline, 
    build_single_yaml_pipeline, 
    build_single_json_pipeline
)

def main():
    parser = argparse.ArgumentParser(description="JasonUtils – утилиты для JSON-команд")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Режим работы")

    # Режим одиночного файла
    run_parser = subparsers.add_parser("run", help="Выполнить одну команду из файла")
    run_parser.add_argument("file", help="Путь к JSON или YAML файлу")
    run_parser.add_argument("--schema", help="Путь к JSON Schema для валидации")

    # Режим пакетной обработки
    batch_parser = subparsers.add_parser("batch", help="Обработать все .json из папки input")
    batch_parser.add_argument("input_dir", help="Папка с входными .json файлами")
    batch_parser.add_argument("output_dir", help="Папка для сохранения результатов")

    args = parser.parse_args()

    if args.command == "run":
        schema = None
        if args.schema:
            with open(args.schema, 'r', encoding='utf-8') as f:
                schema = json.load(f)

        if args.file.endswith(('.yaml', '.yml')):
            use_case = build_single_yaml_pipeline(args.file, schema)
        else:
            use_case = build_single_json_pipeline(args.file, schema)
        
        use_case.execute()

    elif args.command == "batch":
        use_case = build_batch_pipeline(args.input_dir, args.output_dir)
        use_case.execute()

if __name__ == "__main__":
    main()