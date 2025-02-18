import os 
import re
import warnings
from lxml import etree as et
from ..steps import PythonStep
from ...parsers import HeiEditionsParser
from ...namespaces import ns, prefix_format
from ...heiwarning import HeiWarning


def create_synoptic_wit_func(root, parameters): 
    synoptic_map_path = os.path.abspath(parameters['synoptic_map'])
    synoptic_map_root = et.parse(synoptic_map_path, parser=HeiEditionsParser())
    link_groups = synoptic_map_root.findall('.//tei:linkGrp', namespaces=ns)

    base_file_name = parameters.get('base_file_name', '')
    prefixDefsMap = synoptic_map_root.findall(f'./tei:teiHeader/tei:encodingDesc/tei:listPrefixDef//tei:prefixDef', namespaces=ns)
    wit = None
    list_prefix_def = root.find('.//tei:listPrefixDef', namespaces=ns)
    for prefixDef in prefixDefsMap:
        if base_file_name in prefixDef.get('replacementPattern') and prefixDef.get('ana') == 'hc:SynopticTextPrefixDefinition':
            wit = prefixDef.get('ident')
            continue
        prefixDef.attrib['replacementPattern'] = prefixDef.get('replacementPattern').replace('../texts/', './')
        list_prefix_def.append(prefixDef)
    if wit is None:
        warnings.warn(f"Prefix definition not found for {base_file_name}", HeiWarning)
        return

    processed_gaps = set() # This will store the gaps already created    
    for linkgrp in link_groups:
        grp_target = linkgrp.get('target')
        grp_target_prefix, grp_target_position, grp_target_id = parse_target(grp_target)
        if grp_target_prefix is None:
            warnings.warn(f"Invalid target: {grp_target}", HeiWarning)
            continue
        if grp_target_prefix != wit:
            continue
        
        corres_el = root.find(f'.//*[@xml:id="{grp_target_id}"]', namespaces=ns)
        if corres_el is None:  
            warnings.warn(f"Corresponding element not found: {grp_target_id}", HeiWarning)
            continue
        for ptr in linkgrp.findall(f'./tei:ptr', namespaces=ns):
            ptr_target = ptr.get('target')
            ptr_target_prefix, ptr_target_position, ptr_target_id = parse_target(ptr_target)
            if ptr_target_position is None:
                continue
            gap_type_abbr = 'p' if 'Passive' in ptr.get('ana') else 'a'
            ptr.set('target', f'{ptr_target_prefix}:gap-{ptr_target_position}-{ptr_target_id}-{gap_type_abbr}')

        # Handle linkGrp for actual existing IDs
        if grp_target_position is None:
            linkgrp.attrib['target'] = linkgrp.get('target').replace(f'{wit}:', '#')
            corres_el.addprevious(linkgrp)
            continue

        # Handle linkGrp for 'right' or 'left' i.e. gaps
        gap_el = et.Element(prefix_format('tei','gap'))
        gap_type = linkgrp.get('ana')
        gap_el.set('ana', gap_type)
        gap_type_abbr = 'p' if 'Passive' in gap_type else 'a'
        gap_id = f'gap-{grp_target_position}-{grp_target_id}-{gap_type_abbr}'
        gap_el.set(prefix_format('xml', 'id'), gap_id)
        linkgrp.attrib['target'] = f'#{gap_id}' 
        if grp_target_position == 'left':
            if gap_type_abbr == 'a':
                corres_el.addprevious(linkgrp)
            corres_el.addprevious(gap_el)
        elif grp_target_position == 'right':
            corres_el.addnext(gap_el)
            if gap_type_abbr == 'a':
                corres_el.addnext(linkgrp)
        else:
            warnings.warn(f'Invalid target position: {grp_target_position} referencing {grp_target_id}', HeiWarning)

    return root


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
    
def get_step():
    return PythonStep(funct=create_synoptic_wit_func, name="create_synoptic_wit")
