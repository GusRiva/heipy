"""
Tests for PythonStep class.

PythonStep executes custom Python functions on XML documents,
allowing for complex transformations not easily expressed in XSLT.
"""

import pytest
from lxml import etree as et

from heipy.heipipe.steps import PythonStep
from heipy.parsers import HeiEditionsParser
from heipy.namespaces import ns


@pytest.mark.unit
@pytest.mark.python_step
class TestPythonStepInitialization:
    """Test PythonStep initialization."""

    def test_init_with_function(self):
        """Test initialization with a function."""
        def dummy_func(tree, parameters=None):
            return tree

        step = PythonStep(funct=dummy_func, name="test_step")
        assert step.get_name() == "test_step"

    def test_init_without_name(self):
        """Test initialization without name."""
        def dummy_func(tree, parameters=None):
            return tree

        step = PythonStep(funct=dummy_func)
        assert step.get_name() == "__PythonStep__"

    def test_init_with_parameters(self):
        """Test initialization with parameters."""
        def dummy_func(tree, parameters=None):
            return tree

        params = {"key": "value"}
        step = PythonStep(funct=dummy_func, parameters=params)
        assert step.get_parameters() == params


@pytest.mark.unit
@pytest.mark.python_step
class TestPythonStepExecution:
    """Test PythonStep execution."""

    def test_execute_simple_function(self):
        """Test executing a simple function."""
        def simple_func(tree, parameters=None):
            # Add a test attribute
            root = tree.getroot()
            root.set("modified", "true")
            return tree

        step = PythonStep(funct=simple_func)
        input_xml = "<root/>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.get("modified") == "true"

    def test_execute_with_text_content(self):
        """Test executing function on XML with text content."""
        def uppercase_text(tree, parameters=None):
            root = tree.getroot()
            if root.text:
                root.text = root.text.upper()
            return tree

        step = PythonStep(funct=uppercase_text)
        input_xml = "<root>hello world</root>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.text == "HELLO WORLD"

    def test_execute_preserves_children(self):
        """Test that execution preserves child elements."""
        def add_attribute(tree, parameters=None):
            root = tree.getroot()
            root.set("processed", "yes")
            return tree

        step = PythonStep(funct=add_attribute)
        input_xml = "<root><child>content</child><child>more</child></root>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.get("processed") == "yes"
        assert len(result_tree) == 2
        assert result_tree[0].tag == "child"


@pytest.mark.unit
@pytest.mark.python_step
class TestPythonStepWithParameters:
    """Test PythonStep parameter passing."""

    def test_execute_with_single_parameter(self):
        """Test executing with a single parameter."""
        def use_parameter(tree, parameters):
            root = tree.getroot()
            value = parameters.get("test_param")
            root.set("result", value)
            return tree

        step = PythonStep(funct=use_parameter, parameters={"test_param": "expected_value"})
        input_xml = "<root/>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.get("result") == "expected_value"

    def test_execute_with_multiple_parameters(self):
        """Test executing with multiple parameters."""
        def use_multiple_params(tree, parameters):
            root = tree.getroot()
            param1 = parameters.get("key1")
            param2 = parameters.get("key2")
            root.set("value1", param1)
            root.set("value2", param2)
            return tree

        step = PythonStep(
            funct=use_multiple_params,
            parameters={"key1": "val1", "key2": "val2"}
        )
        input_xml = "<root/>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.get("value1") == "val1"
        assert result_tree.get("value2") == "val2"

    def test_execute_without_parameters_optional(self):
        """Test executing function where parameters are optional."""
        def optional_param_func(tree, parameters=None):
            root = tree.getroot()
            if parameters:
                root.set("with_params", "true")
            else:
                root.set("with_params", "false")
            return tree

        step = PythonStep(funct=optional_param_func)
        input_xml = "<root/>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.get("with_params") == "false"


