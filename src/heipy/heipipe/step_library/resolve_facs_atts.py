from ..steps import XsltStep


def get_step():
    return XsltStep(
        files=["text_resolveFacsAtts.xsl", 
               "text_resolveFacsAtts_1.xsl"],
        name="resolve_facs_atts",
        pipe_files=True
    )
