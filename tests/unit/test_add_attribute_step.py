"""
Tests for AddAttribute step class.

AddAttribute adds attributes to elements matching an XPath expression.
"""

import pytest
from lxml import etree as et

from heipy.heipipe.steps import AddAttribute
from heipy.parsers import HeiEditionsParser


@pytest.mark.unit
class TestAddAttributeInitialization:
    """Test AddAttribute initialization."""

    def test_init_with_required_params(self):
        """Test initialization with required parameters."""
        step = AddAttribute(
            match="//p",
            att_name="type",
            att_val="paragraph",
            name="add_attr"
        )
        assert step.get_name() == "add_attr"

    def test_init_without_name(self):
        """Test initialization without name."""
        step = AddAttribute(match="//p", att_name="type", att_val="test")
        assert step.get_name() == "__AddAttribute__"


@pytest.mark.unit
class TestAddAttributeBasicOperation:
    """Test basic attribute addition."""

    def test_add_attribute_to_single_element(self):
        """Test adding attribute to a single element."""
        step = AddAttribute(match="//p", att_name="type", att_val="paragraph")
        input_xml = """<root>
            <p>Test paragraph</p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        p = result_tree.find(".//p")
        assert p.get("type") == "paragraph"

    def test_add_attribute_to_multiple_elements(self):
        """Test adding attribute to multiple matching elements."""
        step = AddAttribute(match="//p", att_name="class", att_val="text")
        input_xml = """<root>
            <p>First paragraph</p>
            <p>Second paragraph</p>
            <p>Third paragraph</p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        paragraphs = result_tree.findall(".//p")
        assert len(paragraphs) == 3
        for p in paragraphs:
            assert p.get("class") == "text"

    def test_add_attribute_no_matching_elements(self):
        """Test adding attribute when no elements match XPath."""
        step = AddAttribute(match="//note", att_name="type", att_val="editorial")
        input_xml = """<root>
            <p>No notes here</p>
        </root>"""
        result = step.execute(input_xml)

        # Should return unchanged
        result_tree = et.fromstring(result.encode('utf-8'))
        p = result_tree.find(".//p")
        assert p.get("type") is None


@pytest.mark.unit
class TestAddAttributeXPathExpressions:
    """Test various XPath expressions."""

    def test_xpath_root_descendants(self):
        """Test XPath matching all descendants."""
        step = AddAttribute(match="//div", att_name="processed", att_val="true")
        input_xml = """<root>
            <div>Level 1</div>
            <section>
                <div>Level 2</div>
            </section>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        divs = result_tree.findall(".//div")
        assert len(divs) == 2
        for div in divs:
            assert div.get("processed") == "true"

    def test_xpath_with_predicate(self):
        """Test XPath with predicate."""
        step = AddAttribute(match="//p[@n]", att_name="numbered", att_val="yes")
        input_xml = """<root>
            <p>No number</p>
            <p n="1">Numbered</p>
            <p n="2">Also numbered</p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        paragraphs = result_tree.findall(".//p")
        # First paragraph should not have the new attribute
        assert paragraphs[0].get("numbered") is None
        # Second and third should have it
        assert paragraphs[1].get("numbered") == "yes"
        assert paragraphs[2].get("numbered") == "yes"

    def test_xpath_specific_path(self):
        """Test XPath with specific path."""
        step = AddAttribute(match="/root/p", att_name="level", att_val="top")
        input_xml = """<root>
            <p>Top level</p>
            <div>
                <p>Nested</p>
            </div>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        # Only top-level p should have attribute
        top_p = result_tree.find("p")
        nested_p = result_tree.find(".//div/p")
        assert top_p.get("level") == "top"
        assert nested_p.get("level") is None


@pytest.mark.unit
class TestAddAttributeWithNamespaces:
    """Test AddAttribute with namespaced XML."""

    def test_add_attribute_tei_elements(self):
        """Test adding attributes to TEI elements."""
        step = AddAttribute(
            match="//tei:p",
            att_name="type",
            att_val="prose"
        )
        input_xml = """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <text>
                <body>
                    <p>First paragraph</p>
                    <p>Second paragraph</p>
                </body>
            </text>
        </TEI>"""
        result = step.execute(input_xml)

        parser = HeiEditionsParser()
        result_tree = et.fromstring(result.encode('utf-8'), parser=parser)
        paragraphs = result_tree.xpath("//tei:p", namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
        assert len(paragraphs) == 2
        for p in paragraphs:
            assert p.get("type") == "prose"


@pytest.mark.unit
class TestAddAttributeOverwriting:
    """Test attribute overwriting behavior."""

    def test_overwrite_existing_attribute(self):
        """Test that existing attribute is overwritten."""
        step = AddAttribute(match="//p", att_name="type", att_val="new_type")
        input_xml = """<root>
            <p type="old_type">Paragraph</p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        p = result_tree.find(".//p")
        assert p.get("type") == "new_type"

    def test_preserve_other_attributes(self):
        """Test that other attributes are preserved."""
        step = AddAttribute(match="//p", att_name="class", att_val="added")
        input_xml = """<root>
            <p id="p1" n="1">Paragraph</p>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        p = result_tree.find(".//p")
        assert p.get("class") == "added"
        assert p.get("id") == "p1"
        assert p.get("n") == "1"


@pytest.mark.unit
class TestAddAttributeValueTypes:
    """Test different attribute value types."""

    def test_string_value(self):
        """Test adding string value."""
        step = AddAttribute(match="//p", att_name="type", att_val="text")
        input_xml = "<root><p>Test</p></root>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.find("p").get("type") == "text"

    def test_numeric_value(self):
        """Test adding numeric value (converted to string)."""
        step = AddAttribute(match="//p", att_name="count", att_val="42")
        input_xml = "<root><p>Test</p></root>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.find("p").get("count") == "42"

    def test_empty_string_value(self):
        """Test adding empty string value."""
        step = AddAttribute(match="//p", att_name="empty", att_val="")
        input_xml = "<root><p>Test</p></root>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.find("p").get("empty") == ""


@pytest.mark.unit
class TestAddAttributeEdgeCases:
    """Test edge cases and special scenarios."""

    def test_add_to_root_element(self):
        """Test adding attribute to root element."""
        step = AddAttribute(match="/root", att_name="version", att_val="1.0")
        input_xml = "<root><p>Content</p></root>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.get("version") == "1.0"

    def test_add_to_empty_element(self):
        """Test adding attribute to empty element."""
        step = AddAttribute(match="//empty", att_name="filled", att_val="no")
        input_xml = "<root><empty/></root>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.find("empty").get("filled") == "no"

    def test_add_to_element_with_children(self):
        """Test adding attribute to element with children."""
        step = AddAttribute(match="//div", att_name="has_children", att_val="true")
        input_xml = """<root>
            <div>
                <p>Child 1</p>
                <p>Child 2</p>
            </div>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        div = result_tree.find("div")
        assert div.get("has_children") == "true"
        # Children should be unchanged
        assert len(div) == 2

    def test_special_characters_in_value(self):
        """Test attribute value with special characters."""
        step = AddAttribute(match="//p", att_name="data", att_val="<>&\"'")
        input_xml = "<root><p>Test</p></root>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        # Special characters should be properly encoded/decoded
        assert result_tree.find("p").get("data") == "<>&\"'"
