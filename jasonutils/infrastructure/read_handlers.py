import os
from pathlib import Path
from typing import Any, Dict, List
from jason.domain.interfaces import ICommandHandler
from jason.domain.exceptions import CommandExecutionError
from jasonutils.domain.interfaces import IPathSecurityGuard
from jasonutils.domain.exceptions import SecurityError


# ======================================================================
#  Чтение содержимого файлов
# ======================================================================
class ReadFilesHandler(ICommandHandler):
    """
    Читает содержимое нескольких файлов по указанным путям.
    Возвращает единый список результатов: для каждого файла — статус,
    содержимое или ошибка. Ошибки безопасности/чтения не прерывают
    выполнение — записываются в поле error соответствующей записи.

    params:
        paths (list[str], обязательно) — массив абсолютных путей к файлам
    """
    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        paths = params.get("paths")
        if not paths or not isinstance(paths, list):
            raise CommandExecutionError(
                "Параметр 'paths' обязателен и должен быть непустым массивом"
            )

        results: List[Dict[str, Any]] = []
        for raw_path in paths:
            entry: Dict[str, Any] = {"path": raw_path}
            try:
                target = Path(raw_path)
                self._guard.check_access(target)

                if not target.exists():
                    entry.update({"status": "error", "error": "Файл не найден"})
                elif not target.is_file():
                    entry.update({"status": "error", "error": "Путь не является файлом"})
                else:
                    content = target.read_text(encoding="utf-8")
                    entry.update({
                        "status": "ok",
                        "content": content,
                        "resolved": str(target.resolve())
                    })
            except SecurityError as e:
                entry.update({"status": "error", "error": f"Доступ запрещён: {e}"})
            except UnicodeDecodeError:
                entry.update({
                    "status": "error",
                    "error": "Файл не является текстовым (ошибка декодирования UTF-8)"
                })
            except Exception as e:
                entry.update({"status": "error", "error": str(e)})

            results.append(entry)

        return results


# ======================================================================
#  Чтение структуры папок
# ======================================================================
class ListFilesHandler(ICommandHandler):
    """
    Читает структуру папок: возвращает список всех вложенных файлов и папок.

    params:
        paths (list[str], обязательно) — массив путей к папкам
        depth (int, по умолчанию 0) — глубина вложения.
            0 = бесконечная рекурсия, 1 = только текущая папка,
            2 = текущая + 1 уровень вложенности и т.д.
        type (str, по умолчанию "all") — фильтр:
            "all" — и файлы, и папки
            "files" — только файлы
            "folders" — только папки
    """
    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        paths = params.get("paths")
        depth = params.get("depth", 0)
        type_filter = params.get("type", "all")

        if not paths or not isinstance(paths, list):
            raise CommandExecutionError(
                "Параметр 'paths' обязателен и должен быть непустым массивом"
            )
        if not isinstance(depth, int) or depth < 0:
            raise CommandExecutionError(
                "Параметр 'depth' должен быть неотрицательным целым числом (0 = бесконечность)"
            )
        if type_filter not in ("all", "files", "folders"):
            raise CommandExecutionError(
                "Параметр 'type' должен быть одним из: all, files, folders"
            )

        items: List[str] = []
        errors: List[Dict[str, str]] = []

        for raw_path in paths:
            try:
                target = Path(raw_path)
                self._guard.check_access(target)

                if not target.exists():
                    errors.append({"path": raw_path, "error": "Папка не найдена"})
                    continue
                if not target.is_dir():
                    errors.append({"path": raw_path, "error": "Путь не является папкой"})
                    continue

                # Саму корневую папку включаем в результат (если фильтр позволяет)
                if type_filter in ("all", "folders"):
                    items.append(str(target.resolve()))

                self._walk(
                    directory=target,
                    current_depth=1,
                    max_depth=depth,
                    type_filter=type_filter,
                    items=items
                )
            except SecurityError as e:
                errors.append({"path": raw_path, "error": f"Доступ запрещён: {e}"})
            except Exception as e:
                errors.append({"path": raw_path, "error": str(e)})

        # Сортировка: папки перед файлами, внутри — по алфавиту (с учётом регистра)
        def sort_key(p: str):
            path_obj = Path(p)
            is_dir = path_obj.is_dir() if path_obj.exists() else False
            return (0 if is_dir else 1, p.lower())

        items.sort(key=sort_key)

        return {"items": items, "errors": errors}

    def _walk(
        self,
        directory: Path,
        current_depth: int,
        max_depth: int,
        type_filter: str,
        items: List[str]
    ) -> None:
        """Рекурсивный обход папки с контролем глубины и проверкой доступа."""
        # Если max_depth != 0 (не бесконечность) и мы вышли за пределы — стоп
        if max_depth != 0 and current_depth > max_depth:
            return

        try:
            entries = list(directory.iterdir())
        except PermissionError:
            return
        except Exception:
            return

        for entry in entries:
            # Проверка доступа для каждого вложенного элемента
            try:
                self._guard.check_access(entry)
            except SecurityError:
                continue  # пропускаем недоступные

            is_dir = entry.is_dir()
            is_file = entry.is_file()

            # Добавляем в результат согласно фильтру
            if type_filter == "all":
                items.append(str(entry.resolve()))
            elif type_filter == "files" and is_file:
                items.append(str(entry.resolve()))
            elif type_filter == "folders" and is_dir:
                items.append(str(entry.resolve()))

            # Рекурсия только в папки
            if is_dir:
                self._walk(entry, current_depth + 1, max_depth, type_filter, items)
