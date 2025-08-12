import codecs
    
def list_all_characters(input:str, input_type='path') -> set:
    """
    Reads a string and returns a sorted set of unique characters found in the file,
    along with their Unicode code points.

    Args:
        input (str): The string to analyze or the path to the input text file.
        input_type(str): Is the input a path or a string? Values: 'str' or 'path' (default)

    Returns:
        set: A sorted set of tuples, where each tuple contains a character and its
                Unicode code point in the format 'U+XXXX'.
    """
    result = set()
    input_string = ''
    if input_type == 'str':
        input_string = input
    else:
        with codecs.open(input, 'r', 'utf-8') as input_file:
            input_string = input_file.read()
    for char in input_string:
        result.add((char, f"U+{ord(char):04X}" ))
    result = sorted(result, key=lambda x: x[1])

    return result
