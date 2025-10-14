import os
import codecs
import pathlib
import importlib.resources

import requests
from lxml import etree as et
from saxonche import PySaxonProcessor, PyXdmValue, PyXdmItem, PyXdmAtomicValue, PyXdmNode, PyXdmMap, PyXdmArray, create_xdm_dict
import warnings
import sys
import re
import html

from .colors import *
from .namespaces import ns

class HeiEditionsResolver(et.Resolver):
    def __init__(self):
        super().__init__()

    def resolve(self, system_url, public_id, context):

        if system_url == "https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/declarations/heieditions-entities.txt":
            with importlib.resources.open_text('heipy.schema', 'heieditions-entities.txt') as entities_file:
                return self.resolve_string(entities_file.read(), context)

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

def heiparse(source, parser=None, input_format='file', output_format='tree', egxml=False, xinclude=False, base_url=''):
    """
    Parse an XML source using a specified parser (dafaults to HeiEditionsParser) and optionally process XInclude directives.
    Args:
        source (str or file-like object): The XML source to parse. This can be a file path or a file-like object or a xml-string (see input_format)
        parser (xml.etree.ElementTree.XMLParser, optional): The parser to use for parsing the XML. 
            If not provided, a default `HeiEditionsParser` instance will be used.
        xinclude (bool, optional): Whether to process XInclude directives in the XML. Defaults to True.
        output_format (str, optional): Output as 'tree' (lxml etree object) or as 'str' (string)
        input_format (str, optional): Input as 'file' (file-like object or path) or as 'string' (the xml string)

    Returns:
        xml.etree.ElementTree.ElementTree: The parsed XML tree.

    Raises:
        xml.etree.ElementTree.ParseError: If there is an error during parsing.
    """      

    parser = parser or HeiEditionsParser()

    if input_format == 'file':
        if egxml:
            input_file = codecs.open(source, "r", "utf-8")
            input_string = preprocess_egxml(input_file.read())
            input_string = input_string.encode('utf-8')
            root_el = et.fromstring(input_string, parser, base_url=base_url)
            tree = et.ElementTree(root_el)
        else:
            tree = et.parse(source, parser)
    elif input_format == 'string':
        root_el = et.fromstring(source, parser, base_url=base_url)
        tree = et.ElementTree(root_el)
    else:
        raise NameError(f"Unknown input_format type {input_format}. Must be 'file' or 'string'.")

    if xinclude:
        tree.xinclude()

    if output_format == 'tree':
        return tree
    elif output_format == 'str':
        return et.tostring(tree, method="xml", encoding="unicode")
    else:
        raise TypeError("The output_format parameter must be either 'tree' or 'str'")

def set_params_for_saxon(parameter_list, proc: PySaxonProcessor, executable):
    for parameter in parameter_list:
        for param, value in parameter.items():
            if value is None:
                continue
            elif value is True or value is False:
                value_f = proc.make_boolean_value(value)
            elif isinstance(value, dict):
                xdmdict = create_xdm_dict(proc, value)
                value_f = proc.make_map(xdmdict)
            elif value.isnumeric():
                value_f = proc.make_float_value(value)
            else:
                value_f = proc.make_string_value(value)
            if value_f is not None:
                executable.set_parameter(param, value_f)


