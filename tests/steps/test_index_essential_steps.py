"""Tests for index_essential_steps."""

import pytest

from heipy.heipipe.steps import XsltStep
from heipy.heipipe.step_library import index_essential_steps
from tests.helpers.xml_compare import assert_xml_equal, vanilla_compare_flow


def test_step_definition():
    """The stylesheets depend on each other, so their order matters:
    duplicates from doublePosting are already marked as preferred and must
    not be touched again by preferredAppellation."""
    step = index_essential_steps.get_step()
    assert step.get_files() == [
        "index/doublePosting.xsl",
        "index/verbalizeDates.xsl",
        "index/preferredAppellation.xsl",
    ]


def test_basic(fixture_loader):
    vanilla_compare_flow(index_essential_steps, fixture_loader)


@pytest.mark.parametrize("variant, xsl", [
    ("double_posting", "index/doublePosting.xsl"),
    ("verbalize_dates", "index/verbalizeDates.xsl"),
    ("preferred_appellation", "index/preferredAppellation.xsl"),
])
def test_single_stylesheet(fixture_loader, variant, xsl):
    step = XsltStep(files=[xsl], name=variant, pipe_files=True)
    input_tree, expected_tree = fixture_loader.load_step_pair(
        "index_essential_steps", variant
    )

    input_string = fixture_loader.tree_to_string(input_tree)
    result_string = step.execute(input_string)

    assert_xml_equal(expected_tree, result_string)
