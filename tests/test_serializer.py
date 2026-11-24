"""Тесты представления чисел, массивов и словарей в XML."""

import unittest
import xml.etree.ElementTree as ET

from config_converter.serializer import to_xml


class SerializerTests(unittest.TestCase):
    """Проверить структуру и форматирование XML."""

    def test_number_document(self) -> None:
        expected = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<config>\n"
            "  <number>42</number>\n"
            "</config>\n"
        )
        self.assertEqual(to_xml(42), expected)

    def test_empty_collections(self) -> None:
        root = ET.fromstring(to_xml([[], {}]))
        array = root.find("array")
        self.assertIsNotNone(array)
        self.assertIsNotNone(array.find("array"))
        self.assertIsNotNone(array.find("dictionary"))

    def test_nested_dictionary(self) -> None:
        value = {"items": [1, {"inner": [2]}]}
        root = ET.fromstring(to_xml(value))
        entry = root.find("dictionary/entry[@name='items']")
        self.assertIsNotNone(entry)
        number = entry.find("array/number")
        nested = entry.find("array/dictionary/entry[@name='inner']")
        self.assertEqual(number.text, "1")
        self.assertEqual(nested.find("array/number").text, "2")

    def test_xml_declaration_and_newline(self) -> None:
        result = to_xml({})
        self.assertTrue(result.startswith('<?xml version="1.0"'))
        self.assertTrue(result.endswith("\n"))

    def test_unsupported_type(self) -> None:
        with self.assertRaises(TypeError):
            to_xml("42")


if __name__ == "__main__":
    unittest.main()
