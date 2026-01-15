"""
Tests for full pipelines

"""
import codecs
from heipy.parsers import heiparse
from heipy.heipipe.pipeline_library.sourcedoc import SourceDocPipe
from tests.helpers.xml_compare import assert_xml_equal, pipeline_compare_flow



class TestSourcedocPipeline:
    """Test SourceDoc Pipeline."""

    def test_sourcedoc_complex(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SourceDocPipe(), 
                              complex_fixtures_dir / "Gregoire_A3_Paris.xml",
                              complex_fixtures_dir / "output/sourcedoc/Gregoire_A3_Paris.xml",
                              generate_auto=True
                              )
        
    def test_sourcedoc_milestones(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SourceDocPipe(), 
                              complex_fixtures_dir / "zone_milestones.xml", 
                              complex_fixtures_dir / "output/sourcedoc/zone_milestones.xml", 
                              generate_auto=False
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
                              step_fixtures_dir / "semantic.revision_spans/input_basic.xml", 
                              complex_fixtures_dir / "output/sourcedoc/revision_spans_basic.xml", 
                              generate_auto=True
                              )
    
        pipeline_compare_flow(SourceDocPipe(), 
                              step_fixtures_dir / "semantic.revision_spans/input_complex.xml", 
                              complex_fixtures_dir / "output/sourcedoc/revision_spans_complex.xml", 
                              generate_auto=True
                              )

