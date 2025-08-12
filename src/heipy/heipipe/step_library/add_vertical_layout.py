from ..steps import XsltStep


def get_step():
    return XsltStep(files=['facsimile_addVerticalLayout.xsl'],
                            name="add_vertical_layout", pipe_files=True)
