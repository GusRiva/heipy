"""Tests for resolve_facs_atts step."""

from heipy.heipipe.step_library import resolve_facs_atts
from heipy.heipipe.pipeline_library.sourcedoc import SourceDocPipe
from tests.helpers.xml_compare import vanilla_compare_flow, pipeline_compare_flow


def test_basic(fixture_loader):
    vanilla_compare_flow(resolve_facs_atts, fixture_loader)


def test_sourcedoc_pipeline(step_fixtures_dir):
    input_file = step_fixtures_dir / "resolve_facs_atts" / "input_basic.xml"
    expected_file = step_fixtures_dir / "resolve_facs_atts" / "expected_sourcedoc.xml"
    pipeline_compare_flow(SourceDocPipe(), input_file, expected_file)
