"""
XML comparison utilities for heipy tests.

IMPORTANT: These utilities PRESERVE WHITESPACE by default, as whitespace
is semantically significant in TEI documents for digital scholarly editing.

Functions:
- xml_equal(): Compare two XML trees for equality
- xml_diff(): Generate a detailed diff between two XML trees
- assert_xml_equal(): Assert XML equality with detailed error messages
- normalize_for_comparison(): Optional normalization (use sparingly)
"""

from lxml import etree as et
from typing import Union, Optional, Tuple
from difflib import unified_diff
import re


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
        return et.fromstring(xml_input.encode('utf-8'))
    elif isinstance(xml_input, bytes):
        return et.fromstring(xml_input)
    else:
        raise TypeError(f"Unsupported XML input type: {type(xml_input)}")


def _elements_equal(e1: et._Element, e2: et._Element,
                   ignore_attribute_order: bool = True) -> Tuple[bool, Optional[str]]:
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
        return False, f"Tail mismatch after <{e1.tag}>: {repr(e1.tail)} != {repr(e2.tail)}"

    # Compare attributes
    if ignore_attribute_order:
        if set(e1.attrib.items()) != set(e2.attrib.items()):
            diff_attrs = set(e1.attrib.items()).symmetric_difference(set(e2.attrib.items()))
            return False, f"Attribute mismatch in <{e1.tag}>: {diff_attrs}"
    else:
        if e1.attrib != e2.attrib:
            return False, f"Attribute mismatch in <{e1.tag}>: {e1.attrib} != {e2.attrib}"

    # Compare number of children
    if len(e1) != len(e2):
        return False, f"Different number of children in <{e1.tag}>: {len(e1)} != {len(e2)}"

    # Recursively compare children
    for c1, c2 in zip(e1, e2):
        equal, msg = _elements_equal(c1, c2, ignore_attribute_order)
        if not equal:
            return False, msg

    return True, None


def xml_equal(left: XMLInput, right: XMLInput,
              ignore_attribute_order: bool = True) -> bool:
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


def xml_diff(left: XMLInput, right: XMLInput,
             context_lines: int = 3) -> str:
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
        s1 = et.tostring(e1, encoding='unicode', pretty_print=True)
        s2 = et.tostring(e2, encoding='unicode', pretty_print=True)

        # Generate unified diff
        diff_lines = list(unified_diff(
            s1.splitlines(keepends=True),
            s2.splitlines(keepends=True),
            fromfile='expected',
            tofile='actual',
            n=context_lines
        ))

        return ''.join(diff_lines) if diff_lines else ''

    except Exception as e:
        return f"Error generating diff: {e}"


def assert_xml_equal(left: XMLInput, right: XMLInput,
                    message: str = "",
                    ignore_attribute_order: bool = True) -> None:
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

        raise AssertionError('\n'.join(error_parts))


def normalize_for_comparison(xml_input: XMLInput,
                             strip_whitespace: bool = False,
                             normalize_space: bool = False,
                             sort_attributes: bool = True) -> et._Element:
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


def _normalize_whitespace_recursive(elem: et._Element,
                                    strip_whitespace: bool,
                                    normalize_space: bool) -> None:
    """
    Recursively normalize whitespace in an element tree.

    Warning: This modifies the element in-place.
    """
    # Normalize text
    if elem.text:
        if strip_whitespace and elem.text.strip() == '':
            elem.text = None
        elif normalize_space:
            elem.text = ' '.join(elem.text.split())

    # Normalize tail
    if elem.tail:
        if strip_whitespace and elem.tail.strip() == '':
            elem.tail = None
        elif normalize_space:
            elem.tail = ' '.join(elem.tail.split())

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

def assert_xml_structure_equal(left: XMLInput, right: XMLInput,
                               message: str = "") -> None:
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


def assert_xml_contains(container: XMLInput, contained: XMLInput,
                       message: str = "") -> None:
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
    contained_str = et.tostring(contained_elem, encoding='unicode')
    container_str = et.tostring(container_elem, encoding='unicode')

    if contained_str not in container_str:
        error_msg = f"XML fragment not found in container"
        if message:
            error_msg = f"{message}\n{error_msg}"
        raise AssertionError(error_msg)
