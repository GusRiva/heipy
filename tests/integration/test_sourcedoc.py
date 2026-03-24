"""
Tests for full pipelines

"""
from heipy.heipipe.pipeline_library.sourcedoc import SourceDocPipe
from tests.helpers.xml_compare import pipeline_compare_flow



class TestSourcedocPipeline:
    """Test SourceDoc Pipeline."""

    def test_sourcedoc_complex(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SourceDocPipe(), 
                              complex_fixtures_dir / "Gregoire_A3_Paris_simple.xml",
                              complex_fixtures_dir / "output/sourcedoc/Gregoire_A3_Paris_simple.xml",
                              generate_auto=True
                              )
        
    def test_sourcedoc_milestones(self, complex_fixtures_dir):
        """Test zone milestones."""
        pipeline_compare_flow(SourceDocPipe(),
                              complex_fixtures_dir / "zone_milestones.xml", 
                              complex_fixtures_dir / "output/sourcedoc/zone_milestones.xml", 
                              generate_auto=True, 
                              )
        
    def test_sourcedoc_tables(self, complex_fixtures_dir):
        """Test tables."""
        pipeline_compare_flow(SourceDocPipe(serial=True),
                              complex_fixtures_dir / "tabelle.xml", 
                              complex_fixtures_dir / "output/sourcedoc/tabelle.xml", 
                              generate_auto=True, 
                              )
    
    def test_sourcedoc_non_tokenized(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SourceDocPipe(), 
                              complex_fixtures_dir / "non_tokenized.xml", 
                              complex_fixtures_dir / "output/sourcedoc/non_tokenized.xml", 
                              generate_auto=False
                              )
        
    def test_sourcedoc_facs(self, complex_fixtures_dir):
        """Test that facs are processed correctly."""
        pipeline_compare_flow(SourceDocPipe(), 
                              complex_fixtures_dir / "facs.xml", 
                              complex_fixtures_dir / "output/sourcedoc/facs.xml", 
                              generate_auto=False
                              )

    def test_sourcedoc_revision_spans(self, step_fixtures_dir, complex_fixtures_dir):
        """Test that revision spans are processed correctly."""
        pipeline_compare_flow(SourceDocPipe(), 
                              step_fixtures_dir / "revision_spans/input_basic.xml", 
                              complex_fixtures_dir / "output/sourcedoc/revision_spans_basic.xml", 
                              generate_auto=False
                              )
    
        pipeline_compare_flow(SourceDocPipe(), 
                              step_fixtures_dir / "revision_spans/input_complex.xml", 
                              complex_fixtures_dir / "output/sourcedoc/revision_spans_complex.xml", 
                              generate_auto=False
                              )
        
    def test_sourcedoc_subst(self, complex_fixtures_dir, step_fixtures_dir):
        "Test subst"
        pipeline_compare_flow(SourceDocPipe(), 
                              step_fixtures_dir / "move_physical_beginnings/input_complex.xml", 
                              complex_fixtures_dir / "output/sourcedoc/subst-with-del.xml", 
                              generate_auto=False
                              )

