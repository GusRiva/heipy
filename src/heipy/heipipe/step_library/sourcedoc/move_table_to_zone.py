from ....namespaces import ns, tei_ns, xml_ns
from ...steps import PythonStep


def move_table_to_zone_func(root, parameters=None):
    """Move each <table> into its corresponding hc:TableZone in the facsimile.

    After split_table_at_physical_beginnings, each <table> belongs to a single
    zone. This step finds the TableZones in the facsimile and moves tables from
    the text body into them, so that combine_facsimile_and_text_to_sourcedoc
    does not leave TableZones empty.
    """
    facsimile_el = root.find('tei:facsimile', ns)
    if facsimile_el is None:
        return root

    # Collect TableZone elements keyed by xml:id
    table_zones_by_id = {}
    for zone in facsimile_el.iter(tei_ns / 'zone'):
        ana = zone.get('ana', '')
        if 'hc:TableZone' in ana:
            zone_id = zone.get(xml_ns / 'id')
            if zone_id is not None:
                table_zones_by_id[zone_id] = zone

    if not table_zones_by_id:
        return root

    # Stopper tags: stop scanning siblings when hitting these
    stopper_tags = {tei_ns / 'pb', tei_ns / 'cb'}

    # Find cb elements whose @facs points to a TableZone
    for cb in root.iter(tei_ns / 'cb'):
        facs = cb.get('facs')
        if facs is None:
            continue
        facs_id = facs.lstrip('#')
        zone = table_zones_by_id.get(facs_id)
        if zone is None:
            continue

        # Move tables that follow this cb until we hit a stopper
        for sibling in list(cb.itersiblings()):
            if sibling.tag in stopper_tags:
                break
            if sibling.tag == tei_ns / 'milestone':
                ana = sibling.get('ana', '')
                if 'hc:ZoneBeginning' in ana or 'hc:ZoneShift' in ana:
                    break
            if sibling.tag == tei_ns / 'table':
                zone.append(sibling)

    return root


def get_step():
    return PythonStep(
        funct=move_table_to_zone_func,
        name="sourcedoc.move_table_to_zone"
    )
