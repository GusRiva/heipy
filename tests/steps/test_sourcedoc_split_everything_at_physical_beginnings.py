"""Tests for split_everything_at_physical_beginnings step."""


from heipy.heipipe.step_library import split_everything_at_physical_beginnings
from tests.helpers.xml_compare import vanilla_compare_flow


# def test_basic(fixture_loader):
#     vanilla_compare_flow(split_everything_at_physical_beginnings, fixture_loader)

def test_del_in_subst(fixture_loader):
    vanilla_compare_flow(split_everything_at_physical_beginnings, fixture_loader, variant="subst-with-del")

