class DomainError(Exception):
    """Базовое исключение домена."""
    pass

class CommandNotFoundError(DomainError):
    """Команда не найдена в реестре."""
    pass

class CommandExecutionError(DomainError):
    """Ошибка при выполнении команды."""
    pass

class InvalidJsonError(DomainError):
    """Некорректный JSON."""
    pass