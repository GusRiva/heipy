"""
Tests for BaseStep class.

Since BaseStep is abstract, we test it through concrete implementations
like XsltStep, focusing on the base functionality provided by BaseStep.
"""

import pytest
from pathlib import Path
from lxml import etree as et

from heipy.heipipe.steps import BaseStep, XsltStep
from heipy.heiwarning import HeiDeprecationWarning


@pytest.mark.unit
@pytest.mark.filterwarnings("ignore:An XsltStep with no XSLT files:heipy.heiwarning.HeiWarning")
class TestBaseStepInitialization:
    """Test BaseStep initialization and basic properties."""

    def test_init_with_name(self):
        """Test initialization with explicit name."""
        step = XsltStep(files=[], name="test_step")
        assert step.get_name() == "test_step"

    def test_init_without_name(self):
        """Test initialization without name defaults to '__XsltStep__'."""
        step = XsltStep(files=[])
        assert step.get_name() == "__XsltStep__"

    def test_init_with_description(self):
        """Test initialization with description."""
        step = XsltStep(files=[], name="test", desc="Test description")
        assert step.get_desc() == "Test description"

    def test_init_without_description(self):
        """Test initialization without description defaults to None."""
        step = XsltStep(files=[])
        assert step.get_desc() is None

    def test_init_with_parameters(self):
        """Test initialization with parameters."""
        # Test new dict format
        params = {"key1": "value1", "key2": "value2"}
        step = XsltStep(files=[], parameters=params)
        assert step.get_parameters() == params
        # Test legacy list format (with deprecation warning)
        params_list = [{"key1": "value1"}, {"key2": "value2"}]
        with pytest.warns(HeiDeprecationWarning, match="list of dictionaries is deprecated"):
            step = XsltStep(files=[], parameters=params_list)
        assert step.get_parameters() == {"key1": "value1", "key2": "value2"}

    def test_init_without_parameters(self):
        """Test initialization without parameters defaults to empty dict."""
        step = XsltStep(files=[])
        assert step.get_parameters() == {}

    def test_init_parameters_none(self):
        """Test initialization with None parameters converts to empty dict."""
        step = XsltStep(files=[], parameters=None)
        assert step.get_parameters() == {}


@pytest.mark.unit
@pytest.mark.filterwarnings("ignore:An XsltStep with no XSLT files:heipy.heiwarning.HeiWarning")
class TestBaseStepIndexManagement:
    """Test index management in BaseStep."""

    def test_default_index_is_none(self):
        """Test that default index is None."""
        step = XsltStep(files=[])
        assert step.get_index() is None

    def test_set_index(self):
        """Test setting index."""
        step = XsltStep(files=[])
        step.set_index(5)
        assert step.get_index() == 5

    def test_set_index_zero(self):
        """Test setting index to zero."""
        step = XsltStep(files=[])
        step.set_index(0)
        assert step.get_index() == 0

    @pytest.mark.parametrize("index", [0, 1, 5, 10, 100])
    def test_set_various_indices(self, index):
        """Test setting various index values."""
        step = XsltStep(files=[])
        step.set_index(index)
        assert step.get_index() == index


@pytest.mark.unit
@pytest.mark.filterwarnings("ignore:An XsltStep with no XSLT files:heipy.heiwarning.HeiWarning")
class TestBaseStepSerialFlag:
    """Test serial flag management in BaseStep."""

    def test_default_serial_is_false(self):
        """Test that default serial flag is False."""
        step = XsltStep(files=[])
        assert step.get_serial() is False

    def test_init_with_serial_true(self):
        """Test initialization with serial=True."""
        step = XsltStep(files=[], serial=True)
        assert step.get_serial() is True

    def test_set_serial_true(self):
        """Test setting serial to True."""
        step = XsltStep(files=[])
        step.set_serial(True)
        assert step.get_serial() is True

    def test_set_serial_false(self):
        """Test setting serial to False."""
        step = XsltStep(files=[], serial=True)
        step.set_serial(False)
        assert step.get_serial() is False


