from lxml import etree as et

def remove_comments(root, parameters=None):
    """Remove all comment nodes using lxml's built-in strip_tags."""
    et.strip_tags(root, et.Comment)
    return root

def get_step():
    return PythonStep(
    funct=remove_comments,
    name="remove_comments"
)

