"""Проверка двух полноценных конфигураций из разных предметных областей."""

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from config_converter.parser import parse_config
from config_converter.serializer import to_xml

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


class ExampleTests(unittest.TestCase):
    """Разобрать примеры и проверить вычисленные константы."""

    def parse_example(self, name: str):
        """Прочитать и разобрать пример из каталога examples."""
        source = (EXAMPLES_DIR / name).read_text(encoding="utf-8")
        return parse_config(source)

    def test_webserver_configuration(self) -> None:
        result = self.parse_example("webserver.cfg")
        server = result["server"]
        self.assertEqual(server["ports"], [8080, 8443])
        self.assertEqual(server["limits"]["timeout"], 30)
        self.assertEqual(len(result["nodes"]), 2)

    def test_library_configuration(self) -> None:
        result = self.parse_example("library.cfg")
        self.assertEqual(result["library"]["categories"], [101, 102, 103])
        for room in result["rooms"]:
            self.assertEqual(room["loandays"], 14)

    def test_examples_produce_valid_xml(self) -> None:
        for path in sorted(EXAMPLES_DIR.glob("*.cfg")):
            with self.subTest(example=path.name):
                value = self.parse_example(path.name)
                root = ET.fromstring(to_xml(value))
                self.assertEqual(root.tag, "config")
                self.assertIsNotNone(root.find("dictionary"))


if __name__ == "__main__":
    unittest.main()