def apply_xslt(input_string=None, xslt_file=None, parameters=None, output_dir=None, input_xdm=None, output_xdm=False, proc=None):
    """
    Apply XSLT transformation with flexible input/output formats.

    Args:
        input_string: XML string (if input_xdm is None)
        xslt_file: Path to XSLT file
        parameters: XSLT parameters
        output_dir: Output directory for base URI
        input_xdm: PyXdmNode object (optional, for batched XSLT steps)
        output_xdm: If True, return XDM node instead of string
        proc: PySaxonProcessor instance (optional, for batched XSLT steps)

    Returns:
        str or PyXdmNode depending on output_xdm
    """
    parameters = parameters or []

    # If processor is provided (batched mode), use it; otherwise create new one
    if proc is None:
        # Create processor with context manager for single transformation
        with PySaxonProcessor(license=False) as proc:
            # Parse input if needed
            if input_xdm is None:
                if input_string is None:
                    raise ValueError("Either input_string or input_xdm must be provided to apply_xslt")
                input_xdm = proc.parse_xml(xml_text=input_string, encoding='utf-8')

            # Compile and execute XSLT
            xslt3 = proc.new_xslt30_processor()
            base_output_path = os.path.dirname(os.path.abspath(xslt_file)) if output_dir is None else output_dir
            executable = xslt3.compile_stylesheet(stylesheet_file=xslt_file)

            if len(parameters) > 0:
                set_params_for_saxon(parameters, proc, executable)

            # Set the global context item for the transformation
            # input_xdm could be a PyXdmValue (sequence) or PyXdmItem (single item)
            # If it's a sequence, get the first item; otherwise use it directly
            if hasattr(input_xdm, '__iter__') and hasattr(input_xdm, 'size') and input_xdm.size > 0:
                context_item = input_xdm[0]  # Get first item from sequence
            else:
                context_item = input_xdm  # Already a single item
            executable.set_global_context_item(xdm_item=context_item)

            if output_xdm:
                # Return XDM value for next XSLT step
                # Use apply_templates_returning_value which accepts PyXdmValue, not just PyXdmNode
                result_xdm = executable.apply_templates_returning_value(xdm_value=input_xdm)
                return result_xdm
            else:
                # Return string
                # Use apply_templates_returning_string which works with PyXdmValue
                result_string = executable.apply_templates_returning_string(xdm_value=input_xdm)
                return result_string
    else:
        # Batched mode - processor already exists, don't close it
        # Parse input if needed
        if input_xdm is None:
            if input_string is None:
                raise ValueError("Either input_string or input_xdm must be provided to apply_xslt")
            input_xdm = proc.parse_xml(xml_text=input_string, encoding='utf-8')

        # Compile and execute XSLT
        xslt3 = proc.new_xslt30_processor()
        base_output_path = os.path.dirname(os.path.abspath(xslt_file)) if output_dir is None else output_dir
        executable = xslt3.compile_stylesheet(stylesheet_file=xslt_file)

        if len(parameters) > 0:
            set_params_for_saxon(parameters, proc, executable)

        # Set the global context item for the transformation
        # input_xdm could be a PyXdmValue (sequence) or PyXdmItem (single item)
        # If it's a sequence, get the first item; otherwise use it directly
        if hasattr(input_xdm, '__iter__') and hasattr(input_xdm, 'size') and input_xdm.size > 0:
            context_item = input_xdm[0]  # Get first item from sequence
        else:
            context_item = input_xdm  # Already a single item
        executable.set_global_context_item(xdm_item=context_item)

        if output_xdm:
            # Return XDM value for next XSLT step
            # Use apply_templates_returning_value which accepts PyXdmValue, not just PyXdmNode
            result_xdm = executable.apply_templates_returning_value(xdm_value=input_xdm)
            return result_xdm
        else:
            # Return string
            # Use apply_templates_returning_string which works with PyXdmValue
            result_string = executable.apply_templates_returning_string(xdm_value=input_xdm)
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
    

def simple_xslt(input, xslt, output, parameters=None, xinclude=False, egxml=False):
    """
    Applies an XSLT transformation to an input file and writes the result to an output file.

    Args:
        input (str): The path to the input file containing the XML content.
        xslt (str): The XSLT stylesheet to be applied.
        output (str): The path to the output file where the transformed content will be written.
        parameters (dict, optional): A dictionary of parameters to pass to the XSLT transformation. Defaults to None.

    Raises:
        FileNotFoundError: If the input file does not exist.
        IOError: If there is an error reading the input file or writing to the output file.
        Exception: If the XSLT transformation fails.

    Returns:
        None
    """
    input_string = heiparse(input, output_format='str', xinclude=xinclude, egxml=egxml, base_url=input)    
    output_dir = os.path.dirname(os.path.abspath(output))
    result = apply_xslt(input_string, xslt, parameters, output_dir=output_dir)

    # if egxml:
    #     result = unscape_egxml(result)

    with codecs.open(output, 'w', 'utf-8') as output_file:
        output_file.write(result)


def preprocess_egxml(raw_xml: str) -> str:
    def wrap_with_cdata(match):
        content = match.group(1)
        return f'<egXML xmlns="http://www.tei-c.org/ns/Examples"><![CDATA[{content}]]></egXML>'

    # Regex: capture content between <egXML> and </egXML> non-greedily (DOTALL = allow newlines)
    pattern = re.compile(r"<egXML[^>]*>(.*?)</egXML>", flags=re.DOTALL)
    return pattern.sub(wrap_with_cdata, raw_xml)


def unscape_egxml(input_string):
    root = heiparse(input_string.encode('utf-8'), input_format='string', output_format="tree")
    for elem in root.findall(".//ex:egXML", ns):
        if elem.text is not None:
            # elem.text = elem.text[9:-3] # indeces to remove <![CDATA[ ... ]]
            unescaped = html.unescape(elem.text)
            try:
                # Try parsing the content as XML and inserting it
                wrapper = et.fromstring(f"<wrapper>{unescaped}</wrapper>")
                elem.clear()
                elem.text = wrapper.text
                elem.extend(wrapper)
            except et.XMLSyntaxError:
                # If it's not valid XML, just keep it as text
                elem.text = unescaped
    input_string = et.tostring(root).decode('utf-8')
    return input_string