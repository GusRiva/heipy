"""
Tests for parser input/output operations.

Tests that XML files can be loaded and written correctly, with special
attention to entity preservation in heiEDITIONS documents.
"""

import re
from lxml import etree as et
from pathlib import Path

from heipy.parsers import HeiEditionsParser


def normalize_prologue(xml_text):
    """
    Normalize prologue formatting for comparison.

    Separates the XML prologue from the content and normalizes formatting
    differences that are semantically irrelevant (quote style, newlines).

    Args:
        xml_text (str): The complete XML document text

    Returns:
        tuple: (normalized_prologue, content) where content starts from root element
    """
    # Split at the root element
    if '<TEI' in xml_text:
        prologue, content = xml_text.split('<TEI', 1)
        content = '<TEI' + content

        # Normalize prologue:
        # 1. Replace single quotes with double quotes in XML declaration
        prologue = prologue.replace("'", '"')

        # 2. Normalize whitespace between declarations
        # Remove extra newlines, keep single newlines between declarations
        prologue = re.sub(r'\n\s*\n', '\n', prologue)

        # 3. Add newlines after each ?> and DOCTYPE > for consistent formatting
        prologue = re.sub(r'\?>\s*<\?', '?>\n<?', prologue)
        prologue = re.sub(r'\?>\s*<!DOCTYPE', '?>\n<!DOCTYPE', prologue)

        return prologue, content
    return xml_text, ''


def compare_elements(elem1, elem2):
    """
    Recursively compare two XML elements for equality.

    Checks:
    - Tag name
    - Attributes
    - Text content
    - Tail content
    - Children (recursively)

    Returns True if identical, False otherwise.
    """
    # Check tag
    if elem1.tag != elem2.tag:
        return False

    # Check attributes
    if elem1.attrib != elem2.attrib:
        return False

    # Check text (strip to ignore whitespace differences in mixed content)
    if (elem1.text or '').strip() != (elem2.text or '').strip():
        return False

    # Check tail
    if (elem1.tail or '').strip() != (elem2.tail or '').strip():
        return False

    # Check number of children
    if len(elem1) != len(elem2):
        return False

    # Recursively check all children
    for child1, child2 in zip(elem1, elem2):
        if not compare_elements(child1, child2):
            return False

    return True


class TestBasicTEIRoundtrip:
    """Test basic TEI document loading and writing."""

    def test_basic_tei_loads_successfully(self, basic_tei):
        """Test that basic TEI fixture loads without error."""
        assert basic_tei is not None
        root = basic_tei.getroot()
        assert root.tag == "{http://www.tei-c.org/ns/1.0}TEI"

    def test_basic_tei_has_expected_structure(self, basic_tei):
        """Test that basic TEI has expected elements."""
        root = basic_tei.getroot()

        # Check for teiHeader
        header = root.find(".//{http://www.tei-c.org/ns/1.0}teiHeader")
        assert header is not None

        # Check for text/body
        body = root.find(".//{http://www.tei-c.org/ns/1.0}body")
        assert body is not None

        # Check for paragraphs
        paragraphs = body.findall(".//{http://www.tei-c.org/ns/1.0}p")
        assert len(paragraphs) >= 1

    def test_basic_tei_roundtrip(self, basic_tei, tmp_path):
        """Test that basic TEI can be written and reloaded without data loss."""
        # Write to temporary file
        output_path = tmp_path / "output.xml"
        with open(output_path, 'wb') as f:
            basic_tei.write(f, encoding='utf-8', xml_declaration=True)

        # Verify file was created
        assert output_path.exists()

        # Re-load the file
        reloaded = et.parse(str(output_path))

        # Compare structure
        original_root = basic_tei.getroot()
        reloaded_root = reloaded.getroot()

        assert original_root.tag == reloaded_root.tag

        # Check that content is preserved
        original_paragraphs = original_root.findall(".//{http://www.tei-c.org/ns/1.0}p")
        reloaded_paragraphs = reloaded_root.findall(".//{http://www.tei-c.org/ns/1.0}p")

        assert len(original_paragraphs) == len(reloaded_paragraphs)

        # Check xml:id attributes are preserved
        for orig_p, reload_p in zip(original_paragraphs, reloaded_paragraphs):
            orig_id = orig_p.get("{http://www.w3.org/XML/1998/namespace}id")
            reload_id = reload_p.get("{http://www.w3.org/XML/1998/namespace}id")
            assert orig_id == reload_id


