"""
Tests for UnwrapStep class.

UnwrapStep removes wrapper elements while preserving their children,
using the unwrapFromElements.xsl transformation.
"""

import pytest
from lxml import etree as et

from heipy.heipipe.steps import UnwrapStep
from heipy.parsers import HeiEditionsParser


@pytest.mark.unit
@pytest.mark.xslt
@pytest.mark.requires_saxon
class TestUnwrapStepInitialization:
    """Test UnwrapStep initialization."""

    def test_init_with_elements_list(self):
        """Test initialization with elements list."""
        elements = [{"element_name": "seg"}]
        step = UnwrapStep(elements=elements, name="unwrap_test")
        assert step.get_name() == "unwrap_test"

    def test_init_without_name(self):
        """Test initialization without name."""
        step = UnwrapStep(elements=[{"element_name": "seg"}])
        assert step.get_name() == "__Unwrap__"

    @pytest.mark.filterwarnings("ignore:An UnwrapStep with no elements:heipy.heiwarning.HeiWarning")
    def test_init_with_empty_elements_list(self):
        """Test initialization with empty elements list."""
        step = UnwrapStep(elements=[])
        assert step.elements == []

    def test_init_stores_elements(self):
        """Test that elements are stored correctly."""
        elements = [
            {"element_name": "seg"},
            {"element_name": "span", "attrib_name": "type"}
        ]
        step = UnwrapStep(elements=elements)
        assert step.elements == elements


