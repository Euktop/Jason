import re
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from jason.domain.interfaces import ICommandHandler
from jason.domain.exceptions import CommandExecutionError
from jasonutils.domain.interfaces import IPathSecurityGuard
from jasonutils.infrastructure.jason_adapter import JasonCommandExecutor


# ----------------------------------------------------------------------
# 1. set_frontmatter
# ----------------------------------------------------------------------
class SetFrontmatterHandler(ICommandHandler):
    """
    Добавляет или обновляет поля в frontmatter (YAML-блок в начале файла).
    Если frontmatter отсутствует – создаёт его.
    """

    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("path")
        fields = params.get("fields", {})
        if not path or not fields:
            raise CommandExecutionError("Параметры 'path' и 'fields' обязательны")

        target = Path(path)
        self._guard.check_access(target)

        if not target.exists():
            raise CommandExecutionError(f"Файл не найден: {target}")

        # Читаем содержимое
        content = target.read_text(encoding="utf-8")
        frontmatter, body = self._split_frontmatter(content)

        # Обновляем поля
        frontmatter.update(fields)
        new_content = self._build_content(frontmatter, body)

        target.write_text(new_content, encoding="utf-8")
        return f"Frontmatter обновлён для {target.resolve()}"

    @staticmethod
    def _split_frontmatter(content: str) -> tuple[dict, str]:
        """Возвращает (frontmatter_dict, тело_без_frontmatter)."""
        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                raw = parts[1]
                body = parts[2]
                try:
                    data = yaml.safe_load(raw) or {}
                except yaml.YAMLError:
                    data = {}
                return data, body
        # Нет frontmatter
        return {}, content

    @staticmethod
    def _build_content(frontmatter: dict, body: str) -> str:
        if not frontmatter:
            return body
        raw = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return f"---\n{raw}---\n{body.lstrip()}"


# ----------------------------------------------------------------------
# 2. insert_line
# ----------------------------------------------------------------------
class InsertLineHandler(ICommandHandler):
    """
    Вставляет одну или несколько строк до или после первого вхождения шаблона.
    Шаблон может быть строкой или регулярным выражением (если начинается и заканчивается '/').
    """

    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("path")
        anchor = params.get("anchor")
        position = params.get("position", "after")
        lines = params.get("lines", [])

        if not path or anchor is None or not lines:
            raise CommandExecutionError(
                "Параметры 'path', 'anchor' и 'lines' обязательны"
            )

        target = Path(path)
        self._guard.check_access(target)
        if not target.exists():
            raise CommandExecutionError(f"Файл не найден: {target}")

        content = target.read_text(encoding="utf-8")

        # Определяем, является ли anchor регулярным выражением
        if anchor.startswith('/') and anchor.endswith('/'):
            pattern = re.compile(anchor[1:-1], re.MULTILINE)
        else:
            pattern = re.compile(re.escape(anchor), re.MULTILINE)

        match = pattern.search(content)
        if not match:
            raise CommandExecutionError(f"Шаблон '{anchor}' не найден в файле")

        insert_text = "\n".join(lines)
        if position == "before":
            new_content = content[:match.start()] + insert_text + "\n" + content[match.start():]
        elif position == "after":
            new_content = content[:match.end()] + "\n" + insert_text + content[match.end():]
        else:
            raise CommandExecutionError("position должно быть 'before' или 'after'")

        target.write_text(new_content, encoding="utf-8")
        return f"Вставлено в {target.resolve()} ({position} '{anchor}')"