@pytest.mark.unit
@pytest.mark.filterwarnings("ignore:An XsltStep with no XSLT files:heipy.heiwarning.HeiWarning")
class TestBaseStepParameterManagement:
    """Test parameter management in BaseStep."""

    def test_get_parameters_empty(self):
        """Test getting parameters when empty."""
        step = XsltStep(files=[])
        assert step.get_parameters() == {}

    def test_add_parameter(self):
        """Test adding a parameter."""
        step = XsltStep(files=[])
        step.add_parameter("key", "value")
        assert len(step.get_parameters()) == 1
        assert step.get_parameters()["key"] == "value"

    def test_add_multiple_parameters(self):
        """Test adding multiple parameters."""
        step = XsltStep(files=[])
        step.add_parameter("key1", "value1")
        step.add_parameter("key2", "value2")
        step.add_parameter("key3", "value3")

        params = step.get_parameters()
        assert len(params) == 3
        assert params["key1"] == "value1"
        assert params["key2"] == "value2"
        assert params["key3"] == "value3"

    def test_add_parameter_with_dict_deprecated(self):
        """Test adding parameter with dict format (deprecated)."""
        step = XsltStep(files=[])
        with pytest.warns(HeiDeprecationWarning, match="Passing a dictionary to add_parameter is deprecated"):
            step.add_parameter({"key": "value"})
        assert step.get_parameters()["key"] == "value"

    def test_add_parameter_with_dict_multiple_keys(self):
        """Test adding parameter with dict containing multiple keys (deprecated)."""
        step = XsltStep(files=[])
        with pytest.warns(HeiDeprecationWarning):
            step.add_parameter({"key1": "value1", "key2": "value2"})
        assert step.get_parameters()["key1"] == "value1"
        assert step.get_parameters()["key2"] == "value2"

    def test_add_parameters(self):
        """Test adding multiple parameters at once using add_parameters()."""
        step = XsltStep(files=[])
        step.add_parameters({
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        })

        params = step.get_parameters()
        assert len(params) == 3
        assert params["key1"] == "value1"
        assert params["key2"] == "value2"
        assert params["key3"] == "value3"

    def test_add_parameters_to_existing(self):
        """Test that add_parameters() adds to existing parameters."""
        step = XsltStep(files=[], parameters={"existing": "param"})
        step.add_parameters({"new1": "value1", "new2": "value2"})

        params = step.get_parameters()
        assert len(params) == 3
        assert params["existing"] == "param"
        assert params["new1"] == "value1"
        assert params["new2"] == "value2"

    def test_add_parameters_overwrites_existing_keys(self):
        """Test that add_parameters() overwrites existing keys."""
        step = XsltStep(files=[], parameters={"key1": "old_value"})
        step.add_parameters({"key1": "new_value", "key2": "value2"})

        params = step.get_parameters()
        assert params["key1"] == "new_value"
        assert params["key2"] == "value2"

    def test_add_parameters_empty_dict(self):
        """Test add_parameters() with empty dict."""
        step = XsltStep(files=[], parameters={"existing": "param"})
        step.add_parameters({})

        params = step.get_parameters()
        assert len(params) == 1
        assert params["existing"] == "param"

    def test_add_parameters_type_error(self):
        """Test that add_parameters() raises TypeError for non-dict input."""
        step = XsltStep(files=[])
        with pytest.raises(TypeError, match="parameters must be a dict"):
            step.add_parameters("not a dict")
        with pytest.raises(TypeError, match="parameters must be a dict"):
            step.add_parameters([{"key": "value"}])

    def test_set_parameters(self):
        """Test setting parameters dict."""
        step = XsltStep(files=[])
        new_params = {"key1": "value1", "key2": "value2"}
        step.set_parameters(new_params)
        assert step.get_parameters() == new_params

    def test_set_parameters_replaces_existing(self):
        """Test that set_parameters replaces existing parameters."""
        step = XsltStep(files=[], parameters={"old": "param"})
        new_params = {"new": "param"}
        step.set_parameters(new_params)
        assert step.get_parameters() == new_params
        assert "old" not in step.get_parameters()


