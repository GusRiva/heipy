"""
XML comparison utilities for heipy tests.

IMPORTANT: These utilities PRESERVE WHITESPACE by default, as whitespace
is semantically significant in TEI documents for digital scholarly editing.

Element-based comparison (compares parsed XML trees):
- xml_equal(): Compare two XML trees for equality
- xml_diff(): Generate a detailed diff between two XML trees
- assert_xml_equal(): Assert XML equality with detailed error messages
- assert_xml_structure_equal(): Compare structure only (ignore text content)
- assert_xml_contains(): Check if XML fragment is contained in another

Text-based comparison (compares serialized XML text):
- normalize_prologue(): Normalize XML prologue formatting
- xml_to_comparable_text(): Convert XML to text for comparison
- text_equal(): Compare two XML documents as text strings
- assert_text_equal(): Assert text equality with detailed diff

Utilities:
- normalize_for_comparison(): Optional normalization (use sparingly)
- get_xpath_to_element(): Generate XPath to locate an element
"""

from lxml import etree as et
from heipy.heipipe.steps import Pipeline
from typing import Union, Optional, Tuple, Literal
from pathlib import Path
from difflib import unified_diff
import re
import codecs


# Type alias for XML inputs
XMLInput = Union[et._Element, et._ElementTree, str, bytes]


def _to_element(xml_input: XMLInput) -> et._Element:
    """
    Convert various XML input types to lxml Element.

    Args:
        xml_input: XML as Element, ElementTree, string, or bytes

    Returns:
        lxml Element

    Raises:
        TypeError: If input type is not supported
    """
    if isinstance(xml_input, et._Element):
        return xml_input
    elif isinstance(xml_input, et._ElementTree):
        return xml_input.getroot()
    elif isinstance(xml_input, str):
        return et.fromstring(xml_input.encode("utf-8"))
    elif isinstance(xml_input, bytes):
        return et.fromstring(xml_input)
    else:
        raise TypeError(f"Unsupported XML input type: {type(xml_input)}")


