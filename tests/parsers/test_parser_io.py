"""
Tests for parser input/output operations.

Tests that XML files can be loaded and written correctly, with special
attention to entity preservation in heiEDITIONS documents.
"""

from lxml import etree as et

from heipy.parsers import HeiEditionsParser, heiparse
from heipy.namespaces import ns
from tests.helpers.xml_compare import normalize_prologue, assert_text_equal


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


class TestXInclude:
    """Test xi:include instructions are resolved correctly."""
    def test_tei_with_xinclude_resolves_succesfully(self, tei_with_xinclude_path):
        """Tests that if xinclude is True, the xi:include element is resolved"""
        tei_tree = heiparse(tei_with_xinclude_path, xinclude=True)
        text_tag = tei_tree.find("tei:text", ns)
        assert text_tag is not None

    def test_tei_with_xinclude_not_resolve_succesfully(self, tei_with_xinclude_path):
        """Tests that if xinclude is False, the xi:include element is not resolved"""
        tei_tree = heiparse(tei_with_xinclude_path, xinclude=False)
        text_tag = tei_tree.find("tei:text", ns)
        assert text_tag is None
        xinclude_tag = tei_tree.find("xi:include", ns)
        assert xinclude_tag is not None

    def test_tei_with_xinclude_has_children(self, tei_with_xinclude_path):
        """Tests that if xinclude is True, the xi:include element is resolved and chidren loaded"""
        tei_tree = heiparse(tei_with_xinclude_path, xinclude=True)
        text_tag = tei_tree.find("tei:text", ns)
        p_els = text_tag.findall(".//tei:p", ns)
        assert len(p_els) == 2


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

        Uses text-based comparison to ensure byte-for-byte preservation of
        entities, formatting, and whitespace.
        """
        # Load original with HeiEditionsParser
        parser = HeiEditionsParser()
        input_path = minimal_fixtures_dir / "tei_with_entities.xml"
        original_tree = et.parse(str(input_path), parser=parser)

        # Write to temp file
        output_path = tmp_path / "roundtrip.xml"
        with open(output_path, 'wb') as f:
            original_tree.write(f, encoding='utf-8', xml_declaration=True)

        # Compare original and output as text (with prologue normalization)
        assert_text_equal(
            input_path,
            output_path,
            message="Roundtrip with entities failed",
            normalize_prologues=True,
            strip_trailing_whitespace=True
        )


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
