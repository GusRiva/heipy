"""Tests for reg_levels."""

from heipy.heipipe.step_library import reg_levels

from tests.helpers.xml_compare import vanilla_compare_flow


def test_basic(fixture_loader):
    vanilla_compare_flow(reg_levels, fixture_loader, generate_auto=True)
