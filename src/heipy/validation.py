from lxml import etree as et

from heipy.parsers import HeiEditionsParser

    
def list_all_characters(input:str, input_type='path', resolve_entities = False) -> set:
    """
    Reads a string and returns a sorted set of unique characters found in the file,
    along with their Unicode code points.

    Args:
        input (str): The string to analyze or the path to the input text file.
        input_type(str): Is the input a path or a string? Values: 'str' or 'path' (default)

    Returns:
        set: A sorted set of tuples, where each tuple contains a character and its
                Unicode code point in the format 'U+XXXX'.
        set: A set of all the characters in the private use of unicode
    """
    result = set()
    private_use_chars = set()
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
    result = sorted(result, key=lambda x: x[1])

    return result, private_use_chars
