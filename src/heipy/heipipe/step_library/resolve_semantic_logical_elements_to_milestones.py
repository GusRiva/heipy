from ..steps import XsltStep

def get_step():
    return XsltStep(
    files=["text_resolveSemanticLogicalElementsToMilestones_new.xsl",],
    name="resolve_semantic_logical_elements_to_milestones",
    pipe_files= True
)
