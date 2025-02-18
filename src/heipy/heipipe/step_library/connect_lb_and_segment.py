from ..steps import XsltStep

def get_step():
    return XsltStep(files=[
    "text_connectLbWithZone.xsl",
    "text_moveIncludedInZone.xsl",
    "text_connectSegmentWithLine.xsl"
    ], name="connect_lb_and_segment")