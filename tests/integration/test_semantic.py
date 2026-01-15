"""
Tests for full pipelines

"""
from heipy.heipipe.pipeline_library.semantic import SemanticPipe
from tests.helpers.xml_compare import pipeline_compare_flow



class TestSemanticPipeline:
    """Test Semantic Pipeline."""

    def test_semantic_basic(self, complex_fixtures_dir):
        """Test that basic TEI can be processed without error."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "Gregoire_A3_Paris_simple.xml", 
                              complex_fixtures_dir / "output/semantic/Gregoire_A3_Paris_simple.xml", 
                              generate_auto=True
                              )

    def test_semantic_complex(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "Gregoire_A3_Paris.xml",
                              complex_fixtures_dir / "output/semantic/Gregoire_A3_Paris.xml",
                              generate_auto=True
                              )
        
    def test_semantic_milestones(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "zone_milestones.xml", 
                              complex_fixtures_dir / "output/semantic/zone_milestones.xml", 
                              generate_auto=True
                              )
    
    def test_semantic_non_tokenized(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "non_tokenized.xml", 
                              complex_fixtures_dir / "output/semantic/non_tokenized.xml", 
                              generate_auto=True
                              )
        
    def test_semantic_facs(self, complex_fixtures_dir):
        """Test that facs are processed correctly."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "facs.xml", 
                              complex_fixtures_dir / "output/semantic/facs.xml",                              
                              generate_auto=True
                              )
