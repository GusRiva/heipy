from ..steps import XsltStep

def get_step():
    return XsltStep(
    files=["text_markNoteAsEditorial.xsl",],
    name="mark_note_as_editorial")