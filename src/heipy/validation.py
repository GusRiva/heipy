from lxml import etree as et

from heipy.parsers import HeiEditionsParser

    
def list_all_characters(input:str, input_type='path', resolve_entities = False) -> tuple[list[tuple[str, str]], set[tuple[str, str, str]]]:
    """
    Reads a string and returns the unique characters found in the file,
    along with their Unicode code points.

    Args:
        input (str): The string to analyze or the path to the input text file.
        input_type(str): Is the input a path or a string? Values: 'str' or 'path' (default)

    Returns:
        tuple: A tuple of two items:
            list: The unique characters as tuples (character, code point in the format 'U+XXXX'),
                sorted by code point.
            set: The characters in the Unicode private use areas as tuples
                (character, code point, first 50 characters of the input).
    """
    result: set[tuple[str, str]] = set()
    private_use_chars: set[tuple[str, str, str]] = set()
    input_string = ''
    if input_type == 'str':
        input_string = input
    else:
        if resolve_entities:
            root = et.parse(input, parser=HeiEditionsParser(resolve_entities=resolve_entities))
            parsed_string = et.tostring(root, encoding='utf-8')
            input_string = parsed_string.decode('utf-8')
        else:
            with open(input, "r", encoding="utf-8") as f:
                input_string = f.read()
    for char in input_string:
        codepoint = ord(char)
        code_str = f"U+{codepoint:04X}"
        result.add((char, code_str ))
        if (
            0xE000 <= codepoint <= 0xF8FF or
            0xF0000 <= codepoint <= 0xFFFFD or
            0x100000 <= codepoint <= 0x10FFFD
        ):
            private_use_chars.add((char, code_str, input[:50]))
    return sorted(result, key=lambda x: x[1]), private_use_chars
