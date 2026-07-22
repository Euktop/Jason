from domain.interfaces import IFileReader
from adapters.json_parser import JsonCommandParser
from application.dtos import CommandRequest

class FileCommandLoader:
    def __init__(self, file_reader: IFileReader, parser: JsonCommandParser):
        self._file_reader = file_reader
        self._parser = parser

    def load(self, path: str) -> CommandRequest:
        content = self._file_reader.read_text(path)
        return self._parser.parse(content)