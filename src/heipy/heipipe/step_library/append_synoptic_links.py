import os
import re
from lxml import etree as et
from ..steps import PythonStep
from ...parsers import HeiEditionsParser
from ...namespaces import ns, prefix_format

# Compile regexes once at module level for performance
_POSITIONAL_REGEX = re.compile(r'^([a-z][a-z0-9\+\.\-]*):\b(left|right)\b\((.+)\)$')
_DIRECT_REGEX = re.compile(r'^([a-z][a-z0-9\+\.\-]*):(.+)$')


def append_synoptic_links_funct(root, parameters=None):
    if parameters is None:
        Warning.warn("parameters for append_synoptic_links is empty, this does nothing.")
        return root
    sigla_mapping = parameters.get('sigla_mapping')
    synoptic_map_path = os.path.abspath(parameters['synoptic_map'])
    synoptic_map_root = et.parse(synoptic_map_path, parser=HeiEditionsParser())
    base_file = parameters.get('base_file')
    base_file_name = base_file.split('/')[-1]
    base_file_config = sigla_mapping.get(base_file_name)
    if base_file_config is None:
        print(f"ERROR: Could not find configuration for {base_file_name} in the configuration file.")
        return root
    base_file_prefix = base_file_config.get('synoptic_pre')
    if base_file_prefix is None:
        print(f"ERROR: Could not find prefix for {base_file} in the configuration file.")
        return root
    listPrefixDef_out = root.find('.//tei:listPrefixDef', namespaces=ns)
    if listPrefixDef_out is None:
        print(f"ERROR: Could not find listPrefixDef in {base_file}. Please include it!")
        return root
    old_prefixDef = [x for x in listPrefixDef_out.iterchildren(et.Element)] # We need to delete repeated prefixDef in the synoptic_map.xml and in the concrete witness. We keep the ones from the synoptic map.
    old_idents = {x.get('ident'):x for x in old_prefixDef}
    for prefixdef in synoptic_map_root.findall('.//tei:prefixDef', namespaces=ns):
        filename = prefixdef.get('replacementPattern').split('/')[-2]
        file_config = sigla_mapping.get(filename)
        if file_config is None:
            continue
        siglum = file_config.get('siglum')
        ident = prefixdef.get('ident')
        if old_idents is not None:
            if old_idents.get(ident) is not None:
                listPrefixDef_out.remove(old_idents[ident])
        prefixdef_attrib_new = prefixdef.attrib
        prefixdef_attrib_new['replacementPattern'] = f'../{siglum}/{siglum}.xml'
        
        et.SubElement(listPrefixDef_out, prefix_format('tei', 'prefixDef'), prefixdef_attrib_new)


    processed_items = set()

    id_index = {el.attrib[prefix_format('xml','id')]: el for el in root.iter() if prefix_format('xml','id') in el.attrib}

    gaplist_el = synoptic_map_root.find('.//tei:list[@ana="hc:GapList"]', namespaces=ns)
    gaplist = {}
    if gaplist_el is not None:
        gaplist = {item.attrib['corresp']: item[0] for item in gaplist_el.iter(prefix_format("tei","item")) if item.attrib['corresp'].split(':')[0] == base_file_prefix }

    # Build caches to avoid expensive XPath queries in the loop
    gap_cache = {}  # Cache for gaps by their xml:id
    linkgrp_cache = {}  # Cache for linkGrp elements by their target

    # count = 0
    for link in synoptic_map_root.findall('.//tei:link', namespaces=ns):
        # count += 1
        # print(f"Processing link number {count}")
        new_element = True
        link_target = link.get('target').split()

        # First we find if there is in this link something pointing to an element in our text
        hook_info = [x for x in link_target if ':' in x and x.split(':', 1)[0] == base_file_prefix]
        if len(hook_info) < 1:
            continue
        if len(hook_info) > 1:
            print(f"Found two verses of the same manuscripts linking to each other: {hook_info}")

        hook_ident = hook_info[0]
        link_target = [x for x in link_target if x != hook_ident]  # Avoid O(n) remove operation
        hook_prefix, hook_pos, hook_id = parse_target(hook_ident)
        if hook_ident in processed_items:
            new_element = False
        processed_items.add(hook_ident)
        hook_el = id_index.get(hook_id)
        if hook_el is None:
            print(f"Could not find {hook_id} from {hook_ident}")
            continue
        
        

        if hook_pos is not None:
            gap_id = gap_xmlid(hook_pos, hook_id)
            if new_element:
                if hook_ident in gaplist:
                    gap = gaplist[hook_ident]
                else:
                    gap = et.Element(prefix_format('tei', 'gap'))
                    gap.set('ana', 'hc:PassiveSynopticGap')
                gap.set(prefix_format('xml', 'id'), gap_id)
                gap_cache[gap_id] = gap
            else:
                gap = gap_cache.get(gap_id)
                if gap is None:
                    gap = root.xpath(f'.//tei:gap[@xml:id="{gap_id}"]', namespaces=ns)[0]
                    gap_cache[gap_id] = gap
            if hook_pos == 'left':
                hook_el.addprevious(gap)
            if hook_pos == 'right':
                hook_el.addnext(gap)
            continue
        
        # hook_pos == None
        if hook_id == 'gap_leaf_1':
            continue
        linkgrp_target = f'#{hook_id}'
        if new_element:
            linkgrp = et.Element(prefix_format('tei', 'linkGrp'))
            linkgrp.set('target', linkgrp_target)
            linkgrp_cache[linkgrp_target] = linkgrp
        else:
            linkgrp = linkgrp_cache.get(linkgrp_target)
            if linkgrp is None:
                linkgrp = root.xpath(f'.//tei:linkGrp[@target="{linkgrp_target}"]', namespaces=ns)[0]
                linkgrp_cache[linkgrp_target] = linkgrp
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
    positional = _POSITIONAL_REGEX.match(target)
    if positional is not None:
        selector_prefix = positional.group(1)
        selector_position = positional.group(2)
        selector_id = positional.group(3)
        return selector_prefix, selector_position, selector_id

    direct = _DIRECT_REGEX.match(target)
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
    return PythonStep(funct=append_synoptic_links_funct, name="append_synoptic_link")
