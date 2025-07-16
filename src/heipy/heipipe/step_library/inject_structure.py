from ..steps import XsltStep


def get_step():
    return XsltStep(
        files=['text_injectStructure1.xsl', 'text_injectStructure2.xsl'],
        name="inject_structure", pipe_files=True, serial=True)
