import os
import json
import yaml
from typing import Iterable

from jasonutils.domain.interfaces import ICommandSource
from jasonutils.domain.entities import ExecutionRequest, CommandPayload
from jasonutils.domain.exceptions import SourceError
from jasonutils.adapters.mappers import CommandMapper


class FolderJsonSource(ICommandSource):
    def __init__(self, folder_path: str, mapper: CommandMapper):
        self._folder = folder_path
        self._mapper = mapper

    def load(self) -> Iterable[ExecutionRequest]:
        if not os.path.isdir(self._folder):
            raise SourceError(f"Папка не найдена: {self._folder}")

        for filename in os.listdir(self._folder):
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(self._folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if isinstance(data, dict):
                    # Одиночная команда – обычный запрос
                    yield ExecutionRequest(filename, self._mapper.map(data))
                elif isinstance(data, list):
                    # Список команд – упаковываем в одну batch-команду
                    yield ExecutionRequest(
                        filename,
                        CommandPayload("batch", {"commands": data})
                    )
                else:
                    raise SourceError(f"Некорректный формат в {filename}")
            except Exception as e:
                raise SourceError(f"Ошибка чтения {filename}: {e}")


class YamlCommandSource(ICommandSource):
    def __init__(self, file_path: str, mapper: CommandMapper):
        self._path = file_path
        self._mapper = mapper

    def load(self) -> Iterable[ExecutionRequest]:
        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise SourceError(f"Ошибка чтения YAML {self._path}: {e}")

        if isinstance(data, dict):
            yield ExecutionRequest(os.path.basename(self._path), self._mapper.map(data))
        elif isinstance(data, list):
            # Для одиночного режима (YAML) тоже можно использовать batch,
            # но по условию задачи мы меняем только пакетный режим (FolderJsonSource).
            # Оставляем как есть – для YAML список будет обработан как несколько команд.
            # При желании можно аналогично обернуть в batch, но это не требуется.
            for i, cmd in enumerate(data):
                yield ExecutionRequest(f"{os.path.basename(self._path)}_{i}", self._mapper.map(cmd))
        else:
            raise SourceError("YAML должен содержать словарь или список словарей")


class SingleJsonSource(ICommandSource):
    def __init__(self, file_path: str, mapper: CommandMapper):
        self._path = file_path
        self._mapper = mapper

    def load(self) -> Iterable[ExecutionRequest]:
        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            raise SourceError(f"Ошибка чтения JSON {self._path}: {e}")

        if isinstance(data, dict):
            yield ExecutionRequest(os.path.basename(self._path), self._mapper.map(data))
        elif isinstance(data, list) and len(data) > 0:
            # Для одиночного режима берём только первую команду
            yield ExecutionRequest(os.path.basename(self._path), self._mapper.map(data[0]))
        else:
            raise SourceError("Файл должен содержать JSON-объект или непустой список")