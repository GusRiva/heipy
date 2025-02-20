from ..steps import XsltStep


def get_step():
    return XsltStep(files=['text_addIDToNote.xsl'],
                            name="add_id_2_note")

