import os 
import re
from lxml import etree as et
from ..steps import PythonStep
from ...parsers import HeiEditionsParser
from ...namespaces import ns, prefix_format


def append_synoptic_links_funct(root, parameters): 
    sigla_mapping = dict([(value, key) for key, value in parameters.get('sigla_mapping').items()])
    synoptic_map_path = os.path.abspath(parameters['synoptic_map'])
    synoptic_map_root = et.parse(synoptic_map_path, parser=HeiEditionsParser())
    base_file = parameters.get('base_file')
    listPrefixDef_out = root.find('.//tei:listPrefixDef', namespaces=ns)
    text_ident = None
    for prefixdef in synoptic_map_root.findall('.//tei:prefixDef', namespaces=ns):
        ident = prefixdef.get('ident')
        replacement_pattern = prefixdef.get('replacementPattern')
        if replacement_pattern[3:-3] == base_file:
            text_ident = ident
            continue
        prefixdef_attrib_new = prefixdef.attrib
        prefixdef_attrib_new['replacementPattern'] = prefixdef_attrib_new.get('replacementPattern', '').replace('../texts/', f'../{sigla_mapping.get(ident)}/')
        et.SubElement(listPrefixDef_out, prefix_format('tei', 'prefixDef'), prefixdef_attrib_new)
    if text_ident is None:
        print(f"Could not find ident for {prefixdef.attrib}")
        return root
    processed_items = set()

    id_index = {el.attrib[prefix_format('xml','id')]: el for el in root.iter() if prefix_format('xml','id') in el.attrib}

    gaplist_el = synoptic_map_root.find('.//tei:list[@ana="hc:GapList"]', namespaces=ns)
    gaplist = {item.attrib['corresp']: item[0] for item in gaplist_el.iter(prefix_format("tei","item")) if item.attrib['corresp'].split(':')[0] == text_ident }

    for link in synoptic_map_root.findall('.//tei:link', namespaces=ns):
        new_element = True
        link_target = re.split(r'\s',link.get('target'))

        # First we find if there is in this link something pointing to an element in our text
        hook_info = [ x for x in link_target if ':' in x and x.split(':')[0] == text_ident]
        if len(hook_info) < 1:
            continue
        if len(hook_info) > 1:
            print(f"Found two verses of the same manuscripts linking to each other: {hook_info}")
        
        hook_ident = hook_info[0]
        link_target.remove(hook_ident)
        hook_prefix, hook_pos, hook_id = parse_target(hook_ident)
        if hook_ident in processed_items:
            new_element = False
        processed_items.add(hook_ident)
        hook_el = id_index.get(hook_id)
        if hook_el is None:
            print(f"Could not find {hook_id} from {hook_ident}")
            continue
        
        

        if hook_pos is not None:
            if new_element:
                if hook_ident in gaplist.keys():
                    gap = gaplist.get(hook_ident)
                else:
                    gap = et.Element(prefix_format('tei', 'gap'))
                    gap.set('ana', 'hc:PassiveSynopticGap')
                gap.set(prefix_format('xml', 'id'), gap_xmlid(hook_pos, hook_id))
            else:
                gap = root.xpath(f'.//tei:gap[@xml:id="{gap_xmlid(hook_pos, hook_id)}"]', namespaces=ns)[0]
            if hook_pos == 'left':
                hook_el.addprevious(gap)
            if hook_pos == 'right':
                hook_el.addnext(gap)
            continue
        
        # hook_pos == None
        if hook_id == 'gap_leaf_1':
            continue
        if new_element:
            linkgrp = et.Element(prefix_format('tei', 'linkGrp'))
            linkgrp.set('target', f'#{hook_id}')
        else:
            linkgrp = root.xpath(f'.//tei:linkGrp[@target="#{hook_id}"]', namespaces=ns)[0]
        for target_item in link_target:
            target_prefix, target_pos, target_id = parse_target(target_item)
            ptr = et.SubElement(linkgrp, prefix_format('tei','ptr'))
            ptr.set('target', target_relative_to_gap([target_prefix, target_pos, target_id]))
        hook_el.addprevious(linkgrp)

    return root

def gap_xmlid(pos:str,id:str):
    return f"gap-{pos}-{id}"

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
    positional = re.match(r'^([a-zA-Z\.\+]+):\b(left|right)\b\((.+)\)$', target)
    if positional is not None:
        selector_prefix = positional.group(1)
        selector_position = positional.group(2)
        selector_id = positional.group(3)
        return selector_prefix, selector_position, selector_id
    
    direct = re.match(r'^([a-zA-Z\.\+]+):(.+)$', target)
    if direct is not None:
        return direct.group(1), None, direct.group(2)
    
    return None, None, None

def target_relative_to_gap(target:str|list):
    if isinstance(target, str):
        target = parse_target(target)
    position = target[1]
    if position is None:
        return f'{target[0]}:{target[2]}'
    return f'{target[0]}:gap-{target[1]}-{target[2]}'

def get_step():
    return PythonStep(funct=append_synoptic_links_funct, name="create_synoptic_wit")
