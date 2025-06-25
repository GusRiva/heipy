from ..steps import XsltStep


def get_step():
    return XsltStep(files=['suppress_first_cb.xsl'],
                            name="suppress_first_cb", pipe_files=True)