@pytest.mark.unit
@pytest.mark.python_step
class TestPythonStepComplexTransformations:
    """Test PythonStep with complex transformations."""

    def test_add_child_elements(self):
        """Test function that adds child elements."""
        def add_children(tree, parameters=None):
            root = tree.getroot()
            for i in range(3):
                child = et.SubElement(root, "child")
                child.set("id", str(i))
                child.text = f"Child {i}"
            return tree

        step = PythonStep(funct=add_children)
        input_xml = "<root/>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        children = result_tree.findall("child")
        assert len(children) == 3
        assert children[0].get("id") == "0"
        assert children[2].text == "Child 2"

    def test_modify_nested_elements(self):
        """Test function that modifies nested elements."""
        def modify_nested(tree, parameters=None):
            # Find all nested elements and add a class
            root = tree.getroot()
            for elem in root.iter():
                if elem.tag != root.tag:
                    elem.set("modified", "true")
            return tree

        step = PythonStep(funct=modify_nested)
        input_xml = """<root>
            <level1>
                <level2>
                    <level3>content</level3>
                </level2>
            </level1>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        level1 = result_tree.find("level1")
        level2 = level1.find("level2")
        level3 = level2.find("level3")

        assert level1.get("modified") == "true"
        assert level2.get("modified") == "true"
        assert level3.get("modified") == "true"

    def test_remove_elements(self):
        """Test function that removes elements."""
        def remove_empty(tree, parameters=None):
            # Remove elements with no text and no children
            root = tree.getroot()
            for elem in list(root.iter()):
                if elem != root and not elem.text and len(elem) == 0:
                    parent = elem.getparent()
                    if parent is not None:
                        parent.remove(elem)
            return tree

        step = PythonStep(funct=remove_empty)
        input_xml = """<root>
            <keep>text</keep>
            <remove/>
            <keep><child/></keep>
            <remove/>
        </root>"""
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        keep_elements = result_tree.findall("keep")
        remove_elements = result_tree.findall("remove")

        assert len(keep_elements) == 2
        assert len(remove_elements) == 0


@pytest.mark.unit
@pytest.mark.python_step
class TestPythonStepWithNamespaces:
    """Test PythonStep with namespaced XML."""

    def test_execute_with_tei_namespace(self):
        """Test executing on TEI XML with namespace."""
        def add_id_to_paragraphs(tree, parameters=None):
            # Find all TEI paragraphs and add IDs
            root = tree.getroot()
            tei_ns = "http://www.tei-c.org/ns/1.0"
            for idx, p in enumerate(root.iter(f"{{{tei_ns}}}p")):
                p.set(f"{{{tei_ns}}}n", str(idx + 1))
            return tree

        step = PythonStep(funct=add_id_to_paragraphs)
        input_xml = """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <text>
                <body>
                    <p>First</p>
                    <p>Second</p>
                </body>
            </text>
        </TEI>"""
        result = step.execute(input_xml)

        parser = HeiEditionsParser()
        result_tree = et.fromstring(result.encode('utf-8'), parser=parser)
        paragraphs = result_tree.xpath("//tei:p", namespaces={"tei": "http://www.tei-c.org/ns/1.0"})

        assert len(paragraphs) == 2
        assert paragraphs[0].get("{http://www.tei-c.org/ns/1.0}n") == "1"
        assert paragraphs[1].get("{http://www.tei-c.org/ns/1.0}n") == "2"


@pytest.mark.unit
@pytest.mark.python_step
class TestPythonStepReturnValues:
    """Test PythonStep return value handling."""

    def test_function_returns_modified_root(self):
        """Test that function's returned root is used."""
        def return_modified(tree, parameters=None):
            root = tree.getroot()
            root.set("marker", "modified")
            return tree

        step = PythonStep(funct=return_modified)
        input_xml = "<root/>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.get("marker") == "modified"

    def test_function_returns_new_tree(self):
        """Test function that returns a completely new tree."""
        def return_new_tree(tree, parameters=None):
            # Create a new tree
            new_root = et.Element("new_root")
            new_root.set("type", "replacement")
            return et.ElementTree(new_root)

        step = PythonStep(funct=return_new_tree)
        input_xml = "<old_root/>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.tag == "new_root"
        assert result_tree.get("type") == "replacement"


@pytest.mark.unit
@pytest.mark.python_step
class TestPythonStepSerialization:
    """Test PythonStep serialization behavior."""

    def test_execute_with_serial_flag(self, tmp_path, monkeypatch):
        """Test execution with serial flag saves intermediate result."""
        monkeypatch.chdir(tmp_path)
        tmp_dir = tmp_path / "tmp"
        tmp_dir.mkdir()

        def simple_transform(tree, parameters=None):
            root = tree.getroot()
            root.set("processed", "yes")
            return tree

        step = PythonStep(funct=simple_transform, name="test_step", serial=True)
        step.set_index(0)
        input_xml = "<root/>"

        result = step.execute(input_xml, serial=True)

        # Check that file was created with index in filename
        expected_file = tmp_dir / "0_test_step.xml"
        assert expected_file.exists()


@pytest.mark.unit
@pytest.mark.python_step
class TestPythonStepEdgeCases:
    """Test edge cases and special scenarios."""

    def test_function_with_no_parameters_argument(self):
        """Test function that doesn't accept parameters argument."""
        def no_param_arg(tree):
            root = tree.getroot()
            root.set("simple", "true")
            return tree

        step = PythonStep(funct=no_param_arg)
        input_xml = "<root/>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.get("simple") == "true"

    def test_whitespace_preservation(self):
        """Test that whitespace is preserved through transformation."""
        def identity(tree, parameters=None):
            return tree

        step = PythonStep(funct=identity)
        input_xml = "<root>  text with  spaces  </root>"
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.text == "  text with  spaces  "

    def test_function_modifies_attributes(self):
        """Test function that modifies existing attributes."""
        def modify_attributes(tree, parameters=None):
            root = tree.getroot()
            for elem in root.iter():
                if 'id' in elem.attrib:
                    elem.set('id', f"modified_{elem.get('id')}")
            return tree

        step = PythonStep(funct=modify_attributes)
        input_xml = '<root id="r1"><child id="c1"/></root>'
        result = step.execute(input_xml)

        result_tree = et.fromstring(result.encode('utf-8'))
        assert result_tree.get("id") == "modified_r1"
        assert result_tree[0].get("id") == "modified_c1"
