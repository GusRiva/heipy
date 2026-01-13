"""
Tests for full pipelines

"""

from heipy.heipipe.pipeline_library.sourcedoc import SourceDocPipe


class TestDefaultPipelines:
    """Test default Pipelines"""

    def test_sourcedoc_basic(self, minimal_fixtures_dir):
        """Test that basic TEI can be processed without error."""
        sourcedoc_pipe = SourceDocPipe()
        result = sourcedoc_pipe.execute(minimal_fixtures_dir / "basic_tei.xml")
        assert result is not None
        assert "<TEI" in result
