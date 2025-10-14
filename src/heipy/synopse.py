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


def extract_number(clique):
    first_element = clique[0] if isinstance(clique, list) else clique
    match = re.search(r'\d+', str(first_element).split(':', 1)[1])
    return float(match.group()) if match else 0

def create_synopse(
    input: list, output: str, sigla_mapping: dict = None, map_criterion="n"
):
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
    valid_map_criterion = ["n", "xml:id", "hei:altN"]
    if map_criterion not in valid_map_criterion:
        raise NameError(
            f"The parameter map_criterion must be one of {valid_map_criterion}"
        )
    all_verses = defaultdict(lambda: {"data": [], "n": None})
    starting_elements = {}
    all_witnesses = []
    all_prefixes = []
    siglum_file_map = set()

    verse_count = {}

    nones = 0
    # empty_siglum = 1
    sigla_mapping = {} if sigla_mapping is None else sigla_mapping

    for input_file in input:
        root = et.parse(input_file, parser=HeiEditionsParser())
        file_mapping = sigla_mapping.get(input_file.split("/")[-1])
        siglum = prefix = None
        if file_mapping:
            siglum = file_mapping.get("siglum")
            prefix = file_mapping.get("synoptic_pre")
        else:
            siglum_el = root.find(
                './tei:teiHeader//tei:idno[@ana="hc:EditorialSiglum"]', namespaces=ns
            )
            if siglum_el is None:
                print(
                    f"WARNING: Could could find siglum for {input_file} in the configuration file or in the file it self."
                )
                continue
                # siglum = f'pre{empty_siglum}'
                # empty_siglum += 1
            else:
                siglum = siglum_el.text
        siglum_file_map.add((siglum, input_file, prefix))
        all_witnesses.append(siglum)
        all_prefixes.append(prefix)
        verse_count[prefix] = {"total": 0, "processed": 0}
        # For fragments that start with a gap
        starting_gap = root.find(".//tei:gap[@xml:id='gap_leaf_1']", namespaces=ns)
        if starting_gap is not None:
            starting_elements[prefix] = "gap_leaf_1"

        for line in root.findall(".//tei:l", namespaces=ns):
            line_id = line.get(prefix_format("xml", "id"))
            if line_id is None:
                continue
            if prefix not in starting_elements:
                starting_elements[prefix] = line_id
            verse_key = None
            n_att = line.get("n")
            if n_att is None:
                n_att = "{:.2f}".format(nones / 100)
                nones += 1
            try:
                float(n_att.replace(",", "."))
            except ValueError:
                digits = re.search("\d+", n_att)
                if digits is None:
                    n_att = "{:.3f}".format(nones / 1000)
                    nones += 1
                else:
                    n_att = str(int(digits.group(0)) + 100000)
            n_att = n_att.replace(",", ".")
            if map_criterion == "n":
                verse_key = n_att
            elif map_criterion == "xml:id":
                verse_key = line_id
            all_verses[verse_key]["data"].append(
                {"id": line_id, "siglum": prefix, "n": n_att}
            )
            verse_count[prefix]["total"] += 1
            if all_verses[verse_key]["n"] is None:
                all_verses[verse_key]["n"] = n_att

    all_verses = OrderedDict(sorted(all_verses.items(), key=lambda x: float(x[1]["n"])))

    all_witnesses_len = len(all_witnesses)

    with importlib.resources.path(
        "heipy.templates", "synoptic_map.xml"
    ) as template_path:
        template_file = open(template_path, "rb")
        output_tree = et.parse(template_file, HeiEditionsParser())
        output_root = output_tree.getroot()

        listprefixdef = output_root.find(".//tei:listPrefixDef", namespaces=ns)
        for sig_info in sorted(siglum_file_map, key=lambda x: x[1]):
            prefix_ident = sig_info[2]
            et.SubElement(
                listprefixdef,
                prefix_format("tei", "prefixDef"),
                {
                    "matchPattern": "(.+)",
                    "ident": prefix_ident,
                    "replacementPattern": f"../{sig_info[1]}/$1",
                    "ana": "hc:SynopticTextPrefixDefinition",
                },
            )

        standoff_el = output_root.find(".//tei:standOff", namespaces=ns)
        standoff_el.clear()
        previous = {x: "" for x in all_prefixes}
        for verse_id, id_hs_dict in all_verses.items():
            id_hs_dict_data = id_hs_dict.get("data")
            for wit in id_hs_dict_data:
                sig_pre = wit.get("siglum")
                previous[sig_pre] = wit["id"]
                verse_count[sig_pre]["processed"] += 1
                if verse_count[sig_pre]["total"] == verse_count[sig_pre]["processed"]:
                    previous[sig_pre] = ""
            link_el = et.Element(prefix_format("tei", "link"))
            target = " ".join(
                [
                    f"{x['siglum']}:{x['id']}"
                    for x in sorted(id_hs_dict_data, key=lambda x: x["siglum"])
                ]
            )

            # If some testimonies do not have the verse number:
            if len(id_hs_dict_data) < all_witnesses_len:
                target += " "
                implicit_witnesses = sorted(
                    list(
                        set(all_prefixes) ^ set([x["siglum"] for x in id_hs_dict_data])
                    )
                )
                for iwi in implicit_witnesses:
                    if previous[iwi] != "":
                        target += (
                            f"{sigla_mapping.get(iwi, iwi)}:right({previous[iwi]}) "
                        )
                    # else:
                    #     if starting_elements[iwi] == 'gap_leaf_1':
                    #         target += f'{sigla_mapping.get(iwi, iwi)}:gap_leaf_1 '
                    #     else:
                    #         target += f'{sigla_mapping.get(iwi, iwi)}:left({starting_elements[iwi]}) '
                target = target.strip()

            link_el.set("n", id_hs_dict.get("n"))
            link_el.set("target", target)
            standoff_el.append(link_el)

        print(verse_count)

        list_gap = et.Element(prefix_format("tei", "list"), {"ana": "hc:GapList"})
        standoff_el.append(list_gap)

        output_tree.write(
            output, pretty_print=True, xml_declaration=True, encoding="utf-8"
        )

    return


