"""Тесты файлового преобразования и кодов завершения CLI."""

import io
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stderr
from pathlib import Path

from config_converter.cli import convert_file, main


class CliTests(unittest.TestCase):
    """Проверить успешные команды и обработку ошибок."""

    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self.directory = Path(self._temporary_directory.name)

    def write_source(self, source: str) -> Path:
        """Записать входной файл во временный каталог."""
        path = self.directory / "input.cfg"
        path.write_text(source, encoding="utf-8")
        return path

    def test_convert_file_creates_parent_directory(self) -> None:
        source = self.write_source("$[value: 42]")
        output = self.directory / "nested" / "result.xml"
        convert_file(source, output)
        root = ET.parse(output).getroot()
        entry = root.find("dictionary/entry[@name='value']")
        self.assertEqual(entry.find("number").text, "42")

    def test_main_with_long_options(self) -> None:
        source = self.write_source("var value = 7 {@(value)}")
        output = self.directory / "result.xml"
        code = main(["--input", str(source), "--output", str(output)])
        self.assertEqual(code, 0)
        self.assertIsNotNone(output.read_text(encoding="utf-8"))

    def test_main_with_short_options(self) -> None:
        source = self.write_source("{}")
        output = self.directory / "short.xml"
        code = main(["-i", str(source), "-o", str(output)])
        self.assertEqual(code, 0)
        self.assertTrue(output.exists())

    def test_syntax_error_returns_failure(self) -> None:
        source = self.write_source("$[broken:]")
        output = self.directory / "invalid.xml"
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = main(["-i", str(source), "-o", str(output)])
        self.assertEqual(code, 1)
        self.assertIn("Синтаксическая ошибка", errors.getvalue())
        self.assertFalse(output.exists())

    def test_unknown_constant_returns_failure(self) -> None:
        source = self.write_source("@(unknown)")
        output = self.directory / "unknown.xml"
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = main(["-i", str(source), "-o", str(output)])
        self.assertEqual(code, 1)
        self.assertIn("unknown", errors.getvalue())
        self.assertFalse(output.exists())

    def test_missing_input_returns_failure(self) -> None:
        source = self.directory / "missing.cfg"
        output = self.directory / "missing.xml"
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = main(["-i", str(source), "-o", str(output)])
        self.assertEqual(code, 1)
        self.assertIn("Ошибка", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
