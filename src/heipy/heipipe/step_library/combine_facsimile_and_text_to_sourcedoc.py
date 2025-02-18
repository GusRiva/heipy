from ..steps import XsltStep

def get_step():
    return XsltStep(files=[
        "text_markWrapper.xsl",
        "text_transformToSourceDoc_new.xsl"
        ], name = "combine_facsimile_and_text_to_sourcedoc")