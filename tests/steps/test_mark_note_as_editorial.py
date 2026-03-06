"""Tests for mark_note_as_editorial step."""


from tests.helpers.xml_compare import xml_equal
from heipy.heipipe.step_library import mark_note_as_editorial

def test_two_classes(fixture_loader):
    """Test marking notes as editorial with two note classes.

    This test verifies that notes with ana attributes matching the configured
    note_classes parameter get marked with 'hc:EditorialContent' class.
    """

    # Initialize step with parameters
    step = mark_note_as_editorial.get_step()
    step.add_parameter('note_classes', 'hc:TextCriticalNote hc:Comment')

    # Load fixtures using flexible API (returns ElementTrees)
    input_tree = fixture_loader.load('mark_note_as_editorial/input_two_classes.xml')
    expected_tree = fixture_loader.load('mark_note_as_editorial/expected_two_classes.xml')

    input_string = fixture_loader.tree_to_string(input_tree)
    result_string = step.execute(input_string)

    assert xml_equal(result_string, expected_tree)


def test_two_classes_structured_api(fixture_loader):
    """Same test using structured API for comparison.

    This demonstrates the alternative load_step_pair API which is useful
    when following the standard input/expected naming convention.
    """

    # Initialize step
    step = mark_note_as_editorial.get_step()
    step.add_parameter('note_classes', 'hc:TextCriticalNote hc:Comment')

    # Load as pair using structured API (returns tuple of trees)
    input_tree, expected_tree = fixture_loader.load_step_pair(
        'mark_note_as_editorial',
        variant='two_classes'
    )

    # Convert and execute
    input_string = fixture_loader.tree_to_string(input_tree)
    result_string = step.execute(input_string)

    # Assert equality
    assert xml_equal(result_string, expected_tree)
