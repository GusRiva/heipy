import warnings
import os
from pathlib import Path
import re

from lxml import etree as et
from .parsers import heiparse
from .namespaces import ns, prefix_format


def merge_zones(zone_already, new_zone):
    for new_line in new_zone:
        zone_already.append(new_line)
    lines_original = list(zone_already)
    filtered_ordered_lines = sorted([x for x in lines_original.copy() if len(''.join(x.itertext()).strip()) > 0 ], 
                             key=lambda line: int(line.attrib.get('n')))
    for l in lines_original:
        zone_already.remove(l)
    for l in filtered_ordered_lines:
        zone_already.append(l)
    return


def _add_prefix_to_ids(root:et.Element, prefix:str):
    xml_id = '{http://www.w3.org/XML/1998/namespace}id'
    prefix = f'_{prefix}'
    all_ids = set()
    for elem in root.iter():
        localname = et.QName(elem).localname
        if localname in ['zone', 'surface']:
            continue
        if xml_id in elem.attrib:
            id = elem.get(xml_id)
            all_ids.add(id)
            elem.attrib[xml_id] = f'{prefix}_{id}'
        for att in ['corresp', 'target']:
            if att in elem.attrib:
                attr_value = elem.get(att)
                elem.attrib[att] = re.sub(r'#(.+)',
                                                fr'#{prefix}_\1',
                                                attr_value)
    return


def combine_sourcedoc(files:list, output_path:str | Path):
    if isinstance(output_path, str):
        output_path = Path(output_path)
    first_file_path = files[0]
    file_name = Path(first_file_path).stem
    tree = None
    try:
        tree = heiparse(first_file_path)
    except:
        warnings.warn(f"Could not find or process {first_file_path}")
        if len(files) > 1:
            combine_sourcedoc(files[1:], output_path)
        return
    root = tree.getroot()
    if len(files) < 2:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(str(output_path), encoding='utf-8', xml_declaration=True)
        return
    _add_prefix_to_ids(root, file_name)
    main_sourcedoc = root.find('.//tei:sourceDoc', ns)
    if main_sourcedoc is None:
        warnings.warn(f"Could not find sourceDoc in {first_file_path}")
        return
    for file_path in files[1:]:
        if not os.path.isfile(file_path):
            warnings.warn(f"Could not find {file_path}.")
            continue
        file_name = Path(file_path).stem
        file = heiparse(file_path)

        # Handle Ids
        _add_prefix_to_ids(file, file_name)

        sourcedoc_el = file.find('.//tei:sourceDoc', ns)
        if sourcedoc_el is None:
            warnings.warn(f"Could not find sourceDoc in {file_path}")
            return
        for surface in sourcedoc_el.findall('.//tei:surface', ns):
            main_sourcedoc.append(surface)
    all_surfaces = main_sourcedoc.findall('.//tei:surface', ns)
    # all_surfaces = sorted(all_surfaces, key=lambda elem: elem.attrib.get(prefix_format('xml', 'id')))

    new_sourcedoc = et.Element(prefix_format('tei', 'sourceDoc'))
    counter_id = ""
    last_surface = None
    for surface in all_surfaces:
        surface_id = surface.attrib.get(prefix_format('xml', 'id'))
        if surface_id != counter_id:
            counter_id = surface_id
            last_surface = surface
            new_sourcedoc.append(surface)
            continue
        # Following code is the actual combine of duplicates
        # surface is the second surface found
        for child in list(surface):
            if child.tag == prefix_format('tei', 'graphic'):
                continue
            layout_zone_id = child.attrib.get(prefix_format('xml', 'id'))
            layout_zone_old = last_surface.find(f".//tei:zone[@xml:id='{layout_zone_id}']", ns)
            if layout_zone_old is None:
                last_surface.append(child)
                continue
            merge_zones(layout_zone_old, child)
            # last_surface.append(child)

    main_sourcedoc.addnext(new_sourcedoc)
    sourcedoc_parent = main_sourcedoc.getparent()
    sourcedoc_parent.remove(main_sourcedoc)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(str(output_path), encoding='utf-8', xml_declaration=True)

