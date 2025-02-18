from ..steps import DeleteStep

def get_step():
    return DeleteStep(elements=[
    "tei:metamark",
    "tei:fw",
    "tei:label[contains(@ana,'hc:DivisionMark')]"
      ], name="remove_non_semantic_elements")
