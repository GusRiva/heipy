from ..steps import XsltStep


def get_step():
    return XsltStep(
        files=["text_resolveFacsAtts_1.xsl", 
               "text_resolveFacsAtts.xsl"],
        name="resolve_facs_atts",
        pipe_files=True
    )
