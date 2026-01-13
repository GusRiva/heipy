"""Tests for semantic.revision_spans step."""

from heipy.heipipe.step_library.semantic import revision_spans
from tests.helpers.xml_compare import vanilla_compare_flow


def test_basic(fixture_loader):
    vanilla_compare_flow(revision_spans, fixture_loader)
    
def test_complex(fixture_loader):
    vanilla_compare_flow(revision_spans, fixture_loader, variant='complex')

def test_milestones(fixture_loader):
    vanilla_compare_flow(revision_spans, fixture_loader, variant='milestones')
    
def test_text_tail(fixture_loader):
    vanilla_compare_flow(revision_spans, fixture_loader, variant='text_tail')
