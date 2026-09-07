class DomainError(Exception):
    """Базовое исключение домена."""
    pass

class SourceError(DomainError):
    """Ошибка при загрузке команд из источника."""
    pass

class ValidationError(DomainError):
    """Ошибка валидации команды."""
    pass

class ExecutionError(DomainError):
    """Ошибка выполнения команды."""
    pass

class SecurityError(DomainError):
    """Ошибка нарушения правил безопасности (доступ к пути запрещен)."""
    pass