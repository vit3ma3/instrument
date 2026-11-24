"""Исключения, возникающие при обработке конфигурации."""


class ConfigError(Exception):
    """Базовый класс ошибок конфигурации."""


class ConfigSyntaxError(ConfigError):
    """Синтаксическая ошибка с координатами и ожидаемыми токенами."""

    def __init__(
        self,
        line: int | None,
        column: int | None,
        expected: list[str],
    ) -> None:
        """Сформировать сообщение об ошибке разбора."""
        self.line = line
        self.column = column
        self.expected = expected
        location = f"строка {line or '?'}, столбец {column or '?'}"
        message = f"Синтаксическая ошибка: {location}."
        if expected:
            message += f" Ожидалось: {', '.join(expected)}."
        super().__init__(message)


class UnknownConstantError(ConfigError):
    """Использование константы до её объявления."""

    def __init__(self, name: str) -> None:
        """Сохранить имя неизвестной константы."""
        self.name = name
        message = f"Константа '{name}' не объявлена перед использованием."
        super().__init__(message)


class DuplicateConstantError(ConfigError):
    """Повторное объявление константы."""

    def __init__(self, name: str) -> None:
        """Сохранить имя повторно объявленной константы."""
        self.name = name
        super().__init__(f"Константа '{name}' уже объявлена.")


class DuplicateKeyError(ConfigError):
    """Повторное использование имени в одном словаре."""

    def __init__(self, name: str) -> None:
        """Сохранить имя повторного ключа."""
        self.name = name
        super().__init__(f"Ключ '{name}' повторяется в словаре.")
