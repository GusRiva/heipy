"""
Tests for heipy.combine.combine_sourcedoc.
"""

import pytest
from lxml import etree as et

from heipy.combine import combine_sourcedoc

NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def write_doc(path, surfaces: str | None):
    sourcedoc = f"<sourceDoc>{surfaces}</sourceDoc>" if surfaces is not None else ""
    path.write_text(f'<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader/>{sourcedoc}</TEI>', encoding="utf-8")
    return path


@pytest.mark.unit
class TestCombineSourcedoc:

    def test_surfaces_are_combined(self, tmp_path):
        a = write_doc(tmp_path / "a.xml", '<surface xml:id="s1"/>')
        b = write_doc(tmp_path / "b.xml", '<surface xml:id="s2"/>')
        out = tmp_path / "out" / "combined.xml"
        combine_sourcedoc([a, b], out)
        ids = et.parse(str(out)).xpath("//tei:sourceDoc/tei:surface/@xml:id", namespaces=NS)
        assert ids == ["s1", "s2"]

    def test_file_without_sourcedoc_is_skipped(self, tmp_path):
        """A later file without sourceDoc is skipped instead of aborting the whole combination."""
        a = write_doc(tmp_path / "a.xml", '<surface xml:id="s1"/>')
        b = write_doc(tmp_path / "b.xml", None)
        c = write_doc(tmp_path / "c.xml", '<surface xml:id="s3"/>')
        out = tmp_path / "combined.xml"
        with pytest.warns(UserWarning, match="Could not find sourceDoc"):
            combine_sourcedoc([a, b, c], out)
        ids = et.parse(str(out)).xpath("//tei:sourceDoc/tei:surface/@xml:id", namespaces=NS)
        assert ids == ["s1", "s3"]
