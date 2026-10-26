"""Tests for format_header step."""

from heipy.heipipe.pipeline_library.public import PublicPipe
from heipy.heipipe.step_library import format_header

BODY = '<text>\n    <body><p>Ein   <hi>unformatierter</hi>\n text</p></body>\n  </text>'

TEI_XML = (
    '<?xml-model href="schema.rng" type="application/xml"?><?xml-model href="schema.sch" type="application/xml"?>'
    '<TEI xmlns="http://www.tei-c.org/ns/1.0">\n'
    '  <teiHeader><fileDesc><titleStmt><title>Test</title></titleStmt></fileDesc></teiHeader>\n'
    f'  {BODY}\n'
    '</TEI>'
)


def run_step():
    return format_header.get_step().execute(TEI_XML)


def test_prolog_on_separate_lines():
    lines = run_step().splitlines()
    assert lines[0] == '<?xml version="1.0" encoding="UTF-8"?>'
    assert lines[1] == '<?xml-model href="schema.rng" type="application/xml"?>'
    assert lines[2] == '<?xml-model href="schema.sch" type="application/xml"?>'
    assert lines[3] == '<TEI xmlns="http://www.tei-c.org/ns/1.0">'


def test_existing_declaration_is_kept():
    xml = '<?xml version="1.0" encoding="UTF-8"?><TEI><teiHeader/></TEI>'
    result = format_header.get_step().execute(xml)
    assert result.count("<?xml version") == 1
    assert result.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<TEI>')


def test_header_is_indented():
    lines = run_step().splitlines()
    assert "  <teiHeader>" in lines
    assert "    <fileDesc>" in lines
    assert "        <title>Test</title>" in lines
    assert "  </teiHeader>" in lines


def test_body_is_untouched():
    assert BODY in run_step()


def test_string_steps_are_last_in_public_pipe():
    names = [step.get_name() for step in PublicPipe().get_steps()]
    assert names[-2:] == ["format_header", "combining_to_entities"]
