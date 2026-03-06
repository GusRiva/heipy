from .parsers import heiparse
from .namespaces import ns
from pathlib import Path
import importlib.resources
import re
from typing import Dict

def create_configuration_json(input_files:list)->dict:
    output_dict = {}
    for file_name in input_files:
        file_dict = {}
        file_path = Path(file_name)
        if not file_path.exists():
            print(f"There is an error, can not find file {file_path}")
            continue
        input_tree = heiparse(file_path)
        siglum_el = input_tree.find('.//tei:idno[@ana="hc:EditorialSiglum"]', ns)
        siglum = ''
        if siglum_el is None:
            print(f"No siglum defined for {file_path}. Use idno with @ana='hc:EditorialSiglum' in the witness description.")
        else:
            siglum = siglum_el.text
        file_dict['siglum'] = siglum
        
        output_dict[file_name] = file_dict

    return


def _get_entity_declarations() -> Dict[str, str]:
    """
    Loads and parses entity declarations from the local heiEDITIONS file.

    Returns:
        Dictionary with resolved strings as keys and entity names as values
    """
    # Use local entity file from heipy
    with importlib.resources.path('heipy.schema', 'heieditions-entities.txt') as heipy_entity_file:
        with open(heipy_entity_file, 'r', encoding='utf-8') as f:
            declaration_body = f.read()

    entities = {}

    # Regex Patterns
    pattern_entity = re.compile(r'!ENTITY (\w+) "(.+)"')
    pattern_codepoint = re.compile(r'&#x([\da-fA-F]+);')
    pattern_g_content = re.compile(r'(<g.*?>)(.+)(</g>)')

    # Iterate over all entity declarations
    for match in pattern_entity.finditer(declaration_body):
        entity_name = match.group(1)
        entity_expanded = match.group(2)

        # For entities that are expanded with a G element
        if entity_expanded.startswith('<g'):
            g_match = pattern_g_content.search(entity_expanded)
            if g_match:
                g_opening = g_match.group(1)
                g_content = g_match.group(2)
                g_closing = g_match.group(3)

                # Extract hexadecimal codepoint from G element content
                codepoint_match = pattern_codepoint.search(g_content)
                if codepoint_match:
                    codepoint_string = codepoint_match.group(1)
                    codepoint = int(codepoint_string, 16)
                    character = chr(codepoint)

                    # Assemble the G element with the expanded character
                    string_with_single_quotes = g_opening + character + g_closing
                    # Replace single quotes with double quotes for XML attributes
                    string_with_double_quotes = string_with_single_quotes.replace("'", '"')

                    entities[string_with_double_quotes] = entity_name
        else:
            # For entities that are expanded directly with a hexadecimal codepoint
            codepoint_match = pattern_codepoint.search(entity_expanded)
            if codepoint_match:
                codepoint_string = codepoint_match.group(1)
                codepoint = int(codepoint_string, 16)
                character = chr(codepoint)
                entities[character] = entity_name

    return entities


def _build_replacement_regex(entities: Dict[str, str]) -> re.Pattern:
    """
    Creates a regex pattern that matches all resolved entities and individual characters.

    Args:
        entities: Dictionary with resolved strings and entity names

    Returns:
        Compiled regex pattern
    """
    # Sort by length (longest first) to guarantee correct matches
    sorted_keys = sorted(entities.keys(), key=len, reverse=True)

    # Escape special regex characters
    escaped_keys = [re.escape(key) for key in sorted_keys]

    # Add pattern for individual characters at the end
    regex_string = '|'.join(escaped_keys) + r'|(.)'

    return re.compile(regex_string)


def restore_entities(source_file: str, target_file: str) -> None:
    """
    Restores XML entities that were resolved after an XSLT transformation.

    This function loads the entity definitions from the local heiEDITIONS file and
    replaces the resolved characters and G elements back into their original entity form.

    Args:
        source_file: Path to input file (with resolved entities)
        target_file: Path to output file (with restored entities)

    Example:
        >>> from heipy.editions_utils import restore_entities
        >>> restore_entities('data/input.xml', 'data/output.xml')
    """
    # DTD declaration to be inserted
    DTD = """<!DOCTYPE TEI SYSTEM "https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/declarations/heieditions-entities.txt">"""

    # Load entity declarations
    entity_declarations = _get_entity_declarations()

    # Create replacement regex
    all_regex_pattern = _build_replacement_regex(entity_declarations)
    
    # Process the file
    with open(source_file, 'r', encoding='utf-8') as source:
        with open(target_file, 'w', encoding='utf-8') as target:
            header_written = False
            for line in source:
                line_string = line.rstrip('\n')

                # Skip lines before <TEI xmlns
                if not header_written:
                    if '<TEI xmlns' not in line_string:
                        continue
                    # Write header when we reach TEI
                    target.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                    target.write('<?xml-model href="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/tei_hes.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>\n')
                    target.write('<?xml-model href="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/tei_hes.rng" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>\n')
                    target.write(DTD + '\n')
                    target.write('<TEI' + line_string.split("<TEI",1)[1] + '\n')
                    header_written = True
                    continue

                # Replace all matches in the line
                result_parts = []
                for match in all_regex_pattern.finditer(line_string):
                    matched_text = match.group(0)
                    # If the match corresponds to a resolved entity
                    if matched_text in entity_declarations:
                        result_parts.append(f"&{entity_declarations[matched_text]};")
                    else:
                        # Otherwise keep unchanged
                        result_parts.append(matched_text)

                new_line = ''.join(result_parts)
                target.write(new_line + '\n')
