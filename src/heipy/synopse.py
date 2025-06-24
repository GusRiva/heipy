import os
import copy
import codecs
import itertools
import warnings
from collections import defaultdict
from lxml import etree as et
import importlib.resources
import re

from .parsers import HeiEditionsParser
from .namespaces import ns, prefix_format
from .heiwarning import HeiWarning


def create_synopse(input:list, output:str, sigla_mapping:dict=None):
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
    all_verses = {}
    starting_elements = {}
    all_witnesses = []
    siglum_file_map = set()
    nones = 0
    empty_siglum = 1
    sigla_mapping = {} if sigla_mapping is None else sigla_mapping
    for input_file in input:
        root = et.parse(input_file, parser=HeiEditionsParser())
        siglum = root.find('./tei:teiHeader//tei:idno[@ana="hc:EditorialSiglum"]', namespaces=ns)
        if siglum is None:
            siglum = f'pre{empty_siglum}'
            empty_siglum += 1
            # warnings.warn(f"No siglum found in {input_file}. Continuing with next file.", HeiWarning)
            # continue
        else:
            siglum = siglum.text
        siglum_file_map.add((siglum, input_file))
        all_witnesses.append(siglum)
        
        # For fragments that start with a gap
        starting_gap = root.find(".//tei:gap[@xml:id='gap_leaf_1']", namespaces=ns)
        if starting_gap is not None:
            starting_elements[siglum] = "gap_leaf_1"
        
        for line in root.findall('.//tei:l', namespaces=ns):
            line_id = line.get(prefix_format('xml','id'))
            if line_id is None:
                continue
            if siglum not in starting_elements:
                starting_elements[siglum] = line_id
            n_att = line.get('n')
            if n_att is None:
                n_att = "{:.2f}".format(nones / 100)
                nones += 1
            try:
                float(n_att.replace(',', '.'))
            except:
                digits = re.search(f'\d+', n_att)
                if digits is None:
                    n_att = "{:.3f}".format(nones / 1000)
                    nones += 1          
                else:
                    n_att = "{:.4f}".format(int(digits.group(0)) / 10000)
            all_verses.setdefault(n_att, []).append({'id': line_id, 'siglum': siglum})
            
    all_verses = dict(sorted(all_verses.items(), key= lambda x: float(x[0].replace(',', '.'))))
    all_witnesses_len = len(all_witnesses)

    # print(all_verses)
    
    with importlib.resources.path('heipy.templates', 'synoptic_map.xml') as template_path:
        template_file = open(template_path, 'rb')
        output_tree = et.parse(template_file, HeiEditionsParser())
        output_root = output_tree.getroot()

        listprefixdef = output_root.find('.//tei:listPrefixDef', namespaces=ns) 
        for sig_info in sorted(siglum_file_map, key= lambda x: x[1]):
            prefix_ident = sigla_mapping.get(sig_info[0], sig_info[0])
            et.SubElement(listprefixdef, prefix_format('tei', 'prefixDef'), 
                          {'matchPattern': '(.+)', 
                           'ident': prefix_ident, 
                           'replacementPattern': f"../{sig_info[1]}/$1",
                           'ana': 'hc:SynopticTextPrefixDefinition'})

        standoff_el = output_root.find('.//tei:standOff', namespaces=ns)
        standoff_el.clear()
        previous = {x:'' for x in all_witnesses}
        for verse_nr, id_hs_dict in all_verses.items():
            for wit in id_hs_dict:
                previous[wit.get('siglum')] = wit['id']
            link_el = et.Element(prefix_format('tei','link'))
            target = ' '.join([f'{sigla_mapping.get(x['siglum'],x['siglum'])}:{x['id']}' for x in sorted(id_hs_dict, key= lambda x: x['siglum'])])
            # If some testimonies do not have the verse number:
            if len(id_hs_dict) < all_witnesses_len:
                target += ' '
                implicit_witnesses = sorted(list(set(all_witnesses) ^ set([x['siglum'] for x in id_hs_dict])))
                for iwi in implicit_witnesses:
                    if previous[iwi] != '':
                        target += f'{sigla_mapping.get(iwi, iwi)}:right({previous[iwi]}) '
                    else:
                        if starting_elements[iwi] == 'gap_leaf_1':
                            target += f'{sigla_mapping.get(iwi, iwi)}:gap_leaf_1 '
                        else:
                            target += f'{sigla_mapping.get(iwi, iwi)}:left({starting_elements[iwi]}) '
                target = target.strip()
            
            link_el.set('target', target)
            standoff_el.append(link_el)
        
        list_gap = et.Element(prefix_format("tei","list"), {'ana': 'hc:GapList'})
        standoff_el.append(list_gap)


        output_tree.write(output, pretty_print=True, xml_declaration=True, encoding='utf-8')


    return


def transform_synopse(input:str):
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
    in_root = et.parse(input_path, parser=HeiEditionsParser())

    prefix_defs = in_root.findall('.//tei:prefixDef[@ana="hc:SynopticTextPrefixDefinition"]', namespaces=ns)
    witness_ids = [x.get('ident') for x in prefix_defs]
    witness_files = [ os.path.basename( x.get('replacementPattern')[:-3] )  for x in prefix_defs]
    master_dict = { x: {'filename': y, 'linkgrps': defaultdict(list)}   for x, y in zip(witness_ids, witness_files)}
    
    # all_link_groups = defaultdict(list)
    for link in in_root.findall('./tei:standOff//tei:link', namespaces=ns):
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
            ms_id = first_item[0].split(':')[0]
            if ms_id not in master_dict.keys():
                continue
            master_dict[ms_id]['linkgrps'][first_item].append(second_item)
            # all_link_groups[first_item].append(second_item)
    for sigle in master_dict:
        out_root = et.Element(prefix_format('tei', 'standOff'))
        out_file_name = master_dict[sigle]['filename']
        for linkgrp_source, linkgrp_targets in  master_dict[sigle]['linkgrps'].items():
            linkgrp_el = et.Element(prefix_format('tei', 'linkGrp'))
            link_grp_target = linkgrp_source[0]
            linkgrp_el.set('target', link_grp_target)
            
            if '(' in link_grp_target:
                # Set ana attribute
                node_type = linkgrp_source[1]
                if node_type in targetfunc_dict.keys():
                    linkgrp_el.set('ana', targetfunc_dict[node_type] )
                    if node_type == 'default' or node_type == 'passiveGap':
                        out_root.append(linkgrp_el)
                        continue
                else:
                    warnings.warn(f'Could not identify node type {node_type}', HeiWarning)
            
            for target in linkgrp_targets:
                # Create the ptr elements
                link_el = et.Element(prefix_format('tei','ptr'))
                link_el.set('target', target[0])
                if target[1] == 'default' and '(' in target[0]:
                    link_el.set('ana', targetfunc_dict['passiveGap'])
                elif target[1] != 'default':
                    link_el.set('ana', targetfunc_dict[target[1]])
                linkgrp_el.append(link_el)

            out_root.append(linkgrp_el)

        tree_str = et.tostring(out_root, encoding='unicode', pretty_print=True)
        with codecs.open(f'synopse/linkgrp/{out_file_name}', 'wb', 'utf-8') as output_file:
            for line in tree_str.split('\n'):
                output_file.write(line + '\n')
    
    return

def incept_linkgrp(semantic_file:str, linkgrp_file:str, output:str):
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
