"""
Tests for full pipelines

"""
import codecs
from heipy.parsers import heiparse
from heipy.heipipe.pipeline_library.sourcedoc import SourceDocPipe
from tests.helpers.xml_compare import assert_xml_equal, pipeline_compare_flow



class TestSourcedocPipeline:
    """Test SourceDoc Pipeline."""

    def test_sourcedoc_basic(self, complex_fixtures_dir):
        """Test that basic TEI can be processed without error."""
        pipeline_compare_flow(SourceDocPipe(), 
                              complex_fixtures_dir / "Gregoire_A3_Paris_simple.xml", 
                              generate_auto=False
                              )

    def test_sourcedoc_complex(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SourceDocPipe(), 
                              complex_fixtures_dir / "Gregoire_A3_Paris.xml", 
                              generate_auto=True
                              )
        
    def test_sourcedoc_milestones(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SourceDocPipe(), 
                              complex_fixtures_dir / "zone_milestones.xml", 
                              generate_auto=False
                              )
    
    def test_sourcedoc_non_tokenized(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SourceDocPipe(), 
                              complex_fixtures_dir / "non_tokenized.xml", 
                              generate_auto=False
                              )
        
    def test_sourcedoc_facs(self, complex_fixtures_dir):
        """Test that facs are processed correctly."""
        pipeline_compare_flow(SourceDocPipe(), 
                              complex_fixtures_dir / "facs.xml", 
                              generate_auto=False
                              )
