"""Tests for final_cleanup."""

from heipy.heipipe.step_library.semantic import final_cleanup

from tests.helpers.xml_compare import assert_xml_equal, vanilla_compare_flow


def test_basic(fixture_loader):
    """By default, tei:standOff is removed."""
    vanilla_compare_flow(final_cleanup, fixture_loader)


def test_keep_standOff(fixture_loader):
    """With keep_standOff=True, tei:standOff is kept unchanged."""
    step = final_cleanup.get_step()
    step.add_parameter('keep_standOff', True)

    input_tree = fixture_loader.load('final_cleanup/input_basic.xml')
    expected_tree = fixture_loader.load('final_cleanup/expected_keep_standOff.xml')

    result_string = step.execute(fixture_loader.tree_to_string(input_tree))

    assert_xml_equal(expected_tree, result_string)


def test_keep_standOff_false(fixture_loader):
    """An explicit keep_standOff=False behaves like the default."""
    step = final_cleanup.get_step()
    step.add_parameter('keep_standOff', False)

    input_tree, expected_tree = fixture_loader.load_step_pair('final_cleanup', variant='basic')

    result_string = step.execute(fixture_loader.tree_to_string(input_tree))

    assert_xml_equal(expected_tree, result_string)
