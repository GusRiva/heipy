import re
import sys
import unicodedata

from ..steps import BaseStep


def _mark_ranges():
    """Character class covering all Unicode marks (categories Mn, Mc, Me)."""
    ranges = []
    start = None
    for cp in range(sys.maxunicode + 2):
        is_mark = cp <= sys.maxunicode and unicodedata.category(chr(cp)).startswith("M")
        if is_mark and start is None:
            start = cp
        elif not is_mark and start is not None:
            ranges.append(f"\\U{start:08X}-\\U{cp - 1:08X}")
            start = None
    return "[" + "".join(ranges) + "]"


# comments, processing instructions, CDATA sections and the DOCTYPE don't resolve
# character references, so they are matched first and kept as they are
pattern = re.compile(
    r"(<!--.*?-->|<\?.*?\?>|<!\[CDATA\[.*?\]\]>|<!DOCTYPE(?:[^\[>]|\[.*?\])*>)|(" + _mark_ranges() + ")",
    re.DOTALL,
)


def _replace(match):
    if match.group(1) is not None:
        return match.group(1)
    return f"&#x{ord(match.group(2)):04X};"


def combining_to_entities(xml):
    """Write all combining characters in text and attribute values as numeric character references."""
    return pattern.sub(_replace, xml)


class CombiningToEntitiesStep(BaseStep):
    """Writes combining characters as numeric character references, e.g. &#x0308;.

    Works on the string, because parsing turns the references back into characters,
    so it must be the last step of a pipeline.
    """

    def __init__(self, name="combining_to_entities", desc="Write combining characters as numeric character references", serial=False, parameters=None):
        super().__init__(name, desc, serial, parameters)

    def __str__(self):
        return f"Combining to entities step »{self.name}«"

    def execute(self, input, serial=False):
        result = combining_to_entities(input)
        if self.serial or serial:
            super()._serialize(result)
        return result


def get_step():
    return CombiningToEntitiesStep()
