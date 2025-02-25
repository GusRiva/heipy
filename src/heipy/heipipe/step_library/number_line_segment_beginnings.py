from ..steps import XsltStep

def get_step():
    return XsltStep(
    files=["text_numberLineSegmentBeginnings.xsl",],
    name="number_line_segment_beginnings",
    pipe_files= True
)
