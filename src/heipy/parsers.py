import argparse
import codecs
import importlib.resources

import requests
from lxml import etree as et
from saxonche import PySaxonProcessor, PyXdmValue, PyXdmItem, PyXdmAtomicValue, PyXdmNode, PyXdmMap, PyXdmArray
import warnings
import sys

from .colors import *


def create_xdm_dict(proc, mmap):
    """
    create_xdm_dict(proc, mmap)
    Delete when saxon fixes bug
    """
    xdmMap = {}
    xdmValue_ = None
    for (key, value) in mmap.items():
        if isinstance(key, str):
            xdmKey_ = proc.make_string_value(key)

            if isinstance(value, str):
                xdmValue_ = proc.make_string_value(value)
            elif isinstance(value,int):
                xdmValue_ = proc.make_integer_value(value)
            elif isinstance(value,float):
                xdmValue_ = proc.make_integer_value(value)
            elif value in (True, False):
                xdmValue_ = proc.make_boolean_value(value)

            elif isinstance(value, PyXdmValue):
                xdmValue_ = value

            elif isinstance(value, PyXdmItem):
                xdmValue_ = value

            elif isinstance(value, PyXdmAtomicValue):
                xdmValue_ = value
            elif isinstance(value, PyXdmNode):
                xdmValue_ = value

            elif isinstance(value, PyXdmMap):
                xdmValue_ = value

            elif isinstance(value, PyXdmArray):
                xdmValue_ = value
            else:
                continue

            xdmMap[xdmKey_] = xdmValue_
        else:
                   raise Exception("Error in making Dictionary")

    return xdmMap


class HeiEditionsResolver(et.Resolver):
    def __init__(self):
        super().__init__()

    def resolve(self, system_url, public_id, context):
        if system_url.startswith("https://digi.ub.uni-heidelberg.de/"):
            response = requests.get(system_url)
            return self.resolve_string(response.text, context)


class HeiEditionsParser(et.XMLParser):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('load_dtd', True)
        kwargs.setdefault('strip_cdata', False)
        kwargs.setdefault('no_network', False)
        kwargs.setdefault('resolve_entities', False)
        kwargs.setdefault('encoding', 'utf-8')
        super().__init__(*args, **kwargs)
        self.resolvers.add(HeiEditionsResolver())
           
    def parse(self, source, base_url=None):
        tree = super().parse(source, base_url)
        tree.xinclude()
        return tree
    
    # def close(self):
    #     tree = super().close()
    #     tree.xinclude()
    #     return tree
        

def set_params_for_saxon(parameter_list, proc: PySaxonProcessor, executable):
    for parameter in parameter_list:
        for param, value in parameter.items():
            if value is True or value is False:
                value_f = proc.make_boolean_value(value)
            # Uncomment when saxonica fixes the bug
            elif isinstance(value, dict):
                xdmdict = create_xdm_dict(proc, value)
                value_f = proc.make_map(xdmdict)
            elif value.isnumeric():
                value_f = proc.make_float_value(value)
            elif value is None:
                continue
            else:
                value_f = proc.make_string_value(value)
            if value_f is not None:
                executable.set_parameter(param, value_f)


def apply_xslt(input_string, xslt_file, parameters=None) -> str:
    parameters = parameters or []
    with PySaxonProcessor(license=False) as proc:
        input_xdm = proc.parse_xml(xml_text=input_string, encoding='utf-8')
        xslt3 = proc.new_xslt30_processor()
        with importlib.resources.path('heipy.heipipe.xslt', xslt_file) as xslt_file_path:
            true_xslt_file = str(xslt_file_path)
            executable = xslt3.compile_stylesheet(
                stylesheet_file=true_xslt_file)
            if len(parameters) > 0:
                set_params_for_saxon(parameters, proc, executable)
            result_string = executable.transform_to_string(xdm_node=input_xdm)
            return result_string
    

def validate_xml_with_heieditions_schema(input_str= None,xml_file=None):
    """Validate an XML file using the heiEDITIONS schema (make sure to update)"""
    try:
        if input_str is None and xml_file is None:
            warnings.warn("Parameter needed for validation. Either file or content as string")
            sys.exit(1)
        xml_doc = None
        if xml_file:
            xml_doc = et.parse(xml_file, parser= HeiEditionsParser(resolve_entities=True))
        elif input_str:
            input_string_enc = input_str.encode('utf-8')
            xml_doc = et.fromstring(input_string_enc, parser=HeiEditionsParser(resolve_entities=True))
        if xml_doc is None:
            warnings.warn("Parameter needed for validation. Either file or content as string")
            sys.exit(1)

        # This is weirdly neccesary to resolve entities properly
        xml_doc_string = et.tostring(xml_doc, encoding='utf-8')
        xml_doc = et.fromstring(xml_doc_string)
        
        with importlib.resources.path('heipy.schema', 'tei_hes.rng') as schema_file_path:
            with open(schema_file_path, 'rb') as schema_file:
                relaxng_doc = et.parse(schema_file)
                relaxng = et.RelaxNG(relaxng_doc)
                if not relaxng.validate(xml_doc):
                    raise Exception(f"{RED}Validation failed:\n{relaxng.error_log}")
            
    except Exception as e:
        raise Exception(f"Error during validation: {e}")
    
    


