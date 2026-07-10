from ..steps import PythonStep
from lxml import etree as et

def delete_comments_funct(tree, parameters=None):
    root = tree.getroot()
    et.strip_tags(root, et.Comment)
    return tree


def get_step():
    return PythonStep(delete_comments_funct, name="delete_comments")
