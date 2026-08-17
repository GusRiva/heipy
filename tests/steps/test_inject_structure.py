"""Tests for inject structure step."""

from heipy.heipipe.step_library.semantic import inject_structure
from tests.helpers.xml_compare import assert_xml_equal

FIXTURES_DIR = "tests/fixtures/step_library/inject_structure/"

def test_basic(fixture_loader):
    # Initialize step
    step = inject_structure.get_step()
    # Load as pair using structured API (returns tuple of trees)
    input_tree, expected_tree = fixture_loader.load_step_pair(
        step.get_name(),
        variant='basic'
    )

    input_string = fixture_loader.tree_to_string(input_tree)
    step.add_parameter('structure_file_path', f'{FIXTURES_DIR}/structure_file_basic.xml')
    result_string = step.execute(input_string)

    assert_xml_equal(expected_tree, result_string)
