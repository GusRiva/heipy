from ..steps import XsltStep

def get_step():
    return XsltStep(files=[
    "text_wrapResolvedContent.xsl"], 
    name= 'wrap_resolved_content', pipe_files=True)
