
    
def list_all_characters(input:str) -> set:
    """
    Reads a string and returns a sorted set of unique characters found in the file,
    along with their Unicode code points.

    Args:
        input_file (str): The path to the input text file.

    Returns:
        set: A sorted set of tuples, where each tuple contains a character and its
                Unicode code point in the format 'U+XXXX'.
    """
    result = set()
    for char in input:
        result.add((char, f"U+{ord(char):04X}" ))
    result = sorted(result, key=lambda x: x[1])

    return result