def _elements_equal(
    e1: et._Element, e2: et._Element, ignore_attribute_order: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Recursively compare two XML elements for equality.

    PRESERVES WHITESPACE - text and tail are compared exactly as-is.

    Args:
        e1: First element
        e2: Second element
        ignore_attribute_order: Whether to ignore the order of attributes

    Returns:
        Tuple of (equal: bool, difference_message: str or None)
    """
    # Compare tags
    if e1.tag != e2.tag:
        return False, f"Tag mismatch: {e1.tag} != {e2.tag}"

    # Compare text (EXACT comparison, whitespace matters)
    if e1.text != e2.text:
        return False, f"Text mismatch in <{e1.tag}>: {repr(e1.text)} != {repr(e2.text)}"

    # Compare tail (EXACT comparison, whitespace matters)
    if e1.tail != e2.tail:
        return (
            False,
            f"Tail mismatch after <{e1.tag}>: {repr(e1.tail)} != {repr(e2.tail)}",
        )

    # Compare attributes
    if ignore_attribute_order:
        if set(e1.attrib.items()) != set(e2.attrib.items()):
            diff_attrs = set(e1.attrib.items()).symmetric_difference(
                set(e2.attrib.items())
            )
            return False, f"Attribute mismatch in <{e1.tag}>: {diff_attrs}"
    else:
        if e1.attrib != e2.attrib:
            return (
                False,
                f"Attribute mismatch in <{e1.tag}>: {e1.attrib} != {e2.attrib}",
            )

    # Compare number of children
    if len(e1) != len(e2):
        return (
            False,
            f"Different number of children in <{e1.tag}>: {len(e1)} != {len(e2)}",
        )

    # Recursively compare children
    for c1, c2 in zip(e1, e2):
        equal, msg = _elements_equal(c1, c2, ignore_attribute_order)
        if not equal:
            return False, msg

    return True, None


def xml_equal(
    left: XMLInput, right: XMLInput, ignore_attribute_order: bool = True
) -> bool:
    """
    Compare two XML documents for equality.

    PRESERVES WHITESPACE - all text content is compared exactly.

    Args:
        left: First XML document
        right: Second XML document
        ignore_attribute_order: Whether to ignore attribute order (default: True)

    Returns:
        True if documents are equal, False otherwise

    Example:
        >>> xml1 = "<root>  text  </root>"
        >>> xml2 = "<root>text</root>"
        >>> xml_equal(xml1, xml2)
        False  # Different whitespace
    """
    try:
        e1 = _to_element(left)
        e2 = _to_element(right)
        equal, _ = _elements_equal(e1, e2, ignore_attribute_order)
        return equal
    except Exception:
        return False


def xml_diff(left: XMLInput, right: XMLInput, context_lines: int = 3) -> str:
    """
    Generate a unified diff between two XML documents.

    Args:
        left: First XML document (expected)
        right: Second XML document (actual)
        context_lines: Number of context lines to show

    Returns:
        Unified diff string, or empty string if documents are equal

    Example:
        >>> diff = xml_diff(expected_xml, actual_xml)
        >>> if diff:
        ...     print("Differences found:")
        ...     print(diff)
    """
    try:
        e1 = _to_element(left)
        e2 = _to_element(right)

        # Serialize with pretty printing for readable diff
        s1 = et.tostring(e1, encoding="unicode", pretty_print=True)
        s2 = et.tostring(e2, encoding="unicode", pretty_print=True)

        # Generate unified diff
        diff_lines = list(
            unified_diff(
                s1.splitlines(keepends=True),
                s2.splitlines(keepends=True),
                fromfile="expected",
                tofile="actual",
                n=context_lines,
            )
        )

        return "".join(diff_lines) if diff_lines else ""

    except Exception as e:
        return f"Error generating diff: {e}"


def assert_xml_equal(
    left: XMLInput,
    right: XMLInput,
    message: str = "",
    ignore_attribute_order: bool = True,
) -> None:
    """
    Assert that two XML documents are equal, with detailed diff on failure.

    PRESERVES WHITESPACE - all text content is compared exactly.

    Args:
        left: First XML document (expected)
        right: Second XML document (actual)
        message: Custom message to prepend to assertion error
        ignore_attribute_order: Whether to ignore attribute order (default: True)

    Raises:
        AssertionError: If documents are not equal, with detailed diff

    Example:
        >>> assert_xml_equal(expected, result, "Transformation failed")
    """
    e1 = _to_element(left)
    e2 = _to_element(right)

    equal, diff_msg = _elements_equal(e1, e2, ignore_attribute_order)

    if not equal:
        diff = xml_diff(left, right)
        error_parts = []

        if message:
            error_parts.append(message)

        error_parts.append(f"\nXML documents are not equal: {diff_msg}")

        if diff:
            error_parts.append("\n\nDetailed diff:")
            error_parts.append(diff)

        raise AssertionError("\n".join(error_parts))


def normalize_for_comparison(
    xml_input: XMLInput,
    strip_whitespace: bool = False,
    normalize_space: bool = False,
    sort_attributes: bool = True,
) -> et._Element:
    """
    Normalize XML for comparison (USE SPARINGLY).

    By default, this function does minimal normalization. Only use whitespace
    normalization options when you're certain whitespace is not significant
    for your specific test case.

    Args:
        xml_input: Input XML
        strip_whitespace: Remove all whitespace-only text nodes (DANGEROUS)
        normalize_space: Normalize whitespace to single spaces (DANGEROUS)
        sort_attributes: Sort attributes alphabetically

    Returns:
        Normalized lxml Element

    Warning:
        Whitespace normalization should be avoided for TEI documents where
        whitespace can be semantically significant.
    """
    elem = _to_element(xml_input)

    # Deep copy to avoid modifying original
    elem = et.fromstring(et.tostring(elem))

    if strip_whitespace or normalize_space:
        _normalize_whitespace_recursive(elem, strip_whitespace, normalize_space)

    if sort_attributes:
        _sort_attributes_recursive(elem)

    return elem


def _normalize_whitespace_recursive(
    elem: et._Element, strip_whitespace: bool, normalize_space: bool
) -> None:
    """
    Recursively normalize whitespace in an element tree.

    Warning: This modifies the element in-place.
    """
    # Normalize text
    if elem.text:
        if strip_whitespace and elem.text.strip() == "":
            elem.text = None
        elif normalize_space:
            elem.text = " ".join(elem.text.split())

    # Normalize tail
    if elem.tail:
        if strip_whitespace and elem.tail.strip() == "":
            elem.tail = None
        elif normalize_space:
            elem.tail = " ".join(elem.tail.split())

    # Recursively process children
    for child in elem:
        _normalize_whitespace_recursive(child, strip_whitespace, normalize_space)


def _sort_attributes_recursive(elem: et._Element) -> None:
    """
    Recursively sort attributes alphabetically.

    Warning: This modifies the element in-place.
    """
    # Sort attributes
    if elem.attrib:
        sorted_attrib = dict(sorted(elem.attrib.items()))
        elem.attrib.clear()
        elem.attrib.update(sorted_attrib)

    # Recursively process children
    for child in elem:
        _sort_attributes_recursive(child)


def get_xpath_to_element(elem: et._Element, root: et._Element = None) -> str:
    """
    Generate an XPath expression to locate an element in a tree.

    Useful for debugging - shows where in the tree a difference occurred.

    Args:
        elem: The element to locate
        root: Root of the tree (if None, uses element's tree root)

    Returns:
        XPath expression as string

    Example:
        >>> xpath = get_xpath_to_element(problematic_element)
        >>> print(f"Difference at: {xpath}")
    """
    if root is None:
        tree = elem.getroottree()
        if tree is not None:
            root = tree.getroot()

    if root is None or elem is root:
        return f"/{elem.tag}"

    # Build path from root to element
    path_parts = []
    current = elem

    while current is not None and current is not root:
        parent = current.getparent()
        if parent is not None:
            # Count position among siblings with same tag
            siblings = [c for c in parent if c.tag == current.tag]
            if len(siblings) > 1:
                position = siblings.index(current) + 1
                path_parts.insert(0, f"{current.tag}[{position}]")
            else:
                path_parts.insert(0, current.tag)
            current = parent
        else:
            break

    if current is root:
        path_parts.insert(0, root.tag)
        return "/" + "/".join(path_parts)
    else:
        return "//" + "/".join(path_parts)


# ============================================================================
# Convenience functions for common comparison patterns
# ============================================================================


def assert_xml_structure_equal(
    left: XMLInput, right: XMLInput, message: str = ""
) -> None:
    """
    Assert XML structure is equal (tags, attributes) but ignore text content.

    Useful for testing structural transformations where text content
    is not modified.

    Args:
        left: Expected XML
        right: Actual XML
        message: Custom error message
    """

    def structure_only(elem: et._Element) -> et._Element:
        """Create a copy with structure but no text."""
        new_elem = et.Element(elem.tag, attrib=elem.attrib)
        for child in elem:
            new_elem.append(structure_only(child))
        return new_elem

    e1 = structure_only(_to_element(left))
    e2 = structure_only(_to_element(right))

    assert_xml_equal(e1, e2, message)


def assert_xml_contains(
    container: XMLInput, contained: XMLInput, message: str = ""
) -> None:
    """
    Assert that one XML fragment is contained within another.

    Args:
        container: XML that should contain the fragment
        contained: XML fragment to find
        message: Custom error message
    """
    container_elem = _to_element(container)
    contained_elem = _to_element(contained)

    # Serialize contained element for searching
    contained_str = et.tostring(contained_elem, encoding="unicode")
    container_str = et.tostring(container_elem, encoding="unicode")

    if contained_str not in container_str:
        error_msg = f"XML fragment not found in container"
        if message:
            error_msg = f"{message}\n{error_msg}"
        raise AssertionError(error_msg)


# ============================================================================
# Text-based comparison utilities
# ============================================================================


def normalize_prologue(xml_text: str) -> Tuple[str, str]:
    """
    Normalize XML prologue formatting for comparison.

    Separates the XML prologue (declarations, DOCTYPE) from the root element
    and normalizes formatting differences that are semantically irrelevant
    (quote style, newlines between declarations).

    Args:
        xml_text: The complete XML document as text

    Returns:
        Tuple of (normalized_prologue, content) where content starts from root element

    Example:
        >>> prologue, content = normalize_prologue(xml_text)
        >>> # Compare prologues and content separately
    """
    # Split at the root element (assumes TEI documents)
    if "<TEI" in xml_text:
        prologue, content = xml_text.split("<TEI", 1)
        content = "<TEI" + content

        # Normalize prologue:
        # 1. Replace single quotes with double quotes in XML declaration
        prologue = prologue.replace("'", '"')

        # 2. Normalize whitespace between declarations
        # Remove extra newlines, keep single newlines between declarations
        prologue = re.sub(r"\n\s*\n", "\n", prologue)

        # 3. Add newlines after each ?> and DOCTYPE > for consistent formatting
        prologue = re.sub(r"\?>\s*<\?", "?>\n<?", prologue)
        prologue = re.sub(r"\?>\s*<!DOCTYPE", "?>\n<!DOCTYPE", prologue)

        return prologue, content

    # If no TEI element found, look for any root element
    # Find first < that's not part of a declaration/comment
    for i, char in enumerate(xml_text):
        if char == "<" and i + 1 < len(xml_text):
            next_char = xml_text[i + 1]
            if next_char not in ["?", "!"]:  # Not a declaration or comment
                prologue = xml_text[:i]
                content = xml_text[i:]
                # Apply same normalization
                prologue = prologue.replace("'", '"')
                prologue = re.sub(r"\n\s*\n", "\n", prologue)
                prologue = re.sub(r"\?>\s*<\?", "?>\n<?", prologue)
                prologue = re.sub(r"\?>\s*<!DOCTYPE", "?>\n<!DOCTYPE", prologue)
                return prologue, content

    return xml_text, ""


def xml_to_comparable_text(
    xml_input: Union[XMLInput, str, Path], strip_trailing_whitespace: bool = True
) -> str:
    """
    Convert XML to normalized text string for text-based comparison.

    Args:
        xml_input: XML as Element, ElementTree, string, bytes, or Path to a file
        strip_trailing_whitespace: Whether to strip trailing whitespace from content

    Returns:
        XML as text string, suitable for text comparison

    Example:
        >>> text1 = xml_to_comparable_text(tree1)
        >>> text2 = xml_to_comparable_text(tree2)
        >>> text3 = xml_to_comparable_text(Path("file.xml"))
        >>> assert text1 == text2
    """
    # Handle Path objects
    if isinstance(xml_input, Path):
        with open(xml_input, "r", encoding="utf-8") as f:
            xml_text = f.read()
    # If it's a string, determine if it's XML text or a file path
    elif isinstance(xml_input, str):
        # Check if it's a file path (doesn't start with '<' or whitespace)
        if not xml_input.lstrip().startswith("<"):
            # Try to read as file
            try:
                with open(xml_input, "r", encoding="utf-8") as f:
                    xml_text = f.read()
            except (FileNotFoundError, OSError):
                # Not a file, treat as XML string
                xml_text = xml_input
        else:
            xml_text = xml_input
    else:
        # Convert element to string
        elem = _to_element(xml_input)
        xml_text = et.tostring(elem, encoding="unicode", xml_declaration=False)

    if strip_trailing_whitespace:
        xml_text = xml_text.rstrip()

    return xml_text


def text_equal(
    left: Union[str, XMLInput, Path],
    right: Union[str, XMLInput, Path],
    normalize_prologues: bool = True,
    strip_trailing_whitespace: bool = True,
) -> bool:
    """
    Compare two XML documents as text strings.

    Unlike xml_equal() which compares parsed XML trees, this function compares
    the serialized text representation. This is useful for ensuring byte-for-byte
    reproducibility of XML files.

    Args:
        left: First document (text, file path, Path object, or XML element)
        right: Second document (text, file path, Path object, or XML element)
        normalize_prologues: Whether to normalize prologue formatting before comparison
        strip_trailing_whitespace: Whether to strip trailing whitespace

    Returns:
        True if documents are equal as text, False otherwise

    Example:
        >>> # Compare two XML files byte-for-byte
        >>> assert text_equal("input.xml", "output.xml")
        >>> assert text_equal(Path("input.xml"), Path("output.xml"))
        >>>
        >>> # Compare XML trees as text
        >>> assert text_equal(original_tree, reloaded_tree)
    """
    # Convert inputs to text
    left_text = xml_to_comparable_text(left, strip_trailing_whitespace)
    right_text = xml_to_comparable_text(right, strip_trailing_whitespace)

    if normalize_prologues:
        # Split and normalize prologues
        left_prologue, left_content = normalize_prologue(left_text)
        right_prologue, right_content = normalize_prologue(right_text)

        # Compare both parts
        return left_prologue == right_prologue and left_content == right_content
    else:
        # Direct text comparison
        return left_text == right_text


def assert_text_equal(
    left: Union[str, XMLInput, Path],
    right: Union[str, XMLInput, Path],
    message: str = "",
    normalize_prologues: bool = True,
    strip_trailing_whitespace: bool = True,
) -> None:
    """
    Assert that two XML documents are equal as text, with detailed diff on failure.

    This is useful for testing that XML files can be written and reloaded with
    exact preservation of formatting, whitespace, and entity references.

    Args:
        left: Expected document (text, file path, Path object, or XML element)
        right: Actual document (text, file path, Path object, or XML element)
        message: Custom message to prepend to assertion error
        normalize_prologues: Whether to normalize prologue formatting before comparison
        strip_trailing_whitespace: Whether to strip trailing whitespace

    Raises:
        AssertionError: If documents are not equal as text, with detailed diff

    Example:
        >>> # Test that roundtrip preserves exact formatting
        >>> assert_text_equal("input.xml", "output.xml", "Roundtrip failed")
        >>> assert_text_equal(Path("input.xml"), Path("output.xml"))
        >>>
        >>> # Can also compare XML elements or text strings
        >>> assert_text_equal(original_tree, reloaded_tree)
    """
    # Convert inputs to text
    left_text = xml_to_comparable_text(left, strip_trailing_whitespace)
    right_text = xml_to_comparable_text(right, strip_trailing_whitespace)

    if normalize_prologues:
        # Split and normalize prologues
        left_prologue, left_content = normalize_prologue(left_text)
        right_prologue, right_content = normalize_prologue(right_text)

        # Check prologue equality
        if left_prologue != right_prologue:
            error_parts = []
            if message:
                error_parts.append(message)

            error_parts.append("\nXML prologues differ:")
            error_parts.append(f"\nExpected prologue:\n{left_prologue}")
            error_parts.append(f"\nActual prologue:\n{right_prologue}")

            # Generate diff
            diff_lines = list(
                unified_diff(
                    left_prologue.splitlines(keepends=True),
                    right_prologue.splitlines(keepends=True),
                    fromfile="expected prologue",
                    tofile="actual prologue",
                    n=3,
                )
            )
            if diff_lines:
                error_parts.append("\nPrologue diff:")
                error_parts.append("".join(diff_lines))

            raise AssertionError("\n".join(error_parts))

        # Check content equality
        if left_content != right_content:
            error_parts = []
            if message:
                error_parts.append(message)

            error_parts.append("\nXML content differs (elements, text, or whitespace)")

            # Generate diff
            diff_lines = list(
                unified_diff(
                    left_content.splitlines(keepends=True),
                    right_content.splitlines(keepends=True),
                    fromfile="expected content",
                    tofile="actual content",
                    n=3,
                )
            )
            if diff_lines:
                error_parts.append("\nContent diff:")
                error_parts.append("".join(diff_lines))

            raise AssertionError("\n".join(error_parts))
    else:
        # Direct comparison
        if left_text != right_text:
            error_parts = []
            if message:
                error_parts.append(message)

            error_parts.append("\nXML documents differ as text")

            # Generate diff
            diff_lines = list(
                unified_diff(
                    left_text.splitlines(keepends=True),
                    right_text.splitlines(keepends=True),
                    fromfile="expected",
                    tofile="actual",
                    n=3,
                )
            )
            if diff_lines:
                error_parts.append("\nDiff:")
                error_parts.append("".join(diff_lines))

            raise AssertionError("\n".join(error_parts))


def vanilla_compare_flow(step, fixture_loader, variant="basic", generate_auto=False):
    # Initialize step
    step = step.get_step()
    step_name = step.get_name()

    # Load as pair using structured API (returns tuple of trees)
    input_tree, expected_tree = fixture_loader.load_step_pair(
        step_name, variant=variant
    )

    input_string = fixture_loader.tree_to_string(input_tree)
    result_string = step.execute(input_string)

    if generate_auto:
        actual_path = fixture_loader.get_step_fixture_path(
            step_name, f"auto_expected_{variant}"
        )
        with codecs.open(actual_path, "w", "utf-8") as out:
            out.write(result_string)
        print(f"Wrote actual output to: {actual_path}")

    assert_xml_equal(expected_tree, result_string)


def pipeline_compare_flow(
    pipeline: Pipeline, 
    input_file: Path, 
    compare_file:Path, 
    generate_auto: bool = False, 
    debug: Optional[list[Literal["time", "serial"]]] = None
) -> None:
    result = pipeline.execute(input_file, debug_options= debug)
    if generate_auto:
        outfile = (
            compare_file.with_name(f"auto_{compare_file.stem}{compare_file.suffix}")
            if compare_file
            else input_file.with_name(f"auto_{input_file.stem}{input_file.suffix}")
        )
        with codecs.open(outfile, "w", "utf-8") as out:
            out.write(result)
    expected_tree = (
        et.parse(compare_file)
        if compare_file
        else et.parse(input_file.with_name(f"{input_file.stem}{input_file.suffix}"))
    )

    assert_xml_equal(expected_tree, result)