# ----------------------------------------------------------------------
# 3. append_to_list
# ----------------------------------------------------------------------
class AppendToListHandler(ICommandHandler):
    """
    Добавляет элемент в конец маркированного, нумерованного или чек-листа
    под указанным заголовком (или в любом месте, если section не задан).
    """

    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("path")
        section = params.get("section")  # опционально
        item = params.get("item")
        if not path or not item:
            raise CommandExecutionError("Параметры 'path' и 'item' обязательны")

        target = Path(path)
        self._guard.check_access(target)
        if not target.exists():
            raise CommandExecutionError(f"Файл не найден: {target}")

        content = target.read_text(encoding="utf-8")

        # Если указан section, ищем его; иначе работаем со всем содержимым
        if section:
            # Ищем заголовок (линия начинается с #)
            pattern = re.compile(r'^(#+)\s*' + re.escape(section) + r'\s*$', re.MULTILINE)
            match = pattern.search(content)
            if not match:
                raise CommandExecutionError(f"Заголовок '{section}' не найден")
            start = match.end()
            # Ищем следующий заголовок того же или более высокого уровня (меньше #)
            level = len(match.group(1))
            next_header = re.compile(r'^#{1,' + str(level) + r'}\s+', re.MULTILINE)
            next_match = next_header.search(content, start)
            end = next_match.start() if next_match else len(content)
            block = content[start:end]
        else:
            block = content
            start = 0
            end = len(content)

        # Ищем последний элемент списка в этом блоке
        # Список: строки, начинающиеся с пробелов, затем маркер (-, *, +, цифра., - [ ])
        list_pattern = re.compile(r'^(\s*)([-*+]|\d+\.|-\s*\[[ xX]\])', re.MULTILINE)
        matches = list_pattern.finditer(block)
        last_match = None
        for m in matches:
            last_match = m

        if not last_match:
            raise CommandExecutionError("Список не найден в указанном блоке")

        # Определяем отступ и маркер для нового элемента
        indent = last_match.group(1)  # пробелы
        marker = last_match.group(2)
        # Определяем базовый отступ для единообразия
        if marker.startswith('- [') or marker.startswith('+ ['):
            # чек-лист, сохраняем маркер как есть
            new_item = f"{indent}- [ ] {item.lstrip()}"  # можно сделать пустой чекбокс, но можно и с переданным item
            # Если item уже содержит маркер, используем его как есть
            if item.lstrip().startswith('-'):
                new_item = indent + item.lstrip()
            else:
                new_item = f"{indent}- {item.lstrip()}"
        elif marker in ('-', '*', '+'):
            new_item = f"{indent}- {item.lstrip()}"
        elif marker[0].isdigit():
            # нумерованный список – берём число и увеличиваем на 1
            num = int(re.search(r'\d+', marker).group())
            new_marker = str(num + 1) + '.'
            new_item = f"{indent}{new_marker} {item.lstrip()}"
        else:
            new_item = f"{indent}- {item.lstrip()}"

        # Вставляем после последнего найденного элемента
        pos = last_match.end()
        # Добавляем перевод строки, если его нет
        insert_pos = start + pos
        new_content = content[:insert_pos] + "\n" + new_item + content[insert_pos:]

        target.write_text(new_content, encoding="utf-8")
        return f"Элемент добавлен в список в {target.resolve()}"


# ----------------------------------------------------------------------
# 4. touch
# ----------------------------------------------------------------------
class TouchHandler(ICommandHandler):
    """
    Обновляет поле 'updated' в frontmatter на текущую дату (или указанную).
    Если поля нет – создаёт.
    """

    def __init__(self, guard: IPathSecurityGuard):
        self._guard = guard

    def execute(self, params: Dict[str, Any]) -> Any:
        path = params.get("path")
        date_str = params.get("date")  # опционально
        if not path:
            raise CommandExecutionError("Параметр 'path' обязателен")

        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        # Используем SetFrontmatterHandler для обновления
        set_handler = SetFrontmatterHandler(self._guard)
        return set_handler.execute({
            "path": path,
            "fields": {"updated": date_str}
        })


# ----------------------------------------------------------------------
# 5. glob
# ----------------------------------------------------------------------
class GlobHandler(ICommandHandler):
    """
    Применяет набор команд ко всем файлам, соответствующим шаблону (glob).
    Команды внутри не должны содержать ключ 'path' – он подставляется автоматически.
    """

    def __init__(self, guard: IPathSecurityGuard, jason_executor: JasonCommandExecutor):
        self._guard = guard
        self._executor = jason_executor

    def execute(self, params: Dict[str, Any]) -> Any:
        pattern = params.get("pattern")
        commands = params.get("commands", [])
        if not pattern or not commands:
            raise CommandExecutionError("Параметры 'pattern' и 'commands' обязательны")

        # Проверяем доступ к корневому каталогу шаблона
        root = Path(pattern).resolve().parent
        self._guard.check_access(root)

        # Находим все файлы по шаблону
        import glob
        files = glob.glob(pattern, recursive=True)
        if not files:
            return f"Файлы по шаблону '{pattern}' не найдены"

        results = []
        for file_path in files:
            file_res = []
            for cmd in commands:
                # Копируем команду и добавляем/заменяем path
                cmd_copy = cmd.copy()
                if "params" not in cmd_copy:
                    cmd_copy["params"] = {}
                cmd_copy["params"]["path"] = file_path
                # Выполняем команду
                try:
                    # Преобразуем словарь в CommandPayload (можно напрямую через адаптер)
                    from jasonutils.domain.entities import CommandPayload
                    payload = CommandPayload(name=cmd_copy["command"], params=cmd_copy["params"])
                    res = self._executor.execute(payload)
                    file_res.append({
                        "file": file_path,
                        "command": cmd_copy["command"],
                        "result": res,
                        "error": None
                    })
                except Exception as e:
                    file_res.append({
                        "file": file_path,
                        "command": cmd_copy["command"],
                        "result": None,
                        "error": str(e)
                    })
            results.append(file_res)

        return results