from ..steps import XsltStep

def get_step():
    return XsltStep(files=[
    "reg_levels.xsl",
    ], name="reg_levels", pipe_files=True)