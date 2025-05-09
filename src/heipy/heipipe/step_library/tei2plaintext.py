from ..steps import XsltStep


def get_step():
    return XsltStep(
        files=['tei2plaintext.xsl'],
        name="tei2plaintext", pipe_files=True)