def transform_synopse(input: str):
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
        "default": "hc:SynopticPassiveGap",
        "passiveGap": "hc:SynopticPassiveGap",
        "activeGap": "hc:SynopticActiveGap",
    }

    input_path = os.path.abspath(input)
    in_root = et.parse(input_path, parser=HeiEditionsParser())

    prefix_defs = in_root.findall(
        './/tei:prefixDef[@ana="hc:SynopticTextPrefixDefinition"]', namespaces=ns
    )
    witness_ids = [x.get("ident") for x in prefix_defs]
    witness_files = [
        os.path.basename(x.get("replacementPattern")[:-3]) for x in prefix_defs
    ]
    master_dict = {
        x: {"filename": y, "linkgrps": defaultdict(list)}
        for x, y in zip(witness_ids, witness_files)
    }

    # all_link_groups = defaultdict(list)
    for link in in_root.findall("./tei:standOff//tei:link", namespaces=ns):
        link_target = link.get("target")
        target_tokens = link_target.split()
        link_targfunc = link.get("targFunc")
        link_targfunc_tokens = list()
        if link_targfunc is None:
            link_targfunc_tokens = ["default" for x in target_tokens]
        else:
            link_targfunc_tokens = link_targfunc.split()
        target_tokens_plus = [
            (x, y) for x, y in zip(target_tokens, link_targfunc_tokens)
        ]
        combinations = list(itertools.permutations(target_tokens_plus, 2))
        for first_item, second_item in combinations:
            ms_id = first_item[0].split(":")[0]
            if ms_id not in master_dict.keys():
                continue
            master_dict[ms_id]["linkgrps"][first_item].append(second_item)
            # all_link_groups[first_item].append(second_item)
    for sigle in master_dict:
        out_root = et.Element(prefix_format("tei", "standOff"))
        out_file_name = master_dict[sigle]["filename"]
        for linkgrp_source, linkgrp_targets in master_dict[sigle]["linkgrps"].items():
            linkgrp_el = et.Element(prefix_format("tei", "linkGrp"))
            link_grp_target = linkgrp_source[0]
            linkgrp_el.set("target", link_grp_target)

            if "(" in link_grp_target:
                # Set ana attribute
                node_type = linkgrp_source[1]
                if node_type in targetfunc_dict.keys():
                    linkgrp_el.set("ana", targetfunc_dict[node_type])
                    if node_type == "default" or node_type == "passiveGap":
                        out_root.append(linkgrp_el)
                        continue
                else:
                    warnings.warn(
                        f"Could not identify node type {node_type}", HeiWarning
                    )

            for target in linkgrp_targets:
                # Create the ptr elements
                link_el = et.Element(prefix_format("tei", "ptr"))
                link_el.set("target", target[0])
                if target[1] == "default" and "(" in target[0]:
                    link_el.set("ana", targetfunc_dict["passiveGap"])
                elif target[1] != "default":
                    link_el.set("ana", targetfunc_dict[target[1]])
                linkgrp_el.append(link_el)

            out_root.append(linkgrp_el)

        tree_str = et.tostring(out_root, encoding="unicode", pretty_print=True)
        with codecs.open(
            f"synopses/linkgrp/{out_file_name}", "wb", "utf-8"
        ) as output_file:
            for line in tree_str.split("\n"):
                output_file.write(line + "\n")

    return


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
    input: list, output:str, sigla_mapping: dict = None, map_criterion="xml:id"
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
        file_mapping = sigla_mapping.get(input_file.split("/")[-1])
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
        start_node = [node for node in graph1.nodes() if graph1.in_degree(node) == 0][0]
        print(f"Starting processing nodes from {pre1} to {pre2}")
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
        # print(sorted(clique) + gap_nodes_for_clique)
        cliques.append(sorted(clique) + gap_nodes_for_clique)  
        
   

    cliques = sorted(cliques, key=extract_number)

    
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
            output.write(f'<link target="{' '.join(cliq)}"/>')
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
    
