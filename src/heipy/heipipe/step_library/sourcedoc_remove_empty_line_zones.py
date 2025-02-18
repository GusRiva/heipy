from ..steps import DeleteStep

def get_step():
    return DeleteStep(
    elements=["tei:zone[@ana='hc:LineZone'][not(*)][normalize-space(text()) = '']"],
    name="sourcedoc_remove_empty_line_zones"
)
