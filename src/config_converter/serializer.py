"""Преобразование внутренних значений конфигурации в XML."""

from xml.etree.ElementTree import Element, SubElement, indent, tostring

from config_converter.parser import ConfigValue


def _value_to_element(value: ConfigValue) -> Element:
    """Создать XML-элемент, соответствующий типу значения."""
    if isinstance(value, int):
        element = Element("number")
        element.text = str(value)
        return element
    if isinstance(value, list):
        element = Element("array")
        for item in value:
            element.append(_value_to_element(item))
        return element
    if isinstance(value, dict):
        element = Element("dictionary")
        for name, item in value.items():
            entry = SubElement(element, "entry", {"name": name})
            entry.append(_value_to_element(item))
        return element
    raise TypeError(f"Неподдерживаемый тип значения: {type(value).__name__}")


def to_xml(value: ConfigValue) -> str:
    """Вернуть значение в виде XML с корневым элементом config."""
    root = Element("config")
    root.append(_value_to_element(value))
    indent(root, space="  ")
    declaration = '<?xml version="1.0" encoding="utf-8"?>\n'
    return declaration + tostring(root, encoding="unicode") + "\n"
