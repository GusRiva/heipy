import os.path
import copy
import itertools
import warnings
from collections import defaultdict
from lxml import etree as et
from os import path
import importlib.resources
import re

from .parsers import HeiEditionsParser
from .namespaces import ns, prefix_format
from .heiwarning import HeiWarning


def create_synopse(input:list, output:str):
    """
    Creates a synoptic map in the abbreviated syntax from a list of input TEI-XML files and writes the result to an output file.

    Args:
        input (list): A list of file paths to the input XML files.
        output (str): The file path to the output file where the synopse will be written.

    Raises:
        HeiWarning: If no siglum is found in an input file, a warning is issued and the file is skipped.

    The function processes each input XML file to extract sigla and line IDs. It collects all sigla and line IDs,
    and writes the synopse to the specified output file.
    It is a requirement that the xml:id of the lines match across files.
    """
    all_ids = {}
    starting_elements = {}
    all_witnesses = []
    for input_file in input:
        root = et.parse(input_file, parser=HeiEditionsParser())
        siglum = root.find('./tei:teiHeader//tei:idno[@ana="hc:EditorialSiglum"]', namespaces=ns)
        if siglum is None:
            warnings.warn(f"No siglum found in {input_file}. Continuing with next file.", HeiWarning)
            continue
        siglum = siglum.text
        all_witnesses.append(siglum)
        for line in root.findall('.//tei:l', namespaces=ns):
            line_id = line.get(prefix_format('xml','id'))
            if siglum not in starting_elements:
                starting_elements[siglum] = line_id
            if line_id is None:
                continue
            all_ids.setdefault(line_id, []).append(siglum)
    all_witnesses_len = len(all_witnesses)
    
    with importlib.resources.path('heipy.templates', 'synoptic_map.xml') as template_path:
        template_file = open(template_path, 'rb')
        output_tree = et.parse(template_file, HeiEditionsParser())
        output_root = output_tree.getroot()
        standoff_el = output_root.find('.//tei:standOff', namespaces=ns)
        standoff_el.clear()
        previous = {x:'' for x in all_witnesses}
        for available_id, in_wit in all_ids.items():
            for wit in in_wit:
                previous[wit] = available_id
            link_el = et.Element(prefix_format('tei','link'))
            target = ' '.join([f'wit{x}:{available_id}' for x in sorted(in_wit)])
            if len(in_wit) < all_witnesses_len:
                target += ' '
                implicit_witnesses = list(set(all_witnesses) ^ set(in_wit))
                target += ' '.join(
                    f'wit{x}:right({previous[x]})' if previous[x] != '' else f'wit{x}:left({starting_elements[x]})'
                    for x in implicit_witnesses
                )

            
            link_el.set('target', target)
            standoff_el.append(link_el)
            
        output_tree.write(output, pretty_print=True, xml_declaration=True, encoding='utf-8')


    return


def transform_synopse(input:str, output:str):
    """
    Transforms an abbreviated synoptic map (collection of <link>) to an expanded synoptic map (collection of <linkGrp>).

    Args:
        input (str): The path to the input TEI XML file.
        output (str): The path where the transformed XML file will be saved.

    Returns:
        None
    """
    # Values
    targetfunc_dict = {
        'default': 'hc:SynopticPassiveGap',
        'passiveGap': 'hc:SynopticPassiveGap',
        'activeGap': 'hc:SynopticActiveGap'
    }


    input_path = os.path.abspath(input)
    root = et.parse(input_path, parser=HeiEditionsParser())

    prefix_defs = root.findall('.//tei:prefixDef[@ana="hc:SynopticTextPrefixDefinition"]', namespaces=ns)
    witness_ids = [x.get('ident') for x in prefix_defs]
    
    # Make a copy of the root, remove the text and fill with the new content
    new_root = copy.deepcopy(root)
    new_standoff = new_root.find('.//tei:standOff', namespaces=ns)
    new_standoff.clear()

    def_dict = defaultdict(list)
    for link in root.findall('./tei:standOff//tei:link', namespaces=ns):
        link_target = link.get('target')
        target_tokens = link_target.split()
        link_targfunc = link.get('targFunc')
        link_targfunc_tokens = list()
        if link_targfunc is None:
            link_targfunc_tokens = ['default' for x  in target_tokens]
        else:
            link_targfunc_tokens = link_targfunc.split()
        target_tokens_plus = [ (x,y) for x,y in zip(target_tokens, link_targfunc_tokens)]
        combinations = list(itertools.permutations(target_tokens_plus, 2))
        for first_item, second_item in combinations:
            def_dict[first_item].append(second_item)
    grouped = [[k,sorted(v, key= lambda x: x[0])] for k, v in def_dict.items()]
    for group in grouped:
        print(group)
        link_grp_target = group[0][0]
        link_grp = et.Element(prefix_format('tei','linkGrp'))        
        link_grp.set('target', link_grp_target)
        if '(' in link_grp_target:
            node_type = group[0][1]
            if node_type in targetfunc_dict.keys():
                link_grp.set('ana', targetfunc_dict[node_type] )
            else:
                warnings.warn(f'Could not identify node type {node_type}', HeiWarning)
        for target in group[1]:
            link_el = et.Element(prefix_format('tei','ptr'))
            link_el.set('target', target[0])
            if target[1] == 'default' and '(' in target[0]:
                link_el.set('ana', targetfunc_dict['passiveGap'])
            elif target[1] != 'default':
                link_el.set('ana', targetfunc_dict[target[1]])
            link_grp.append(link_el)

        new_standoff.append(link_grp)

    new_root.write(output, pretty_print=True, xml_declaration=True, encoding='utf-8')

    return

def parse_target(target:str):
    """
    Parses a target string to extract the selector prefix, position, and ID.
    The target string can be in one of two formats:
    1. 'prefix:position(id)' - where 'prefix' is a sequence of lowercase letters, dots, or plus signs,
        'position' is either 'left' or 'right', and 'id' is any string.
    2. 'prefix:id' - where 'prefix' is a sequence of lowercase letters, dots, or plus signs, and 'id' is any string.
    Args:
        target (str): The target string to be parsed.
    Returns:
        tuple: A tuple containing three elements:
            - selector_prefix (str or None): The prefix part of the target string.
            - selector_position (str or None): The position part of the target string, if present.
            - selector_id (str or None): The ID part of the target string.
            If the target string does not match any of the expected formats, all elements of the tuple will be None.
    """
    positional = re.match(r'^([a-z\.\+]+):\b(left|right)\b\((.+)\)$', target)
    if positional is not None:
        selector_prefix = positional.group(1)
        selector_position = positional.group(2)
        selector_id = positional.group(3)
        return selector_prefix, selector_position, selector_id
    
    direct = re.match(r'^([a-z\.\+]+):(.+)$', target)
    if direct is not None:
        return direct.group(1), None, direct.group(2)
    
    return None, None, None
