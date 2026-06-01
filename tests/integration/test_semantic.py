"""
Tests for full pipelines

"""
from heipy.heipipe.pipeline_library.semantic import SemanticPipe
from tests.helpers.xml_compare import pipeline_compare_flow



class TestSemanticPipeline:
    """Test Semantic Pipeline."""

    def test_semantic_breaks(self):
        """Test breaks with no"""
        pipe = SemanticPipe()
        input_xml = """<TEI xmlns="http://www.tei-c.org/ns/1.0">
            <text>
                <l>Text <lb/>with a no
                <lb break='no'/>te continues.</l>
                <w xml:id="w_911_7" norm="bewarn">pewa<lb n="19.1" ana="hc:InterlinearLine hc:RunOverAbove" rendition="hc:FlushRight" break="no"/>re<choice><am>bar</am><ex>n</ex></choice></w>
            </text>
        </TEI>"""
        result = pipe.execute(input_xml, input_format='xml_string')
        assert result == """<?xml version="1.0" encoding="UTF-8"?><TEI xmlns="http://www.tei-c.org/ns/1.0"><text xml:space="preserve"><l>Text<lb/>with a no<lb break="no"/>te continues.</l><w xml:id="w_911_7" norm="bewarn">pewa<lb n="19.1" ana="hc:InterlinearLine hc:RunOverAbove" break="no"/>re<choice><am>bar</am><ex>n</ex></choice></w></text></TEI>"""
        

    def test_semantic_basic(self, complex_fixtures_dir):
        """Test that basic TEI can be processed without error."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "Gregoire_A3_Paris_simple.xml", 
                              complex_fixtures_dir / "output/semantic/Gregoire_A3_Paris_simple.xml", 
                              generate_auto=False
                              )

    def test_semantic_complex(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "Gregoire_A3_Paris.xml",
                              complex_fixtures_dir / "output/semantic/Gregoire_A3_Paris.xml",
                              generate_auto=False
                              )
        
    def test_semantic_milestones(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "zone_milestones.xml", 
                              complex_fixtures_dir / "output/semantic/zone_milestones.xml", 
                              generate_auto=False
                              )
    
    def test_semantic_non_tokenized(self, complex_fixtures_dir):
        """Test that complex TEI can be processed without error."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "non_tokenized.xml", 
                              complex_fixtures_dir / "output/semantic/non_tokenized.xml", 
                              generate_auto=False
                              )
        
    def test_semantic_facs(self, complex_fixtures_dir):
        """Test that facs are processed correctly."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "facs.xml", 
                              complex_fixtures_dir / "output/semantic/facs.xml",                              
                              generate_auto=False
                              )
    
    def test_semantic_line_segment(self, complex_fixtures_dir):
        """Test transformation line segment."""
        pipeline_compare_flow(SemanticPipe(), 
                              complex_fixtures_dir / "line_segment.xml", 
                              complex_fixtures_dir / "output/semantic/line_segment.xml", 
                              generate_auto=True
                              )
