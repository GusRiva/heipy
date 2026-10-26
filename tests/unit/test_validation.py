"""
Tests for heipy.validation.list_all_characters.
"""

import pytest

from heipy.validation import list_all_characters


@pytest.mark.unit
class TestListAllCharacters:

    def test_returns_sorted_characters_and_private_use(self):
        chars, private_use = list_all_characters("baa", input_type="str")
        assert chars == [("a", "U+0061"), ("b", "U+0062"), ("", "U+E000")]
        assert private_use == {("", "U+E000", "baa")}

    def test_no_private_use_characters(self):
        _, private_use = list_all_characters("abc", input_type="str")
        assert private_use == set()

    def test_read_from_file(self, tmp_path):
        file = tmp_path / "input.txt"
        file.write_text("þa", encoding="utf-8")
        chars, _ = list_all_characters(str(file))
        assert chars == [("a", "U+0061"), ("þ", "U+00FE")]
