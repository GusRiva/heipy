from ...steps import DeleteStep

def get_step():
    return DeleteStep(elements=[
    "tei:gap[@unit='page' or @unit='leaf']",
], name="remove_gap_page")
