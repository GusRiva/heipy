from ..steps import XsltStep

def get_step():
    return XsltStep(files=[
        "text_trimWhitespaceAdjacentToPhysicalBeginnings.xsl",
        "text_normalizeWhitespaceInMixedContent.xsl",
        "text_stripWhitespaceInElementsStatedBySchema.xsl",
        "text_normalizeWhitespaceInTokenizedContent.xsl"
      ],
    desc="Handles mixed content whitespaces, so that every element is in the right place",
    name="Whitespaces"
)
