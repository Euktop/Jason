from domain.interfaces import IOutput

class ConsoleOutput(IOutput):
    def write(self, message: str) -> None:
        print(message)