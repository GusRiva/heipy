from ..steps import XsltStep

def get_step():
    return XsltStep(files=[
    "text_filterVisualInformation.xsl",
    ], name="filter_visual_information")