import os
from pathlib import Path
import codecs
import itertools
import warnings
from collections import defaultdict, OrderedDict
from lxml import etree as et
import importlib.resources
import re
import networkx as nx
from itertools import permutations
import shutil

from .parsers import HeiEditionsParser
from .namespaces import ns, prefix_format, ns_tags
from .heiwarning import HeiWarning


def _first_element(clique, base_text: str | None = None):
    first_element = None
    if isinstance(clique, list):
        if len(clique) > 0:
            first_element = clique[0]
            if base_text is not None:
                found_base_text = [
                    x for x in clique
                    if x.startswith(f'{base_text}:') and 'right(' not in x and 'left(' not in x
                ]
                if len(found_base_text) == 1:
                    first_element = found_base_text[0]
    else:
        first_element = clique
    return first_element


def extract_number(clique, base_text: str | None = None):
    """Returns a (major, minor) tuple for ordinal sorting, e.g. l_12.10 sorts after l_12.9."""
    first_element = _first_element(clique, base_text)
    if first_element is None:
        return (0, 0)

    match = re.search(r'(\d+)(?:\.(\d+))?', str(first_element).split(':', 1)[1])
    if not match:
        return (0, 0)
    major, minor = match.groups()
    return (int(major), int(minor) if minor is not None else 0)


def extract_number_str(clique, base_text: str | None = None) -> str:
    """Like extract_number, but keeps the original digit string (e.g. trailing zeros)."""
    first_element = _first_element(clique, base_text)
    if first_element is None:
        return "0"

    match = re.search(r'\d+(?:\.\d+)?', str(first_element).split(':', 1)[1])
    return match.group() if match else "0"


def sort_clique(clq, base_text=None):
    if base_text is not None:
        base_item = None
        for i in range(len(clq)):
            if clq[i].startswith(f"{base_text}:"):
                base_item = clq.pop(i)
                break
        if base_item is not None:
            return [base_item] + sorted(clq)

    return sorted(clq)


def incept_linkgrp(semantic_file: str, linkgrp_file: str, output: str):
    return


def parse_target(target: str):
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
    positional = re.match(r"^([a-z\.\+]+):\b(left|right)\b\((.+)\)$", target)
    if positional is not None:
        selector_prefix = positional.group(1)
        selector_position = positional.group(2)
        selector_id = positional.group(3)
        return selector_prefix, selector_position, selector_id

    direct = re.match(r"^([a-z\.\+]+):(.+)$", target)
    if direct is not None:
        return direct.group(1), None, direct.group(2)

    return None, None, None


def create_synopse_graphs(
    input: list, 
    output:str, 
    sigla_mapping: dict = {}, 
    map_criterion="xml:id", 
    base_text:str | None = None
):
    valid_map_criterion = ["n", "xml:id", "hei:altN"]
    if map_criterion not in valid_map_criterion:
        raise NameError(
            f"The parameter map_criterion must be one of {valid_map_criterion}"
        )

    sigla_mapping = {} if sigla_mapping is None else sigla_mapping
    output_file = output if output is not None else 'synopses/default/synoptic.xml'
    tags_to_consider = ["l", "p"]
    witness_graphs = {}
    syn_graph = nx.Graph()
    # xmlids = {}
    prefixes = []
    for input_file in input:
        wit_graph = nx.DiGraph()
        root = et.parse(input_file, parser=HeiEditionsParser())
        file_mapping = sigla_mapping.get(input_file.split("/")[1])
        
        prefix = None
        if file_mapping:
            prefix = file_mapping.get("synoptic_pre")
        if prefix is None:
            print(f"Could not find prefix for {input_file}!!")
            continue
        prefixes.append(prefix)
        previous = None
        for line in root.iter(*ns_tags(ns.get("tei"), *tags_to_consider)):
            line_id = line.get(prefix_format("xml", "id"))
            if line_id is None:
                continue
            wit_graph.add_node(line_id)
            if previous is not None:
                wit_graph.add_edge(previous, line_id)
            previous = line_id

        # nx.write_graphml(wit_graph, f"synopses/synoptic_{prefix}.graphml")
        witness_graphs[prefix] = wit_graph

    for pre1, pre2 in permutations(prefixes, 2):
        graph1 = witness_graphs[pre1]
        graph2 = witness_graphs[pre2]
        print(f"Processing nodes in text {output} from {pre1} to {pre2}")
        start_node = [node for node in graph1.nodes() if graph1.in_degree(node) == 0]
        if len(start_node) < 1:
            warnings.warn(f"Could not find start node for {pre1}!: Skipping.")
            continue
        start_node = start_node[0]
        process_nodes(start_node, syn_graph, graph1, pre1, graph2, pre2, None, None)

    non_gap_graph = syn_graph.subgraph([x for x in syn_graph.nodes() if syn_graph.nodes[x].get('type') != 'gap'])
    cliques = list()
    for clique in nx.find_cliques(non_gap_graph):
        gap_nodes_for_clique = list()
        used_prefs = set()
        for cl_node in clique:
            edges = syn_graph.edges(cl_node)
            for edge in edges:
                con_node = edge[1]
                if 'right(' in con_node or 'left(' in con_node:
                    node_pref = con_node.split(':')[0]
                    if node_pref in used_prefs:
                        old_repeated = [x for x in gap_nodes_for_clique if x.startswith(f"{node_pref}:")]
                        if len(old_repeated) > 0:
                            old_repeated = old_repeated[0]
                            repeated_sorted = sorted([old_repeated] + [con_node], key= extract_number)
                            gap_nodes_for_clique.remove(old_repeated)
                            con_node = repeated_sorted[-1] # If there is a conflict with many gaps in the same click for the same manuscript, use the biggest number, probably right
                    used_prefs.add(node_pref)   
                    gap_nodes_for_clique.append(con_node)
        cliques.append(sort_clique(list(clique), base_text) + gap_nodes_for_clique)
            
    cliques = sorted(cliques, key=lambda clique: extract_number(clique, base_text))

    
    os.makedirs(os.path.dirname(output_file), exist_ok= True)
    
    with codecs.open(output_file, mode='w', encoding='utf-8') as output:
        output.write('''<?xml version='1.0' encoding='UTF-8'?>
<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml"
	schematypens="http://purl.oclc.org/dsdl/schematron"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
   <teiHeader>
      <fileDesc>
         <titleStmt>
            <title>Synoptische Karte</title>
         </titleStmt>
         <publicationStmt>
            <p>Publication Information</p>
         </publicationStmt>
         <sourceDesc>
            <p>Information about the source</p>
         </sourceDesc>
      </fileDesc>
      <encodingDesc>
         <listPrefixDef>
            <prefixDef ident="hc" matchPattern="(.+)" replacementPattern="https://lod.ub.uni-heidelberg.de/ontologies/heieditions/hc/current/$1"/>
        ''')
        for sig, sig_data in sigla_mapping.items():
            output.write(f'    <prefixDef matchPattern="(.+)" ident="{sig_data['synoptic_pre']}" replacementPattern="../texts/{sig}/$1" ana="hc:SynopticTextPrefixDefinition"/>\n        ')
        output.write('''</listPrefixDef>
      </encodingDesc>
   </teiHeader>''')
        output.write('<standOff>')
        for cliq in cliques:
            output.write(f'<link n="{extract_number_str(cliq)}" target="{' '.join(cliq)}"/>')
        output.write('</standOff></TEI>')
    
    # Create the backup copy
    output_file_path = Path(output_file)
    shutil.copy2(output_file, output_file_path.with_name(f"{output_file_path.stem}.bak{output_file_path.suffix}"))
    
    return


