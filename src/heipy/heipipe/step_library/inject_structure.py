from lxml import etree as et
import re

from ..steps import PythonStep
from ...namespaces import ns, tei_ns, xml_ns
from ...colors import RED, RESET


def inject_structure_func(tree: et.ElementTree, parameters=None):
    """
    Inject div structure into TEI document based on a structure configuration file.

    The structure file defines the new structure (front/body/back with divs).
    Content elements (lg, l, p, ab, etc.) are collected from the source by xml:id
    and placed into the new structure according to ptr ranges.

    Parameters:
        tree: The ElementTree of the TEI document
        parameters: Dictionary containing 'structure_file_path' key with path to structure XML

    Returns:
        Modified ElementTree with div structure injected
    """
    root = tree.getroot()
    if isinstance(parameters, list) and len(parameters) > 0:
        if len(parameters) > 0:
            parameters = {k: v for d in parameters for k, v in d.items()}
        else:
            parameters = None

    if parameters is None or 'structure_file_path' not in parameters:
        raise ValueError(f"{RED}Missing required parameter 'structure_file_path'{RESET}")

    structure_file_path = parameters['structure_file_path']

    # Parse the structure configuration file
    try:
        structure_tree = et.parse(structure_file_path)
        structure_root = structure_tree.getroot()
    except Exception as e:
        raise ValueError(f"{RED}Error parsing structure file {structure_file_path}: {e}{RESET}")

    # Get the text element from structure file
    structure_text = structure_root.xpath("//tei:text", namespaces=ns)
    if not structure_text:
        raise ValueError(f"{RED}No text element found in structure file{RESET}")
    structure_text = structure_text[0]

    # Find the text element in the source document
    source_text = root.xpath("//tei:text", namespaces=ns)
    if not source_text:
        raise ValueError(f"{RED}No text element found in source document{RESET}")
    source_text = source_text[0]
    
    # Remove old front, body, back from source text
    et.strip_tags(source_text, [tei_ns / x for x in 
                   ["front", "body", "back", "div"]])
    

    # Create index of all elements with xml:id for fast lookup
    id_index = {}
    for elem in root.iter():
        if elem.tag == tei_ns / 'w':
            continue
        xml_id = elem.get(xml_ns / "id")
        if xml_id:
            id_index[xml_id] = elem

    # Build new structure from the structure file
    new_structure_elements = []
    for child in structure_text:
        tag_name = child.tag
        if tag_name in [tei_ns / "front",
                        tei_ns / "body",
                        tei_ns / "back"]:
            new_element = build_structural_element(child, root, id_index)
            if new_element is not None:
                new_structure_elements.append(new_element)

    # Add new structure elements
    for elem in new_structure_elements:
        source_text.append(elem)

    
    # Manage the pb / cb / lb outside divs
    pbs_outside_div = source_text.xpath(".//tei:pb[not(ancestor::tei:div)]", namespaces=ns)
    for pb_outside_div in pbs_outside_div:
        for following_el in pb_outside_div.xpath('.//following::tei:div', namespaces=ns):
            if following_el.tag == tei_ns / 'div':
                following_el.insert(0, pb_outside_div)
                break


    return tree


def build_structural_element(structure_elem, source_root, id_index):
    """
    Build a structural element (front, body, or back) based on the structure configuration.

    Parameters:
        structure_elem: The front/body/back element from structure file
        source_root: The root of the source document
        id_index: Dictionary mapping xml:id to elements

    Returns:
        A new front/body/back element with complete structure
    """
    # Create new element with same tag
    new_elem = et.Element(structure_elem.tag)

    # Copy attributes
    for attr_name, attr_value in structure_elem.attrib.items():
        new_elem.set(attr_name, attr_value)

    # Process children
    for child in structure_elem:
        if child.tag == "{http://www.tei-c.org/ns/1.0}div":
            new_div = build_div_with_content(child, source_root, id_index)
            if new_div is not None:
                new_elem.append(new_div)

    return new_elem


def build_div_with_content(structure_div, source_root, id_index):
    """
    Build a single div element with its content from the source document.

    Parameters:
        structure_div: The div element from the structure configuration
        source_root: The root element of the source TEI document
        id_index: Dictionary mapping xml:id to elements

    Returns:
        A new div element with content, or None if there was an error
    """
    # Create new div element
    new_div = et.Element("{http://www.tei-c.org/ns/1.0}div")

    # Copy attributes
    for attr_name, attr_value in structure_div.attrib.items():
        new_div.set(attr_name, attr_value)

    # Add head element if present
    head_elements = structure_div.xpath("tei:head", namespaces=ns)
    if head_elements:
        new_head = copy_element(head_elements[0])
        new_div.append(new_head)

    # Check if this div has child divs
    child_divs = structure_div.xpath("tei:div", namespaces=ns)

    if child_divs:
        # This div has nested divs - process them recursively
        for child_div in child_divs:
            nested_div = build_div_with_content(child_div, source_root, id_index)
            if nested_div is not None:
                new_div.append(nested_div)
    else:
        # This is a leaf div - get content from ptr element
        ptr_elements = structure_div.xpath("tei:ptr", namespaces=ns)
        if ptr_elements:
            ptr_target = ptr_elements[0].get("target")
            if ptr_target:
                # Parse range from ptr/@target
                range_match = re.search(r'range\(([^,]+),([^)]+)\)', ptr_target)
                if range_match:
                    start_id = range_match.group(1).strip()
                    end_id = range_match.group(2).strip()
                    # Collect elements from source
                    elements = collect_elements_from_range(start_id, end_id, id_index)
                    for elem in elements:
                        new_div.append(elem)

    return new_div


def collect_elements_from_range(start_id, end_id, id_index):
    """
    Collect sibling elements between start_id and end_id (inclusive).

    Parameters:
        start_id: xml:id of the first element
        end_id: xml:id of the last element
        id_index: Dictionary mapping xml:id to elements (for fast O(1) lookup)

    Returns:
        List of sibling elements (removed from their parent)
    """
    # Find start and end elements using index (fast O(1) lookup)
    start_element = id_index.get(start_id)
    if start_element is None:
        print(f"{RED}Warning: Could not find start element with xml:id='{start_id}'{RESET}")
        return []

    end_element = id_index.get(end_id)
    if end_element is None:
        print(f"{RED}Warning: Could not find end element with xml:id='{end_id}'{RESET}")
        return []

    # Get parent - they should be siblings
    parent = start_element.getparent()
    if parent is None:
        print(f"{RED}Warning: Start element has no parent{RESET}")
        return []
    
    if end_element.getparent() != parent:
        print(f"{RED}Warning: Start and end elements are not siblings{RESET}")
        return []

    # Find indices in parent
    start_idx = parent.index(start_element)
    end_idx = parent.index(end_element)

    if start_idx > end_idx:
        print(f"{RED}Warning: Start element comes after end element{RESET}")
        return []

    # Collect siblings from parent
    collected = []
    for _ in range(start_idx, end_idx + 1):
        # Always take at start_idx since we're removing
        elem = parent[start_idx]
        parent.remove(elem)
        collected.append(elem)

    return collected


def copy_element(element):
    """
    Create a deep copy of an element.

    Parameters:
        element: The element to copy

    Returns:
        A deep copy of the element
    """
    return et.fromstring(et.tostring(element))


def get_step():
    return PythonStep(funct=inject_structure_func, name="inject_structure")
