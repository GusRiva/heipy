import re
import warnings

from ...steps import PythonStep
from lxml import etree as et
from ....heiwarning import HeiWarning

def replace_schema_url_func(tree, parameters=None):
    if parameters is None:
        warnings.warn("No new Schema URL was given for the Public Pipeline. Use the parameter 'schema_url' in the step 'replace_schema_url'.", HeiWarning)
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

def get_step(schema_url: str | None = None):
    """Replaces the href of all xml-model processing instructions.

    Args:
        schema_url: New schema URL (parameter ``schema_url``). Without it the
            processing instructions stay unchanged and a warning is issued.
    """
    step = PythonStep(replace_schema_url_func, name="replace_schema_url")
    if schema_url is not None:
        step.set_parameter("schema_url", schema_url)
    return step
