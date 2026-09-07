import shutil
from pathlib import Path
from typing import Any, Dict
from jason.domain.interfaces import ICommandHandler
from jason.domain.exceptions import CommandExecutionError
from jasonutils.domain.interfaces import IPathSecurityGuard
from jasonutils.domain.value_objects import SearchOptions
from jasonutils.infrastructure.search_engine import SearchEngine

# ======================================================================
#  Создание файла
# ======================================================================
class CreateFileHandler(ICommandHandler):
    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("path")
        content = params.get("content", "")
        if not path:
            raise CommandExecutionError("Параметр 'path' обязателен")
        target = Path(path)
        self._guard.check_access(target)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"Файл создан: {target.resolve()}"
        except Exception as e:
            raise CommandExecutionError(f"Ошибка создания файла: {e}")

# ======================================================================
#  Изменение файла (полная перезапись)
# ======================================================================
class ModifyFileHandler(ICommandHandler):
    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("path")
        content = params.get("content")
        if not path or content is None:
            raise CommandExecutionError("Параметры 'path' и 'content' обязательны")
        target = Path(path)
        self._guard.check_access(target)
        try:
            target.write_text(content, encoding="utf-8")
            return f"Файл изменён: {target.resolve()}"
        except Exception as e:
            raise CommandExecutionError(f"Ошибка изменения файла: {e}")

# ======================================================================
#  Поиск и замена (с расширенными опциями)
# ======================================================================
class SearchReplaceHandler(ICommandHandler):
    def __init__(self, guard: IPathSecurityGuard, search_engine: SearchEngine = None):
        self._guard = guard
        self._engine = search_engine or SearchEngine()

    def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("path")
        search = params.get("search")
        replace = params.get("replace", "")

        if not path or search is None:
            raise CommandExecutionError("Параметры 'path' и 'search' обязательны")

        # Собираем Value Object с опциями поиска
        try:
            options = SearchOptions(
                regex=bool(params.get("regex", False)),
                case_sensitive=bool(params.get("case_sensitive", True)),
                whole_words=bool(params.get("whole_words", False)),
                max_matches=int(params.get("max_matches", 1)),
                direction=str(params.get("direction", "top_to_bottom"))
            )
        except (ValueError, TypeError) as e:
            raise CommandExecutionError(f"Некорректные параметры поиска: {e}")

        if options.max_matches < 0:
            raise CommandExecutionError("Параметр 'max_matches' не может быть отрицательным")
        if options.direction not in ("top_to_bottom", "bottom_to_top"):
            raise CommandExecutionError(
                "Параметр 'direction' должен быть 'top_to_bottom' или 'bottom_to_top'"
            )

        target = Path(path)
        self._guard.check_access(target)
        files = self._collect_files(target)
        count = 0
        for f in files:
            try:
                self._guard.check_access(f)
                text = f.read_text(encoding="utf-8")
                new_text, replacements = self._engine.replace(text, search, replace, options)
                if replacements > 0:
                    f.write_text(new_text, encoding="utf-8")
                    count += 1
            except UnicodeDecodeError:
                continue  # бинарный файл — пропускаем
            except Exception:
                continue  # нет доступа или другая ошибка — пропускаем

        # Если замен не произошло и цель — один файл, добавляем его содержимое в результат
        if count == 0 and target.is_file():
            try:
                content = target.read_text(encoding="utf-8")
                return {
                    "message": "Заменено файлов: 0",
                    "content": content,
                    "path": str(target.resolve())
                }
            except Exception:
                # Если не удалось прочитать, возвращаем только сообщение
                return "Заменено файлов: 0"
        else:
            return f"Заменено файлов: {count}"

    @staticmethod
    def _collect_files(target: Path):
        if target.is_file():
            return [target]
        if target.is_dir():
            return [f for f in target.rglob("*") if f.is_file()]
        raise CommandExecutionError(f"Путь не найден: {target}")

# ======================================================================
#  Удаление файла / папки
# ======================================================================
class DeleteFileHandler(ICommandHandler):
    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("path")
        if not path:
            raise CommandExecutionError("Параметр 'path' обязателен")
        target = Path(path)
        self._guard.check_access(target)
        try:
            if target.is_file():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
            else:
                raise CommandExecutionError(f"Путь не найден: {target}")
            return f"Удалено: {target.resolve()}"
        except CommandExecutionError:
            raise
        except Exception as e:
            raise CommandExecutionError(f"Ошибка удаления: {e}")

# ======================================================================
#  Копирование файла / папки
# ======================================================================
class CopyHandler(ICommandHandler):
    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        src = params.get("source")
        dst = params.get("destination")
        if not src or not dst:
            raise CommandExecutionError("Параметры 'source' и 'destination' обязательны")
        src_path = Path(src)
        dst_path = Path(dst)
        self._guard.check_access(src_path)
        self._guard.check_access(dst_path)
        if not src_path.exists():
            raise CommandExecutionError(f"Источник не найден: {src_path.resolve()}")
        try:
            if src_path.is_file():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
            elif src_path.is_dir():
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                raise CommandExecutionError(f"Неизвестный тип: {src_path}")
            return f"Скопировано: {src_path.resolve()} → {dst_path.resolve()}"
        except CommandExecutionError:
            raise
        except Exception as e:
            raise CommandExecutionError(f"Ошибка копирования: {e}")

# ======================================================================
#  Перенос (вырезание) файла / папки
# ======================================================================
class MoveHandler(ICommandHandler):
    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        src = params.get("source")
        dst = params.get("destination")
        if not src or not dst:
            raise CommandExecutionError("Параметры 'source' и 'destination' обязательны")
        src_path = Path(src)
        dst_path = Path(dst)
        self._guard.check_access(src_path)
        self._guard.check_access(dst_path)
        if not src_path.exists():
            raise CommandExecutionError(f"Источник не найден: {src_path.resolve()}")
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))
            return f"Перенесено: {src_path.resolve()} → {dst_path.resolve()}"
        except Exception as e:
            raise CommandExecutionError(f"Ошибка переноса: {e}")