"""
Tests for full pipelines

"""
import re

import pytest
from saxonche import PySaxonApiError

from heipy.heipipe.pipeline_library.public import PublicPipe
from tests.helpers.xml_compare import pipeline_compare_flow


class TestPublicPipeline:
    """Test Public Pipeline."""

    sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title ana="hc:MainTitle">Sample</title>
            </titleStmt>
            <publicationStmt>
                <publisher >
                    <orgName>Universitätsbibliothek Heidelberg</orgName>
                    <idno ana="hc:GNDURI">https://d-nb.info/gnd/2002498-8</idno>
                    <listRef>
                        <ptr ana="hc:URLReference" target="https://www.ub.uni-heidelberg.de/"/>
                    </listRef>
                </publisher>
                <pubPlace>
                    <placeName>Heidelberg</placeName>
                    <idno ana="hc:GNDURI">https://d-nb.info/gnd/4023996-2</idno>
                </pubPlace>
                <date when="2026">2026</date>
                <availability>
                    <licence target="https://creativecommons.org/licenses/by-sa/4.0">
                        <p>Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)</p>
                    </licence>
                </availability>
            </publicationStmt>
        </fileDesc>
    </teiHeader><body/></TEI>'''


    def test_public_basic(self, complex_fixtures_dir):
        pipe = PublicPipe()
        pipe.set_pipestep_parameter('replace_schema_url', 'schema_url', 'https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/releases/2026-07-21/tei_hes_index.rng')
        pipe.set_pipestep_parameter('update_changeList', 'changeDate', '2026-09-01') 
        pipeline_compare_flow(pipe, 
                            complex_fixtures_dir / "tokenized.xml", 
                            complex_fixtures_dir / "output/public/tokenized.xml", 
                            generate_auto=False
                            )
        
        
    def test_public_error_id(self):
        pipe = PublicPipe()
        with pytest.raises(PySaxonApiError, match="check_for_ub_publisher.xsl"):
            pipe.execute(self.sample_xml, input_format='xml_string')
            
            
    def test_public_error_licence(self):
        pipe = PublicPipe()
        xml_test = re.sub(r'<licence.*?</licence>', '', self.sample_xml, flags=re.DOTALL)
        with pytest.raises(PySaxonApiError, match="check_for_ub_publisher.xsl"):
            pipe.execute(xml_test, input_format='xml_string')