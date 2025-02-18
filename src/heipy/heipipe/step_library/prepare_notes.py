from ..steps import Pipeline, XsltStep
from .move_note_after_its_target import get_step as gs

def get_step():
    return Pipeline(steps=[
    XsltStep(files=['text_addIDToNote.xsl'],
             name="text_prepare_notes"),
    gs()
    ], name="prepare_notes")