@pytest.mark.unit
@pytest.mark.xslt
@pytest.mark.requires_saxon
class TestUnwrapStepBasicUnwrapping:
    """Test basic element unwrapping."""

    def test_unwrap_single_element_type(self):
        """Test unwrapping a single element type by name."""
        step = UnwrapStep(elements=[{"element_name": "seg"}])
        input_xml = """<root>
            <p>Text with <seg>wrapped content</seg> continues.</p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        # seg should be removed, but its text content should remain
        segs = result_tree.findall(".//seg")
        assert len(segs) == 0
        p = result_tree.find(".//p")
        # Text should be preserved
        assert "wrapped content" in et.tostring(p, encoding='unicode', method='text')

    def test_unwrap_preserves_children_text(self):
        """Test that children's text is preserved after unwrapping."""
        step = UnwrapStep(elements=[{"element_name": "wrapper"}])
        input_xml = """<root>
            <wrapper>Content inside wrapper</wrapper>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        wrappers = result_tree.findall(".//wrapper")
        assert len(wrappers) == 0
        # Content should be preserved in parent
        assert "Content inside wrapper" in result

    def test_unwrap_preserves_nested_children(self):
        """Test that nested child elements are preserved."""
        step = UnwrapStep(elements=[{"element_name": "outer"}])
        input_xml = """<root>
            <outer>
                <inner>Nested content</inner>
            </outer>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        # outer should be removed
        outers = result_tree.findall(".//outer")
        assert len(outers) == 0
        # inner should still exist
        inners = result_tree.findall(".//inner")
        assert len(inners) == 1
        assert inners[0].text == "Nested content"

    def test_unwrap_multiple_instances(self):
        """Test unwrapping all instances of an element."""
        step = UnwrapStep(elements=[{"element_name": "seg"}])
        input_xml = """<root>
            <p><seg>First</seg> and <seg>Second</seg> and <seg>Third</seg></p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        segs = result_tree.findall(".//seg")
        assert len(segs) == 0
        # All text should be preserved
        p = result_tree.find("p")
        text_content = et.tostring(p, encoding='unicode', method='text')
        assert "First" in text_content
        assert "Second" in text_content
        assert "Third" in text_content


@pytest.mark.unit
@pytest.mark.xslt
@pytest.mark.requires_saxon
class TestUnwrapStepWithAttributes:
    """Test unwrapping with attribute matching."""

    def test_unwrap_by_element_and_attribute_name(self):
        """Test unwrapping elements with specific attribute name."""
        step = UnwrapStep(elements=[{
            "element_name": "seg",
            "attrib_name": "type"
        }])
        input_xml = """<root>
            <p>
                <seg type="phrase">With type</seg>
                <seg>Without type</seg>
            </p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        # Only seg with type attribute should be unwrapped
        segs = result_tree.findall(".//seg")
        # The one without type attribute should remain
        assert len(segs) == 1
        assert segs[0].get("type") is None

    def test_unwrap_by_element_attribute_and_value(self):
        """Test unwrapping elements with specific attribute value."""
        step = UnwrapStep(elements=[{
            "element_name": "seg",
            "attrib_name": "type",
            "attrib_val": "editorial"
        }])
        input_xml = """<root>
            <p>
                <seg type="editorial">Editorial seg</seg>
                <seg type="original">Original seg</seg>
                <seg>No type seg</seg>
            </p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        # Only seg with type="editorial" should be unwrapped
        segs = result_tree.findall(".//seg")
        assert len(segs) == 2
        # Check remaining segs
        types = [seg.get("type") for seg in segs]
        assert "editorial" not in types
        assert "original" in types


@pytest.mark.unit
@pytest.mark.xslt
@pytest.mark.requires_saxon
class TestUnwrapStepMultipleElements:
    """Test unwrapping multiple element types."""

    def test_unwrap_multiple_element_types(self):
        """Test unwrapping multiple different element types."""
        step = UnwrapStep(elements=[
            {"element_name": "seg"},
            {"element_name": "span"}
        ])
        input_xml = """<root>
            <p>
                <seg>Segment content</seg>
                <span>Span content</span>
            </p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        segs = result_tree.findall(".//seg")
        spans = result_tree.findall(".//span")
        assert len(segs) == 0
        assert len(spans) == 0
        # Content should be preserved
        assert "Segment content" in result
        assert "Span content" in result

    def test_unwrap_sequential_processing(self):
        """Test that elements are unwrapped sequentially."""
        step = UnwrapStep(elements=[
            {"element_name": "outer"},
            {"element_name": "middle"}
        ])
        input_xml = """<root>
            <outer>
                <middle>
                    <inner>Content</inner>
                </middle>
            </outer>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        # Both outer and middle should be removed
        assert len(result_tree.findall(".//outer")) == 0
        assert len(result_tree.findall(".//middle")) == 0
        # inner should remain
        assert len(result_tree.findall(".//inner")) == 1


@pytest.mark.unit
@pytest.mark.xslt
@pytest.mark.requires_saxon
class TestUnwrapStepEmptyElements:
    """Test UnwrapStep with empty elements list."""

    @pytest.mark.filterwarnings("ignore:An UnwrapStep with no elements:heipy.heiwarning.HeiWarning")
    def test_empty_elements_list_returns_unchanged(self):
        """Test that empty elements list returns input unchanged."""
        step = UnwrapStep(elements=[])
        input_xml = """<root>
            <seg>content</seg>
            <span>more</span>
        </root>"""
        result = step.execute(input_xml)

        # Should return input unchanged
        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.find("seg") is not None
        assert result_tree.find("span") is not None


@pytest.mark.unit
@pytest.mark.xslt
@pytest.mark.requires_saxon
class TestUnwrapStepWithNamespaces:
    """Test UnwrapStep with namespaced XML."""

    def test_unwrap_tei_elements(self):
        """Test unwrapping TEI elements with namespace."""
        step = UnwrapStep(elements=[{"element_name": "seg"}])
        input_xml = """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <text>
                <p><seg>Segmented text</seg> continues.</p>
            </text>
        </TEI>"""
        result = step.execute(input_xml)

        parser = HeiEditionsParser()
        result_tree = et.fromstring(result.encode('utf-8'), parser=parser)
        # seg should be unwrapped
        segs = result_tree.xpath("//tei:seg", namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
        assert len(segs) == 0
        # Text should be preserved
        assert "Segmented text" in result


@pytest.mark.unit
@pytest.mark.xslt
@pytest.mark.requires_saxon
class TestUnwrapStepWhitespaceHandling:
    """Test UnwrapStep whitespace preservation."""

    def test_preserve_whitespace_around_element(self):
        """Test that whitespace around unwrapped element is preserved."""
        step = UnwrapStep(elements=[{"element_name": "seg"}])
        input_xml = """<root>
            <p>Before  <seg>content</seg>  after</p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        p = result_tree.find("p")
        # Whitespace should be preserved
        text_content = et.tostring(p, encoding='unicode')
        # Check that whitespace patterns exist
        assert "Before" in text_content
        assert "content" in text_content
        assert "after" in text_content

    def test_preserve_whitespace_in_mixed_content(self):
        """Test whitespace preservation in mixed content."""
        step = UnwrapStep(elements=[{"element_name": "seg"}])
        input_xml = """<root>
            <p>Text <seg>wrapped</seg> more <b>bold</b> end</p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        # Should preserve overall structure and whitespace
        assert result_tree.find(".//b") is not None
        text_content = et.tostring(result_tree.find("p"), encoding='unicode', method='text')
        assert "Text" in text_content
        assert "wrapped" in text_content
        assert "bold" in text_content


@pytest.mark.unit
@pytest.mark.xslt
@pytest.mark.requires_saxon
class TestUnwrapStepXDMBatching:
    """Test UnwrapStep XDM batching functionality."""

    def test_output_xdm_for_batching(self, saxon_proc):
        """Test that output_xdm parameter works for batching."""
        step = UnwrapStep(elements=[{"element_name": "seg"}])
        input_xml = """<root>
            <p><seg>content</seg></p>
        </root>"""

        # Request XDM output for batching
        result = step.execute(input_xml, output_xdm=True, proc=saxon_proc)

        # Result should be XDM object, not string
        assert result is not None
        assert not isinstance(result, str)

    def test_input_xdm_for_batching(self, saxon_proc):
        """Test that input_xdm parameter works for batched execution."""
        # First step creates XDM
        step1 = UnwrapStep(elements=[{"element_name": "outer"}])
        input_xml = """<root>
            <outer><seg>content</seg></outer>
        </root>"""
        xdm_result = step1.execute(input_xml, output_xdm=True, proc=saxon_proc)

        # Second step uses XDM input
        step2 = UnwrapStep(elements=[{"element_name": "seg"}])
        final_result = step2.execute(input_xdm=xdm_result, output_xdm=False, proc=saxon_proc)

        # Final result should be string with both unwraps applied
        assert isinstance(final_result, str)
        assert "outer" not in final_result
        assert "seg" not in final_result
        assert "content" in final_result


@pytest.mark.unit
@pytest.mark.xslt
@pytest.mark.requires_saxon
class TestUnwrapStepEdgeCases:
    """Test edge cases and special scenarios."""

    def test_unwrap_empty_element(self):
        """Test unwrapping an empty element."""
        step = UnwrapStep(elements=[{"element_name": "seg"}])
        input_xml = """<root>
            <p>Before<seg/>After</p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        segs = result_tree.findall(".//seg")
        assert len(segs) == 0

    def test_unwrap_deeply_nested(self):
        """Test unwrapping deeply nested elements."""
        step = UnwrapStep(elements=[{"element_name": "seg"}])
        input_xml = """<root>
            <level1>
                <level2>
                    <level3>
                        <seg>Deep content</seg>
                    </level3>
                </level2>
            </level1>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        segs = result_tree.findall(".//seg")
        assert len(segs) == 0
        # Structure should be preserved
        assert result_tree.find(".//level1/level2/level3") is not None

    def test_unwrap_element_not_present(self):
        """Test unwrapping element type that doesn't exist."""
        step = UnwrapStep(elements=[{"element_name": "nonexistent"}])
        input_xml = """<root>
            <p>Some content</p>
        </root>"""
        result = step.execute(input_xml)

        # Should return mostly unchanged
        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.find("p") is not None

    def test_unwrap_with_complex_attributes(self):
        """Test unwrapping with complex attribute matching."""
        step = UnwrapStep(elements=[{
            "element_name": "seg",
            "attrib_name": "ana",
            "attrib_val": "hc:EditorialContent"
        }])
        input_xml = """<root xmlns:hc="https://example.org/hc">
            <p>
                <seg ana="hc:EditorialContent">Editorial</seg>
                <seg ana="hc:OriginalContent">Original</seg>
            </p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        # Only the editorial seg should be unwrapped
        segs = result_tree.findall(".//{https://example.org/hc}seg")
        if len(segs) > 0:
            # Check that editorial is gone but original remains
            ana_values = [seg.get("ana") for seg in segs]
            assert "hc:EditorialContent" not in ana_values
