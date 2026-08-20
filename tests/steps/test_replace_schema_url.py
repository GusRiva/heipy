"""Tests for replace_schema_url step."""

import io

from lxml import etree as et

from heipy.heipipe.step_library.public.replace_schema_url import replace_schema_url_func
from heipy.parsers import HeiEditionsParser

NEW_SCHEMA_URL = "https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/releases/2026-07-21/tei_hes_index.rng"

TEI_XML = """<?xml-model href="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/tei_hes_index.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>Test Document</title>
            </titleStmt>
            <publicationStmt>
                <p>Test publication statement</p>
            </publicationStmt>
            <sourceDesc>
                <p>Test source description</p>
            </sourceDesc>
        </fileDesc>
    </teiHeader>
    <text>
        <body/>
    </text>
</TEI>
"""


def test_replace_schema_url_updates_href():
    tree = et.parse(io.BytesIO(TEI_XML.encode("utf-8")), parser=HeiEditionsParser())

    result = replace_schema_url_func(tree, parameters={"schema_url": NEW_SCHEMA_URL})

    pis = result.xpath("//processing-instruction('xml-model')")
    assert len(pis) == 1

    pi_text = pis[0].text
    assert f'href="{NEW_SCHEMA_URL}"' in pi_text
    assert 'type="application/xml"' in pi_text
    assert 'schematypens="http://relaxng.org/ns/structure/1.0"' in pi_text


TEI_XML_TWO_SCHEMAS = """<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/tei_hes.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/tei_hes.rng" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title>Test Document</title>
            </titleStmt>
            <publicationStmt>
                <p>Test publication statement</p>
            </publicationStmt>
            <sourceDesc>
                <p>Test source description</p>
            </sourceDesc>
        </fileDesc>
    </teiHeader>
    <text>
        <body/>
    </text>
</TEI>
"""


def test_replace_schema_url_updates_all_hrefs():
    tree = et.parse(io.BytesIO(TEI_XML_TWO_SCHEMAS.encode("utf-8")), parser=HeiEditionsParser())

    result = replace_schema_url_func(tree, parameters={"schema_url": NEW_SCHEMA_URL})

    pis = result.xpath("//processing-instruction('xml-model')")
    assert len(pis) == 2

    for pi_text in (pis[0].text, pis[1].text):
        assert f'href="{NEW_SCHEMA_URL}"' in pi_text

    assert 'schematypens="http://relaxng.org/ns/structure/1.0"' in pis[0].text
    assert 'schematypens="http://purl.oclc.org/dsdl/schematron"' in pis[1].text
