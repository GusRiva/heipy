"""Tests for revision_spans step."""

from heipy.heipipe.step_library import revision_spans
from tests.helpers.xml_compare import vanilla_compare_flow


def test_basic(fixture_loader):
    vanilla_compare_flow(revision_spans, fixture_loader, generate_auto= True)
    
def test_complex(fixture_loader):
    vanilla_compare_flow(revision_spans, fixture_loader, variant='complex', generate_auto= True)

def test_milestones(fixture_loader):
    vanilla_compare_flow(revision_spans, fixture_loader, variant='milestones', generate_auto= True)
    
def test_text_tail(fixture_loader):
    vanilla_compare_flow(revision_spans, fixture_loader, variant='text_tail', generate_auto= True)

def test_tokenized(fixture_loader):
    vanilla_compare_flow(revision_spans, fixture_loader, variant='tokenized', generate_auto= True)
