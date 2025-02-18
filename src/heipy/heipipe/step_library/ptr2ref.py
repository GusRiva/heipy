from ..steps import XsltStep

def get_step():
    return XsltStep(files=[
    "ptr2Ref.xsl",
    ], name="ptr2ref")