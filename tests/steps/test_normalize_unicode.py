"""Tests for normalize_unicode step."""

from heipy.heipipe.step_library import normalize_unicode
from tests.helpers.xml_compare import vanilla_compare_flow


def test_basic(fixture_loader):
    vanilla_compare_flow(normalize_unicode, fixture_loader)