def process_nodes(
    start_node: str,
    G: nx.Graph,
    source_g: nx.DiGraph,
    source_pre: str,
    target_graph: nx.DiGraph,
    target_pre: str,
    initial_previous,
    visited=None,
):
    if visited is None:
        visited = set()
    
    if source_pre is None:
        print("Found None!")
    # target_endpoints = {n for n in target_graph.nodes() if target_graph.out_degree(n) == 0}

    # Use iterative approach with a stack to avoid recursion limits
    stack = [(start_node, initial_previous)]
    # Store the connections to gaps here as tupples, and only create them if you then find an actual match
    gap_stack = []
    target_nodes = frozenset(target_graph.nodes())
    source_edges_cache = {n: list(source_g.edges(n)) for n in source_g.nodes()}

    while stack:
        node, previous = stack.pop()
        
        # print(f"Process node: {source_pre}:{node}")
        
        if node in visited:
            print(f"DEBUG: Cycle detected! Node {node} in {source_pre} already visited.")
            continue
        
        visited.add(node)
        if node in target_nodes:
            if len(gap_stack) > 0:
                for gap_s, gap_t in gap_stack:
                    G.add_edge(gap_s, gap_t)
                    G.nodes[gap_t]['type'] = 'gap'
                gap_stack.clear()
            G.add_edge(f"{source_pre}:{node}", f"{target_pre}:{node}")
            # if not target_graph.edges(node):
            #     return
            previous = node
        elif previous is not None:
            gap_stack.append((f"{source_pre}:{node}", f"{target_pre}:right({previous})"))
        
        next_nodes = source_edges_cache.get(node, [])
        
        if len(next_nodes) > 1:
            print(f"WARNING: Found more than one connected node in {source_pre}: {next_nodes}")
            continue
        if len(next_nodes) == 0:
            continue
        
        next_node = next_nodes[0][1]
        
        # Check if the next node would create a cycle
        if next_node in visited:
            print(f"DEBUG: Would create cycle with {next_node} in {source_pre}, stopping this path")
            continue
        
        # Add next node to stack for processing
        stack.append((next_node, previous))
    

def write_synoptic_map_xml(G:nx.DiGraph, sigla_mapping:dict, output:str):
    output_file = output if output is not None else 'synopses/synoptic.xml'
    with codecs.open(output_file, mode='w', encoding='utf-8') as output:
        output.write('''<?xml version='1.0' encoding='UTF-8'?>
<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng" type="application/xml"
	schematypens="http://purl.oclc.org/dsdl/schematron"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
   <teiHeader>
      <fileDesc>
         <titleStmt>
            <title>Synoptische Karte</title>
         </titleStmt>
         <publicationStmt>
            <p>Publication Information</p>
         </publicationStmt>
         <sourceDesc>
            <p>Information about the source</p>
         </sourceDesc>
      </fileDesc>
      <encodingDesc>
         <listPrefixDef>
            <prefixDef ident="hc" matchPattern="(.+)" replacementPattern="https://lod.ub.uni-heidelberg.de/ontologies/heieditions/hc/current/$1"/>
        ''')
        for sig, sig_data in sigla_mapping.items():
            output.write(f'    <prefixDef matchPattern="(.+)" ident="{sig_data['synoptic_pre']}" replacementPattern="../texts/{sig}/$1" ana="hc:SynopticTextPrefixDefinition"/>\n        ')
        output.write('''</listPrefixDef>
      </encodingDesc>
   </teiHeader>''')
        output.write('<standOff>')
        for node in sorted(list(G.nodes()), key= lambda x: x.split(':')[1]):
            edges = G.out_edges(node)
            if len(edges) < 1:
                continue
            output.write(f'<linkGrp target="{node}">')
            for edge in edges:
                output.write(f'<ptr target="{edge[1]}"/>')
            output.write('</linkGrp>')
        output.write('</standOff></TEI>')
    return
    
