"""Tests for sourcedoc.combine_facsimile_and_text_to_sourcedoc."""

import pytest
from lxml import etree as et

from heipy.heipipe.step_library.sourcedoc.combine_facsimile_and_text_to_sourcedoc import combine_facsimile_text
from heipy.heiwarning import HeiWarning

NS = {"tei": "http://www.tei-c.org/ns/1.0"}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def make_tree(lb_facs: str):
    xml = f"""<TEI xmlns="http://www.tei-c.org/ns/1.0"
        xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS">
      <teiHeader/>
      <facsimile>
        <surface ana="hc:Page" xml:id="s1">
          <zone ana="hc:TextZone" xml:id="z1">
            <zone ana="hc:LineZone" xml:id="lz1"/>
          </zone>
        </surface>
      </facsimile>
      <lb n="1" facs="{lb_facs}" hei:belongsToZone="#z1"/>Line one
    </TEI>"""
    return et.ElementTree(et.fromstring(xml))


def test_line_goes_into_line_zone():
    root = combine_facsimile_text(make_tree("#lz1")).getroot()
    line_zone = root.find(".//tei:sourceDoc//tei:zone[@ana='hc:LineZone']", NS)
    line = line_zone.find("tei:line", NS)
    assert line is not None
    assert line.text.strip() == "Line one"
    # the xml:id moves from the line zone to the line
    assert line.get(XML_ID) == "lz1"
    assert line_zone.get(XML_ID) is None


def test_missing_line_zone_falls_back_to_zone():
    """An lb/@facs pointing to a missing LineZone must not crash; the line goes into its zone."""
    with pytest.warns(HeiWarning, match="Could not find linezone"):
        root = combine_facsimile_text(make_tree("#does_not_exist")).getroot()
    text_zone = root.xpath(".//tei:sourceDoc//tei:zone[@xml:id='z1']", namespaces=NS)[0]
    lines = text_zone.findall(".//tei:line", NS)
    assert len(lines) == 1
    assert lines[0].text.strip() == "Line one"


def test_lines_without_facs_are_sorted_by_n():
    """Lines without their own LineZone are ordered by @n; lines without a numeric @n go last."""
    xml = """<TEI xmlns="http://www.tei-c.org/ns/1.0"
        xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS">
      <teiHeader/>
      <facsimile><surface ana="hc:Page" xml:id="s1"><zone ana="hc:TextZone" xml:id="z1"/></surface></facsimile>
      <lb hei:belongsToZone="#z1"/>no n
      <lb n="2" hei:belongsToZone="#z1"/>two
      <lb n="1" hei:belongsToZone="#z1"/>one
    </TEI>"""
    root = combine_facsimile_text(et.ElementTree(et.fromstring(xml))).getroot()
    texts = [line.text.strip() for line in root.iterfind(".//tei:sourceDoc//tei:line", NS)]
    assert texts == ["one", "two", "no n"]


def test_segment_beginning_without_zone_is_skipped():
    xml = """<TEI xmlns="http://www.tei-c.org/ns/1.0"
        xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS">
      <teiHeader/>
      <facsimile><surface ana="hc:Page" xml:id="s1"><zone ana="hc:TextZone" xml:id="z1"/></surface></facsimile>
      <lb n="1" hei:belongsToZone="#z1"/>one
      <milestone ana="hc:LineSegmentBeginning" n="1" hei:belongsToLine="1"/>
    </TEI>"""
    with pytest.warns(HeiWarning, match="without hei:belongsToZone"):
        combine_facsimile_text(et.ElementTree(et.fromstring(xml)))
