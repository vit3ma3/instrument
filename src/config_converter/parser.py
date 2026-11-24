"""Грамматика и преобразование учебного языка во внутренние значения."""

from typing import TypeAlias, cast

from lark import Lark, Token, Transformer, UnexpectedInput

from config_converter.errors import (
    ConfigSyntaxError,
    DuplicateConstantError,
    DuplicateKeyError,
    UnknownConstantError,
)

ConfigValue: TypeAlias = int | list["ConfigValue"] | dict[str, "ConfigValue"]

GRAMMAR = r"""
start: const_decl* value
const_decl: "var" NAME "=" value
?value: number
      | array
      | dictionary
      | const_ref
number: NUMBER
array: "{" [value ("," value)*] "}"
dictionary: "$[" [entry ("," entry)*] "]"
entry: NAME ":" value
const_ref: "@(" NAME ")"
NUMBER: /\d+/
NAME: /[a-z]+/
%import common.WS
%ignore WS
"""


class ConfigTransformer(Transformer):
    """Построить значения Python и вычислить константы по месту разбора."""

    def __init__(self) -> None:
        """Создать пустое окружение констант."""
        super().__init__()
        self._constants: dict[str, ConfigValue] = {}

    def start(self, items: list[ConfigValue | None]) -> ConfigValue:
        """Вернуть итоговое значение после объявлений констант."""
        return cast(ConfigValue, items[-1])

    def number(self, items: list[Token]) -> int:
        """Преобразовать десятичный токен в целое число."""
        return int(items[0])

    def array(self, items: list[ConfigValue]) -> list[ConfigValue]:
        """Собрать массив, сохранив порядок элементов."""
        return list(items)

    def entry(self, items: list[object]) -> tuple[str, ConfigValue]:
        """Собрать пару имени и значения для словаря."""
        return str(items[0]), cast(ConfigValue, items[1])

    def dictionary(
        self,
        items: list[tuple[str, ConfigValue]],
    ) -> dict[str, ConfigValue]:
        """Собрать словарь и отклонить повторяющиеся ключи."""
        result: dict[str, ConfigValue] = {}
        for name, value in items:
            if name in result:
                raise DuplicateKeyError(name)
            result[name] = value
        return result

    def const_decl(self, items: list[object]) -> None:
        """Добавить константу в окружение после вычисления значения."""
        name = str(items[0])
        if name in self._constants:
            raise DuplicateConstantError(name)
        self._constants[name] = cast(ConfigValue, items[1])

    def const_ref(self, items: list[Token]) -> ConfigValue:
        """Подставить значение ранее объявленной константы."""
        name = str(items[0])
        if name not in self._constants:
            raise UnknownConstantError(name)
        return self._constants[name]


_PARSER = Lark(GRAMMAR, parser="lalr", lexer="contextual")


def parse_config(text: str) -> ConfigValue:
    """Разобрать текст, вычислить константы и вернуть итоговое значение."""
    try:
        tree = _PARSER.parse(text)
    except UnexpectedInput as error:
        expected = sorted(getattr(error, "expected", set()))
        raise ConfigSyntaxError(
            getattr(error, "line", None),
            getattr(error, "column", None),
            expected,
        ) from error
    result = ConfigTransformer().transform(tree)
    return cast(ConfigValue, result)
