"""Tests for replace_schema_url step."""

from heipy.heipipe.step_library.public import check_prefixes
from tests.helpers.xml_compare import vanilla_compare_flow


def test_basic(fixture_loader):
    vanilla_compare_flow(check_prefixes, fixture_loader)

def test_prefix_exists(fixture_loader):
    vanilla_compare_flow(check_prefixes, fixture_loader, variant="prefix_exists")