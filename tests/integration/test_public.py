"""
Tests for full pipelines

"""
from heipy.heipipe.pipeline_library.public import PublicPipe
from tests.helpers.xml_compare import pipeline_compare_flow


class TestPublicPipeline:
    """Test Public Pipeline."""
    def test_public_basic(self, complex_fixtures_dir):
        pipe = PublicPipe()
        pipe.set_pipestep_parameter('replace_schema_url', 'schema_url', 'https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/releases/2026-07-21/tei_hes_index.rng')
        pipeline_compare_flow(pipe, 
                            complex_fixtures_dir / "tokenized.xml", 
                            complex_fixtures_dir / "output/public/tokenized.xml", 
                            generate_auto=True
                            )