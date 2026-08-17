"""Tests for transpose / Umstellungen."""

from heipy.heipipe.step_library.semantic import transpose
from tests.helpers.xml_compare import vanilla_compare_flow


def test_basic(fixture_loader):
    vanilla_compare_flow(transpose, fixture_loader)
