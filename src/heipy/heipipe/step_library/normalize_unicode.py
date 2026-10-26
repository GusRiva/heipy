import unicodedata

from lxml import etree as et

from ..steps import PythonStep


def _nfc(value):
    if not value or unicodedata.is_normalized("NFC", value):
        return value
    return unicodedata.normalize("NFC", value)


def _normalize_text(node):
    normalized = _nfc(node.text)
    if normalized is not node.text:
        node.text = normalized


def _normalize_tail(node):
    normalized = _nfc(node.tail)
    if normalized is not node.tail:
        node.tail = normalized


def normalize_unicode_func(tree, parameters=None):
    root = tree.getroot()
    # comments and processing instructions outside the root element have no tail
    for node in [*root.itersiblings(preceding=True), *root.itersiblings()]:
        _normalize_text(node)
    for node in root.iter():
        # unresolved entity references: their text is read-only, but their tail is not
        if not isinstance(node, et._Entity):
            _normalize_text(node)
        if node is not root:
            _normalize_tail(node)
        if isinstance(node.tag, str):
            for name, value in node.attrib.items():
                normalized = _nfc(value)
                if normalized is not value:
                    node.attrib[name] = normalized
    return tree


def get_step():
    return PythonStep(normalize_unicode_func, name="normalize_unicode")
