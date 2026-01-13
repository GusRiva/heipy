"""
Pytest configuration and shared fixtures for heipy tests.

This module provides common fixtures used across all test modules including:
- Path fixtures for test data directories
- XML parsing fixtures
- Saxon processor fixtures
- Minimal TEI document fixtures
- Comparison helper fixtures
"""

import pytest
from pathlib import Path
from lxml import etree as et
from saxonche import PySaxonProcessor

# Import heipy modules
from heipy.parsers import HeiEditionsParser, heiparse
from heipy.namespaces import ns


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def minimal_fixtures_dir(fixtures_dir):
    """Return path to minimal TEI fixtures."""
    return fixtures_dir / "minimal"

@pytest.fixture(scope="session")
def complex_fixtures_dir(fixtures_dir):
    """Return path to minimal TEI fixtures."""
    return fixtures_dir / "complex"


@pytest.fixture(scope="session")
def step_fixtures_dir(fixtures_dir):
    """Return path to step-specific fixtures."""
    return fixtures_dir / "step_library"


# ============================================================================
# XML Parsing Fixtures
# ============================================================================

@pytest.fixture
def hei_parser():
    """
    Provide HeiEditionsParser instance.

    This parser includes custom entity resolution for heiEDITIONS schema
    and is configured for TEI XML parsing.
    """
    return HeiEditionsParser()


@pytest.fixture
def parse_xml(hei_parser):
    """
    Factory fixture to parse XML strings or files.

    Usage:
        def test_something(parse_xml):
            tree = parse_xml("<root>content</root>")
            # or
            tree = parse_xml(filepath="path/to/file.xml")
    """
    def _parse(xml_string=None, filepath=None):
        if filepath:
            return et.parse(str(filepath), parser=hei_parser)
        elif xml_string:
            return et.fromstring(xml_string.encode('utf-8'), parser=hei_parser)
        else:
            raise ValueError("Must provide either xml_string or filepath")
    return _parse


# ============================================================================
# Saxon Processor Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def saxon_proc():
    """
    Provide Saxon processor with automatic cleanup.

    The processor is created for each test function and properly cleaned up
    after the test completes. Use this when testing XSLT transformations.

    Usage:
        def test_xslt(saxon_proc):
            xslt_proc = saxon_proc.new_xslt30_processor()
            # ... use processor
    """
    proc = PySaxonProcessor(license=False)
    yield proc
    # Cleanup handled automatically by context manager pattern


# ============================================================================
# Minimal TEI Document Fixtures
# ============================================================================

@pytest.fixture
def basic_tei(minimal_fixtures_dir, hei_parser):
    """
    Load basic minimal TEI document.

    Contains a minimal valid TEI structure with:
    - teiHeader with required elements
    - Single paragraph in body
    """
    path = minimal_fixtures_dir / "basic_tei.xml"
    return et.parse(str(path), parser=hei_parser)


@pytest.fixture
def tei_with_entities(minimal_fixtures_dir, hei_parser):
    """
    Load TEI document with heiEDITIONS entities.

    Contains:
    - heiEDITIONS schema declaration
    - DOCTYPE with entity declarations
    - Common entities: &bar;, &us;, &er;

    Used for testing entity preservation through load/write cycles.
    """
    path = minimal_fixtures_dir / "tei_with_entities.xml"
    return et.parse(str(path), parser=hei_parser)

@pytest.fixture
def tei_with_xinclude_path(minimal_fixtures_dir):
    """
    Path to TEI document with xi:include function.
    Contains:
    - heiEDITIONS schema declaration
    - xi Prefix definition
    - xi:include
    Used for testing entity preservation through load/write cycles.
    """
    return minimal_fixtures_dir / "tei_with_xinclude.xml"
    


# ============================================================================
# XML Comparison Functions
# ============================================================================
#
# XML comparison functions are available in tests.helpers.xml_compare
# Import them directly in your test files instead of using fixtures:
#
# from tests.helpers.xml_compare import xml_equal, assert_xml_equal, assert_text_equal
#
# Available functions:
#   - xml_equal(): Compare two XML trees for equality (element-based)
#   - xml_diff(): Generate detailed diff between XML trees
#   - assert_xml_equal(): Assert XML equality with detailed error messages
#   - assert_xml_structure_equal(): Compare structure only (ignore text)
#   - assert_xml_contains(): Check if XML fragment is contained
#   - text_equal(): Compare XML documents as text strings
#   - assert_text_equal(): Assert text equality with detailed diff
#   - normalize_prologue(): Normalize XML prologue formatting
#
# Example usage:
#     from tests.helpers.xml_compare import xml_equal
#
#     def test_transformation(fixture_loader):
#         result = transform(input_xml)
#         assert xml_equal(result, expected)
#
# ============================================================================


# ============================================================================
# Fixture Loader Fixtures
# ============================================================================

@pytest.fixture
def fixture_loader(step_fixtures_dir):
    """
    Provide StepFixtureLoader instance for loading step test fixtures.

    Usage:
        def test_step(fixture_loader):
            input_tree, expected_tree = fixture_loader.load_step_pair("step_name")
    """
    from tests.helpers.fixture_loader import StepFixtureLoader
    return StepFixtureLoader(step_fixtures_dir)


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def xml_to_string():
    """
    Provide helper to convert XML tree to string.

    Usage:
        def test_something(xml_to_string):
            xml_string = xml_to_string(tree)
    """
    def _to_string(tree, pretty=False):
        if isinstance(tree, et._Element):
            return et.tostring(tree, encoding="unicode", pretty_print=pretty)
        elif isinstance(tree, et._ElementTree):
            return et.tostring(tree.getroot(), encoding="unicode", pretty_print=pretty)
        else:
            raise TypeError(f"Expected Element or ElementTree, got {type(tree)}")
    return _to_string


@pytest.fixture
def tmp_xml_file(tmp_path):
    """
    Factory fixture to create temporary XML files for testing.

    Usage:
        def test_file_processing(tmp_xml_file):
            xml_file = tmp_xml_file("<root>test</root>", filename="test.xml")
            # ... use xml_file path
    """
    def _create(xml_content, filename="temp.xml"):
        xml_path = tmp_path / filename
        xml_path.write_text(xml_content, encoding="utf-8")
        return xml_path
    return _create
