import warnings
import os

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

def combine_sourcedoc(files:list, output_path:str):
    first_file_path = files[0]
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
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        return
    main_sourcedoc = root.find('.//tei:sourceDoc', ns)
    if main_sourcedoc is None:
        warnings.warn(f"Could not find sourceDoc in {first_file_path}")
        return
    for file_path in files[1:]:
        if not os.path.isfile(file_path):
            warnings.warn(f"Could not find {file_path}.")
            continue
        file = heiparse(file_path)
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
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)




