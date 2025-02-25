from ..steps import XsltStep

def get_step():
    return XsltStep(files=[
    "page_number_leading_zeroes.xsl",
    ],name="page_number_leading_zeroes", pipe_files=True)
