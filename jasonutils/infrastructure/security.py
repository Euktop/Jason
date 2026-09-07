from pathlib import Path
from typing import List
from jasonutils.domain.interfaces import IPathSecurityGuard
from jasonutils.domain.exceptions import SecurityError


class PathSecurityGuard(IPathSecurityGuard):
    """
    Реализует логику Whitelist / Blacklist.
    Списки читаются из текстовых файлов (один путь на строку).
    Чёрный список имеет приоритет над белым.
    Поддерживает рекурсивное наследование для папок.
    Поддерживает hot-reload через reload().
    """

    def __init__(self, whitelist_path: str, blacklist_path: str):
        self._whitelist_file = Path(whitelist_path)
        self._blacklist_file = Path(blacklist_path)
        self._whitelist: List[Path] = []
        self._blacklist: List[Path] = []
        self.reload()

    # ------------------------------------------------------------------
    # Публичный API
    # ------------------------------------------------------------------

    def reload(self) -> None:
        """Перечитывает white_list.txt и black_list.txt."""
        self._whitelist = self._parse_list_file(self._whitelist_file)
        self._blacklist = self._parse_list_file(self._blacklist_file)

    def check_access(self, target_path: Path) -> None:
        resolved = target_path.resolve()

        # 1. Blacklist — абсолютный запрет
        for bl in self._blacklist:
            if resolved == bl or bl in resolved.parents:
                raise SecurityError(
                    f"Доступ запрещён (Blacklist): {resolved}"
                )

        # 2. Whitelist — если список не пуст, путь обязан быть внутри
        if self._whitelist:
            allowed = any(
                resolved == wl or wl in resolved.parents
                for wl in self._whitelist
            )
            if not allowed:
                raise SecurityError(
                    f"Доступ запрещён (не в Whitelist): {resolved}"
                )

    # ------------------------------------------------------------------
    # Приватные методы
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_list_file(file_path: Path) -> List[Path]:
        """
        Читает текстовый файл со списком путей.
        - Пустые строки игнорируются.
        - Строки, начинающиеся с '#', — комментарии.
        - Пути приводятся к абсолютным (resolve).
        """
        if not file_path.is_file():
            return []

        paths: List[Path] = []
        for raw_line in file_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            paths.append(Path(line).resolve())
        return paths