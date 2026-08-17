"""Tests for connect_lb_and_segment step."""


from heipy.heipipe.step_library.sourcedoc import connect_lb_and_segment
from tests.helpers.xml_compare import vanilla_compare_flow


def test_basic(fixture_loader):
    vanilla_compare_flow(connect_lb_and_segment, fixture_loader)


def test_complex(fixture_loader):
    vanilla_compare_flow(connect_lb_and_segment, fixture_loader, variant="complex")

def test_edgecase(fixture_loader):
    vanilla_compare_flow(connect_lb_and_segment, fixture_loader, variant="edgecase")
