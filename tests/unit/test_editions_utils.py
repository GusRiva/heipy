"""
Tests for heipy.editions_utils.create_langusage.
"""

import pytest
from lxml import etree as et

from heipy.editions_utils import create_langusage

NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def make_tree(text_langs: str, lang_usage: str = "") -> et._ElementTree:
    xml = f"""<TEI xmlns="http://www.tei-c.org/ns/1.0">
      <teiHeader><fileDesc/><profileDesc>{lang_usage}</profileDesc></teiHeader>
      <text {text_langs}><body><p xml:lang="la">Text</p></body></text>
    </TEI>"""
    return et.ElementTree(et.fromstring(xml))


def idents(tree) -> list:
    return [el.get("ident") for el in tree.findall(".//tei:langUsage/tei:language", NS)]


@pytest.mark.unit
class TestCreateLangUsage:

    def test_returns_tree(self):
        result = create_langusage(make_tree('xml:lang="osx"'))
        assert isinstance(result, et._ElementTree)

    def test_languages_are_collected_and_sorted(self):
        result = create_langusage(make_tree('xml:lang="osx"'))
        assert idents(result) == ["la", "osx"]

    def test_existing_langusage_is_replaced(self):
        tree = make_tree('xml:lang="osx"', '<langUsage><language ident="fr"/></langUsage>')
        assert idents(create_langusage(tree)) == ["la", "osx"]

    @pytest.mark.parametrize("lang", ["xx", "osx-12345678910"])
    def test_invalid_tag_leaves_tree_unchanged(self, lang):
        """Invalid ("xx") and malformed tags leave an existing langUsage untouched."""
        tree = make_tree(f'xml:lang="{lang}"', '<langUsage><language ident="fr"/></langUsage>')
        with pytest.warns(UserWarning, match="invalid language tag"):
            result = create_langusage(tree)
        assert idents(result) == ["fr"]

    def test_missing_lang_on_text_raises(self):
        with pytest.raises(Exception, match="at least one xml:lang"):
            create_langusage(make_tree(""))

    def test_missing_text_raises(self):
        tree = et.ElementTree(et.fromstring('<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader/></TEI>'))
        with pytest.raises(ValueError, match="tei:text"):
            create_langusage(tree)

    def test_profiledesc_is_created(self):
        tree = et.ElementTree(et.fromstring(
            '<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc/></teiHeader>'
            '<text xml:lang="la"/></TEI>'))
        result = create_langusage(tree)
        assert result.find("tei:teiHeader/tei:fileDesc", NS).getnext().tag == "{http://www.tei-c.org/ns/1.0}profileDesc"
        assert idents(result) == ["la"]

    def test_missing_filedesc_raises(self):
        tree = et.ElementTree(et.fromstring(
            '<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader/><text xml:lang="la"/></TEI>'))
        with pytest.raises(ValueError, match="tei:fileDesc"):
            create_langusage(tree)
