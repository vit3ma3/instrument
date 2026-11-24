"""Тесты грамматики, вложенных значений и вычисления констант."""

import unittest

from config_converter.errors import (
    ConfigSyntaxError,
    DuplicateConstantError,
    DuplicateKeyError,
    UnknownConstantError,
)
from config_converter.parser import parse_config


class ParserTests(unittest.TestCase):
    """Проверить все конструкции учебного языка."""

    def test_number(self) -> None:
        self.assertEqual(parse_config("12345"), 12345)

    def test_array_preserves_order(self) -> None:
        self.assertEqual(parse_config("{1, 2, 3}"), [1, 2, 3])

    def test_empty_array(self) -> None:
        self.assertEqual(parse_config("{}"), [])

    def test_dictionary(self) -> None:
        result = parse_config("$[first: 1, second: 2]")
        self.assertEqual(result, {"first": 1, "second": 2})

    def test_empty_dictionary(self) -> None:
        self.assertEqual(parse_config("$[]"), {})

    def test_deeply_nested_values(self) -> None:
        source = "$[items: {1, {2, $[inner: {3}]}}]"
        expected = {"items": [1, [2, {"inner": [3]}]]}
        self.assertEqual(parse_config(source), expected)

    def test_constant_declaration(self) -> None:
        self.assertEqual(parse_config("var answer = 42 @(answer)"), 42)

    def test_constant_in_declaration(self) -> None:
        source = "var first = 10 var second = @(first) @(second)"
        self.assertEqual(parse_config(source), 10)

    def test_array_constant(self) -> None:
        source = "var ports = {80, 443} $[ports: @(ports)]"
        self.assertEqual(parse_config(source), {"ports": [80, 443]})

    def test_dictionary_constant(self) -> None:
        source = "var limits = $[rate: 20] {1, @(limits)}"
        self.assertEqual(parse_config(source), [1, {"rate": 20}])

    def test_constants_in_nested_values(self) -> None:
        source = """
            var timeout = 30
            var retry = 3
            $[server: $[limits: {@(timeout), @(retry)}]]
        """
        expected = {"server": {"limits": [30, 3]}}
        self.assertEqual(parse_config(source), expected)

    def test_unknown_constant(self) -> None:
        with self.assertRaises(UnknownConstantError):
            parse_config("@(missing)")

    def test_forward_constant_reference(self) -> None:
        source = "var first = @(second) var second = 2 @(first)"
        with self.assertRaises(UnknownConstantError):
            parse_config(source)

    def test_duplicate_constant(self) -> None:
        source = "var value = 1 var value = 2 @(value)"
        with self.assertRaises(DuplicateConstantError):
            parse_config(source)

    def test_duplicate_dictionary_key(self) -> None:
        with self.assertRaises(DuplicateKeyError):
            parse_config("$[value: 1, value: 2]")

    def test_invalid_syntax(self) -> None:
        cases = (
            "",
            "-1",
            "$[Key: 1]",
            "{1 2}",
            "$[value: 1",
            "@(missing)",
            "{1,}",
            "1 2",
        )
        for source in cases:
            with self.subTest(source=source):
                if source == "@(missing)":
                    with self.assertRaises(UnknownConstantError):
                        parse_config(source)
                else:
                    with self.assertRaises(ConfigSyntaxError):
                        parse_config(source)

    def test_syntax_error_contains_location(self) -> None:
        with self.assertRaises(ConfigSyntaxError) as context:
            parse_config("$[first: 1,\nsecond 2]")
        self.assertEqual(context.exception.line, 2)
        self.assertIsNotNone(context.exception.column)
        self.assertTrue(context.exception.expected)


if __name__ == "__main__":
    unittest.main()
