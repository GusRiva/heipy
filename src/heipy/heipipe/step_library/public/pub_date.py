from ...steps import PythonStep
from lxml import etree as et
from ....namespaces import ns

def pub_date_funct(tree, parameters=None):
    root = tree.getroot()
    publ_stmt = root.xpath("//tei:publStmt", ns)
    return tree


def get_step():
    return PythonStep(pub_date_funct, name="pub_date")
