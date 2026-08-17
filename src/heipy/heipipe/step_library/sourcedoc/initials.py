from ...steps import XsltStep

def get_step():
    return XsltStep(files=[
    "text_initials.xsl",
    ], name="initials", pipe_files=True)
