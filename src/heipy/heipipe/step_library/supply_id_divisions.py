from ..steps import XsltStep


def get_step():
    return XsltStep(
        files=['text_supplyIDOnDivisions.xsl'],
        name="supply_id_divisions", pipe_files=True)
    

