from ..steps import XsltStep


def get_step():
    step = XsltStep(
        files=["container2milestone.xsl",],
        name="container2milestone", pipe_files=True)
    return step


