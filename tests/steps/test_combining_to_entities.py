"""Tests for combining_to_entities step.

The comparison is done on strings: in a parsed tree a character reference
and the raw character are identical.
"""

from lxml import etree as et

from heipy.heipipe.step_library import combining_to_entities

TEI_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<?test-pi guͤt?>\n'
    '<TEI xmlns="http://www.tei-c.org/ns/1.0">\n'
    '  <text>\n'
    '    <body>\n'
    '      <p n="guͤt">guͤt müde ā̈</p>\n'
    '      <!-- guͤt -->\n'
    '    </body>\n'
    '  </text>\n'
    '</TEI>'
)


def run_step():
    return combining_to_entities.get_step().execute(TEI_XML)


def test_text_and_attributes():
    result = run_step()
    assert '<p n="gu&#x0364;t">gu&#x0364;t' in result
    assert "a&#x0304;&#x0308;</p>" in result


def test_precomposed_characters_stay():
    assert "müde" in run_step()


def test_comments_and_processing_instructions_stay():
    result = run_step()
    assert "<?test-pi guͤt?>" in result
    assert "<!-- guͤt -->" in result


def test_content_is_unchanged():
    expected = et.tostring(et.fromstring(TEI_XML.encode("utf-8")))
    actual = et.tostring(et.fromstring(run_step().encode("utf-8")))
    assert actual == expected
