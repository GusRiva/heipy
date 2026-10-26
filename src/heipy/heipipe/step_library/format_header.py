import re

import xmlformatter

from ..steps import BaseStep

formatter = xmlformatter.Formatter(selfclose=True, correct=True, preserve_attributes=True, preserve=["c"])
header_pattern = re.compile(r"([ \t]*)(<teiHeader\b.*?</teiHeader>)", re.DOTALL)


def format_header(xml):
    """Format only the teiHeader element and leave the rest of the document untouched."""
    match = header_pattern.search(xml)
    if match is None:
        return xml
    indent, header = match.groups()
    formatted = formatter.format_string(header).decode("utf-8").strip()
    formatted = formatted.replace("\n", "\n" + indent)
    return xml[:match.start()] + indent + formatted + xml[match.end():]


def format_prolog(xml):
    """Put the XML declaration, each prolog item and the TEI start tag on their own lines."""
    tei_start = xml.find("<TEI")
    if tei_start == -1:
        return xml
    prolog = xml[:tei_start].strip()
    if not prolog.startswith("<?xml "):
        prolog = '<?xml version="1.0" encoding="UTF-8"?>' + prolog
    prolog = re.sub(r">\s*<", ">\n<", prolog)
    return prolog + "\n" + xml[tei_start:]


class FormatHeaderStep(BaseStep):
    """Formats the prolog and the teiHeader of the serialized document.

    Works on the string, so it must come after all steps that parse the document again.
    """

    def __init__(self, name="format_header", desc="Format the prolog and the teiHeader", serial=False, parameters=None):
        super().__init__(name, desc, serial, parameters)

    def __str__(self):
        return f"Format header step »{self.name}«"

    def execute(self, input, serial=False):
        result = format_prolog(format_header(input))
        if self.serial or serial:
            super()._serialize(result)
        return result


def get_step():
    return FormatHeaderStep()
