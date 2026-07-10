"""Tests for delete_comments step."""

from heipy.heipipe.step_library import delete_comments
from tests.helpers.xml_compare import vanilla_compare_flow


def test_basic(fixture_loader):
    vanilla_compare_flow(delete_comments, fixture_loader)
