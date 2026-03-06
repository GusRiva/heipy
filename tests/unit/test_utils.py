"""
Tests for restore_entities function.
"""

import pytest

from heipy.editions_utils import restore_entities


@pytest.mark.unit
class TestRestoreEntities:
    """Test restore_entities function."""

    def test_basic_restore_entities(self, minimal_fixtures_dir, tmp_path):
        """Test that entities are restored correctly from input file."""
        input_file = minimal_fixtures_dir / "tei_with_entities_resolved.xml"
        expected_file = minimal_fixtures_dir / "tei_with_entities.xml"
        output_file = tmp_path / "output.xml"

        restore_entities(str(input_file), str(output_file))

        assert output_file.exists()
        assert output_file.read_text(encoding="utf-8") == expected_file.read_text(
            encoding="utf-8"
        )
