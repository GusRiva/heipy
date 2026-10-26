"""
Tests for Pipeline class.

Covers the output formats of Pipeline.execute() and step lookup by name.
"""

import pytest
from lxml import etree as et

from heipy.heipipe.steps import DeleteStep, Pipeline

INPUT_XML = '<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><p>Text<note>Note</note> ünd mehr</p></text></TEI>'


@pytest.fixture
def pipeline():
    return Pipeline(steps=[DeleteStep(elements=["tei:note"], name="delete_note")], name="test_pipe")


@pytest.mark.unit
class TestPipelineOutputFormats:
    """Test the output_format argument of Pipeline.execute()."""

    def test_output_str_is_default(self, pipeline):
        result = pipeline.execute(INPUT_XML, input_format="xml_string")
        assert isinstance(result, str)
        assert "<note" not in result
        assert "ünd mehr" in result

    def test_output_etree(self, pipeline):
        result = pipeline.execute(INPUT_XML, input_format="xml_string", output_format="etree")
        assert isinstance(result, et._ElementTree)
        root = result.getroot()
        assert root.tag == "{http://www.tei-c.org/ns/1.0}TEI"
        assert root.find(".//{http://www.tei-c.org/ns/1.0}note") is None

    def test_output_bytes(self, pipeline):
        result = pipeline.execute(INPUT_XML, input_format="xml_string", output_format="bytes")
        assert isinstance(result, bytes)
        assert b"<note" not in result
        assert "ünd mehr".encode("utf-8") in result

    def test_all_output_formats_agree(self, pipeline):
        result_str = pipeline.execute(INPUT_XML, input_format="xml_string")
        result_etree = pipeline.execute(INPUT_XML, input_format="xml_string", output_format="etree")
        result_bytes = pipeline.execute(INPUT_XML, input_format="xml_string", output_format="bytes")
        assert result_bytes == result_str.encode("utf-8")
        assert et.tostring(result_etree) == et.tostring(et.fromstring(result_bytes))

    def test_invalid_output_format_raises(self, pipeline):
        with pytest.raises(ValueError):
            pipeline.execute(INPUT_XML, input_format="xml_string", output_format="html")


@pytest.mark.unit
class TestPipelineGetStepByName:
    """Test Pipeline.get_step_by_name()."""

    def test_existing_step(self, pipeline):
        assert pipeline.get_step_by_name("delete_note") is pipeline.get_steps()[0]

    def test_missing_step_returns_none(self, pipeline):
        assert pipeline.get_step_by_name("does_not_exist") is None
