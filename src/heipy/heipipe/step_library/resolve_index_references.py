from ..steps import XsltStep


def get_step():
    return XsltStep(files=['resolve_index_references.xsl'],
                    name="resolve_index_references", pipe_files=True)