@pytest.mark.unit
@pytest.mark.filterwarnings("ignore:An XsltStep with no XSLT files:heipy.heiwarning.HeiWarning")
class TestBaseStepParameterByName:
    """Test parameter retrieval and setting by name."""

    def test_get_parameter_by_name_not_found(self):
        """Test getting parameter that doesn't exist returns None."""
        step = XsltStep(files=[])
        assert step.get_parameter_by_name("nonexistent") is None

    def test_get_parameter_by_name_found(self):
        """Test getting existing parameter by name."""
        step = XsltStep(files=[], parameters={"key": "value"})
        assert step.get_parameter_by_name("key") == "value"

    def test_get_parameter_by_name_first_match(self):
        """Test that parameter is returned when key exists."""
        step = XsltStep(files=[], parameters={"key": "value"})
        assert step.get_parameter_by_name("key") == "value"

    def test_set_parameter_by_name_new(self):
        """Test setting a new parameter by name (deprecated)."""
        step = XsltStep(files=[])
        with pytest.warns(HeiDeprecationWarning, match="set_parameter_by_name\\(\\) is deprecated"):
            step.set_parameter_by_name("new_key", "new_value")

        assert step.get_parameter_by_name("new_key") == "new_value"
        assert step.get_parameters()["new_key"] == "new_value"

    def test_set_parameter_by_name_existing(self):
        """Test updating an existing parameter by name (deprecated)."""
        step = XsltStep(files=[], parameters={"key": "old_value"})
        with pytest.warns(HeiDeprecationWarning, match="set_parameter_by_name\\(\\) is deprecated"):
            step.set_parameter_by_name("key", "new_value")

        assert step.get_parameter_by_name("key") == "new_value"
        assert step.get_parameters()["key"] == "new_value"

    def test_set_parameter_by_name_multiple_keys(self):
        """Test setting parameters when multiple keys exist (deprecated)."""
        step = XsltStep(files=[], parameters={"key1": "value1", "key2": "value2"})
        with pytest.warns(HeiDeprecationWarning):
            step.set_parameter_by_name("key3", "value3")

        assert len(step.get_parameters()) == 3
        assert step.get_parameter_by_name("key3") == "value3"

    @pytest.mark.parametrize("value", [
        "string_value",
        123,
        True,
        False,
        None,
        {"nested": "dict"},
        ["list", "of", "items"]
    ])
    def test_set_parameter_various_value_types(self, value):
        """Test setting parameters with various value types (deprecated method)."""
        step = XsltStep(files=[])
        with pytest.warns(HeiDeprecationWarning):
            step.set_parameter_by_name("key", value)
        assert step.get_parameter_by_name("key") == value

    def test_set_parameter_new(self):
        """Test setting a new parameter using set_parameter() (recommended)."""
        step = XsltStep(files=[])
        step.set_parameter("new_key", "new_value")

        assert step.get_parameter_by_name("new_key") == "new_value"
        assert step.get_parameters()["new_key"] == "new_value"

    def test_set_parameter_existing(self):
        """Test updating an existing parameter using set_parameter() (recommended)."""
        step = XsltStep(files=[], parameters={"key": "old_value"})
        step.set_parameter("key", "new_value")

        assert step.get_parameter_by_name("key") == "new_value"
        assert step.get_parameters()["key"] == "new_value"

    @pytest.mark.parametrize("value", [
        "string_value",
        123,
        True,
        False,
        None,
        {"nested": "dict"},
        ["list", "of", "items"]
    ])
    def test_set_parameter_various_value_types_new_method(self, value):
        """Test setting parameters with various value types using set_parameter()."""
        step = XsltStep(files=[])
        step.set_parameter("key", value)
        assert step.get_parameter_by_name("key") == value


