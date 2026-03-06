from ...steps import XsltStep

def get_step():
    return XsltStep(
    files=["text_splitWordAtPhysicalBeginnings.xsl",],
    name="split_word_at_physical_beginnings",
    pipe_files=True
)