class TestEntityPreservation:
    """Test that heiEDITIONS entities are preserved through load/write cycles."""

    def test_tei_with_entities_loads_successfully(self, tei_with_entities):
        """Test that TEI with entities fixture loads without error."""
        assert tei_with_entities is not None
        root = tei_with_entities.getroot()
        assert root.tag == "{http://www.tei-c.org/ns/1.0}TEI"

    def test_entities_are_loaded(self, tei_with_entities):
        """Test that entities are present in the loaded document."""
        # Serialize the tree and check if entities are in the output
        xml_string = et.tostring(tei_with_entities, encoding='unicode')

        # Check if the entity references appear in the serialized output
        assert '&bar;' in xml_string, "Expected &bar; entity in serialized output"
        assert '&us;' in xml_string, "Expected &us; entity in serialized output"
        assert '&er;' in xml_string, "Expected &er; entity in serialized output"

    def test_entity_preservation_in_serialization(self, tei_with_entities, tmp_path, minimal_fixtures_dir):
        """
        Test that entities are preserved when writing XML.

        This is the critical test: entities like &bar; should appear in the
        output file, not their resolved Unicode characters.
        """
        # Write to temporary file
        output_path = tmp_path / "output_with_entities.xml"
        with open(output_path, 'wb') as f:
            tei_with_entities.write(f, encoding='utf-8', xml_declaration=True)

        # Read the output as raw text
        with open(output_path, 'r', encoding='utf-8') as f:
            output_text = f.read()

        # Check if entities are preserved in output
        # The output should contain entity references like &bar;, &us;, AND &er;
        assert '&bar;' in output_text, "Expected &bar; entity in output file"
        assert '&us;' in output_text, "Expected &us; entity in output file"
        assert '&er;' in output_text, "Expected &er; entity in output file"

        # Read the original input as raw text for comparison
        input_path = minimal_fixtures_dir / "tei_with_entities.xml"
        with open(input_path, 'r', encoding='utf-8') as f:
            input_text = f.read()

        # Check if the DOCTYPE declaration is preserved
        # (This is important for entity definitions)
        if '<!DOCTYPE' in input_text:
            # DOCTYPE should be in output if it was in input
            assert '<!DOCTYPE' in output_text, "DOCTYPE declaration not preserved"

    def test_roundtrip_with_entities(self, minimal_fixtures_dir, tmp_path):
        """
        Test complete roundtrip: load with HeiEditionsParser, write, reload, compare.
        """
        # Load original with HeiEditionsParser
        parser = HeiEditionsParser()
        input_path = minimal_fixtures_dir / "tei_with_entities.xml"
        original_tree = et.parse(str(input_path), parser=parser)

        # Write to temp file
        output_path = tmp_path / "roundtrip.xml"
        with open(output_path, 'wb') as f:
            original_tree.write(f, encoding='utf-8', xml_declaration=True)

        # Read the original input file as text
        with open(input_path, 'r', encoding='utf-8') as f:
            original_text = f.read()

        # Read the serialized output file as text
        with open(output_path, 'r', encoding='utf-8') as f:
            output_text = f.read()

        # Split into prologue and content
        orig_prologue, orig_content = normalize_prologue(original_text)
        out_prologue, out_content = normalize_prologue(output_text)

        # Normalize trailing whitespace - strip it from both for comparison
        orig_content = orig_content.rstrip()
        out_content = out_content.rstrip()

        # Prologue should be semantically equivalent (after normalization)
        assert orig_prologue == out_prologue, \
            f"Prologue differs:\nOriginal:\n{orig_prologue}\n\nOutput:\n{out_prologue}"

        # Content must be byte-for-byte identical (after normalizing trailing newlines)
        assert orig_content == out_content, \
            "XML content differs (elements, text, or whitespace)"


class TestHeiEditionsParser:
    """Test HeiEditionsParser specific functionality."""

    def test_parser_initialization(self):
        """Test that HeiEditionsParser can be initialized."""
        parser = HeiEditionsParser()
        assert parser is not None

    def test_parser_has_dtd_support(self, minimal_fixtures_dir):
        """Test that parser is configured to load DTDs."""
        parser = HeiEditionsParser()

        # Test that the parser can actually load a file with DOCTYPE/entities
        # This verifies that load_dtd=True is working
        input_path = minimal_fixtures_dir / "tei_with_entities.xml"
        tree = et.parse(str(input_path), parser=parser)

        # If DTD support wasn't enabled, parsing would fail or entities wouldn't work
        assert tree is not None
        root = tree.getroot()
        assert root.tag == "{http://www.tei-c.org/ns/1.0}TEI"

    def test_parser_has_entity_resolver(self):
        """Test that parser has custom entity resolver."""
        parser = HeiEditionsParser()
        # The parser should have resolvers configured
        assert parser.resolvers is not None
        assert hasattr(parser.resolvers, 'add')

    def test_parse_simple_xml_string(self, hei_parser):
        """Test parsing a simple XML string."""
        xml_string = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <element>content</element>
</root>"""
        tree = et.fromstring(xml_string.encode('utf-8'), parser=hei_parser)
        assert tree is not None
        assert tree.tag == "root"

    def test_parse_tei_string(self, hei_parser):
        """Test parsing a simple TEI string."""
        tei_string = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt><title>Test</title></titleStmt>
            <publicationStmt><p>Test</p></publicationStmt>
            <sourceDesc><p>Test</p></sourceDesc>
        </fileDesc>
    </teiHeader>
    <text><body><p>Test</p></body></text>
</TEI>"""
        tree = et.fromstring(tei_string.encode('utf-8'), parser=hei_parser)
        assert tree is not None
        assert tree.tag == "{http://www.tei-c.org/ns/1.0}TEI"
