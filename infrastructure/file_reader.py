import os
from domain.interfaces import IFileReader
from domain.exceptions import DomainError

class FileReader(IFileReader):
    def read_text(self, path: str) -> str:
        if not os.path.isfile(path):
            raise DomainError(f"Файл не найден: {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise DomainError(f"Ошибка чтения файла: {e}")