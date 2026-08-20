import re
import warnings

from ...steps import PythonStep
from lxml import etree as et
from ....heiwarning import HeiWarning

def replace_schema_url_func(tree, parameters=None):
    if parameters is None:
        warnings.warn("No new Schema URL was given for the Public Pipeline.", HeiWarning)
        return tree
    if 'schema_url' in parameters:
        schema_url = parameters['schema_url']
        for pi in tree.xpath("//processing-instruction('xml-model')"):
            pi.text = re.sub(
                r'(href=["\'])[^"\']*(["\'])',
                rf'\1{schema_url}\2',
                pi.text
            )
    return tree

def get_step():
    return PythonStep(replace_schema_url_func, name="replace_schema_url")