@pytest.mark.unit
@pytest.mark.filterwarnings("ignore:An XsltStep with no XSLT files:heipy.heiwarning.HeiWarning")
class TestBaseStepSerialization:
    """Test serialization functionality in BaseStep."""

    def test_serialize_creates_file(self, tmp_path, monkeypatch):
        """Test that _serialize creates a file."""
        # Change working directory to tmp_path for this test
        monkeypatch.chdir(tmp_path)

        # Create tmp directory
        tmp_dir = tmp_path / "tmp"
        tmp_dir.mkdir()

        step = XsltStep(files=[], name="test_step", serial=True)
        step.set_index(0)
        xml_string = "<root>test content</root>"

        # Call serialize with default filename (uses tmp/{index}_{name}.xml)
        step._serialize(xml_string)

        # Check file was created with default naming
        expected_file = tmp_dir / "0_test_step.xml"
        assert expected_file.exists()

    def test_serialize_file_content(self, tmp_path, monkeypatch):
        """Test that serialized file contains correct content."""
        monkeypatch.chdir(tmp_path)
        tmp_dir = tmp_path / "tmp"
        tmp_dir.mkdir()

        step = XsltStep(files=[], name="test_step", serial=True)
        step.set_index(1)
        xml_string = "<root>test content</root>"

        step._serialize(xml_string)

        expected_file = tmp_dir / "1_test_step.xml"
        content = expected_file.read_text(encoding="utf-8")
        assert xml_string in content

    def test_serialize_with_index(self, tmp_path, monkeypatch):
        """Test serialization with step index in filename."""
        monkeypatch.chdir(tmp_path)
        tmp_dir = tmp_path / "tmp"
        tmp_dir.mkdir()

        step = XsltStep(files=[], name="test_step", serial=True)
        step.set_index(5)
        xml_string = "<root>test</root>"

        step._serialize(xml_string)

        expected_file = tmp_dir / "5_test_step.xml"
        assert expected_file.exists()


@pytest.mark.unit
@pytest.mark.filterwarnings("ignore:An XsltStep with no XSLT files:heipy.heiwarning.HeiWarning")
class TestBaseStepStringRepresentation:
    """Test string representation of BaseStep."""

    def test_str_with_name(self):
        """Test __str__ with named step."""
        step = XsltStep(files=[], name="my_step")
        assert "my_step" in str(step)

    def test_str_without_name(self):
        """Test __str__ with unnamed step."""
        step = XsltStep(files=[])
        step_str = str(step)
        assert "__XsltStep__" in step_str or "XsltStep" in step_str


@pytest.mark.unit
@pytest.mark.filterwarnings("ignore:An XsltStep with no XSLT files:heipy.heiwarning.HeiWarning")
class TestBaseStepEdgeCases:
    """Test edge cases and error conditions."""

    def test_parameter_with_none_value(self):
        """Test adding parameter with None value."""
        step = XsltStep(files=[])
        step.add_parameter("key", None)
        assert step.get_parameters()["key"] is None

    def test_set_parameter_empty_string_key(self):
        """Test setting parameter with empty string as key."""
        step = XsltStep(files=[])
        step.set_parameter_by_name("", "value")
        assert step.get_parameter_by_name("") == "value"

    def test_multiple_parameters_same_name(self):
        """Test behavior with setting same key multiple times - last one wins."""
        step = XsltStep(files=[], parameters={"key": "value1", "other": "value3"})
        step.set_parameter_by_name("key", "value2")
        # With dict, last set value wins
        assert step.get_parameter_by_name("key") == "value2"
        assert step.get_parameter_by_name("other") == "value3"

    def test_set_parameter_updates_value(self):
        """Test that set_parameter_by_name updates the value."""
        step = XsltStep(files=[], parameters={"key": "value1"})
        step.set_parameter_by_name("key", "updated")

        params = step.get_parameters()
        assert params["key"] == "updated"
