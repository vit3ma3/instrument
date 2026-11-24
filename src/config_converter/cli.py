"""Интерфейс командной строки для преобразования файлов в XML."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from config_converter.errors import ConfigError
from config_converter.parser import parse_config
from config_converter.serializer import to_xml


def build_argument_parser() -> argparse.ArgumentParser:
    """Создать разборщик аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="config2xml",
        description="Преобразовать учебную конфигурацию в XML.",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="путь к файлу в учебном конфигурационном языке",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="путь к создаваемому XML-файлу",
    )
    return parser


def convert_file(input_path: Path, output_path: Path) -> None:
    """Прочитать конфигурацию и записать результат преобразования."""
    source = input_path.read_text(encoding="utf-8")
    value = parse_config(source)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(to_xml(value), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    """Выполнить команду и вернуть код завершения процесса."""
    args = build_argument_parser().parse_args(argv)
    try:
        convert_file(args.input, args.output)
    except (ConfigError, OSError, UnicodeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0
