from lxml import etree as et
from collections import defaultdict
from copy import deepcopy
import warnings
from ....heiwarning import HeiWarning
from ...steps import PythonStep
from ....namespaces import ns, hei_ns, xml_ns, tei_ns

hei_belongs_to_zone = hei_ns / "belongsToZone"
stopper_tags = [tei_ns / x for x in ["lb", 'pb', 'cb']]
def _line_number(line: et._Element) -> float:
    """Sort key for lines by @n; lines without a numeric @n go to the end (in document order)."""
    try:
        return float(line.get('n', ''))
    except ValueError:
        return float('inf')


def combine_facsimile_text(tree: et._ElementTree, parameters=None):
    root = tree.getroot()
    sourcedoc_el = et.Element( tei_ns / 'sourceDoc')
    facsimile_el = root.find('tei:facsimile', ns)
    if facsimile_el is None:
        root.append(sourcedoc_el)
        return tree
    text_zones_by_id = dict()
    image_zones_by_id = dict()
    gap_zones_by_id = dict()
    line_zones = dict()
    for surface in facsimile_el.iterchildren(tag= tei_ns / 'surface'):
        for fac_zone in surface.iter(tei_ns / 'zone'):
            fac_zone_ana = fac_zone.attrib["ana"]
            if 'hc:LineZone' in fac_zone_ana:
                line_zone_id = fac_zone.get(xml_ns / 'id')
                if line_zone_id is None:
                    warnings.warn(f"Missing xml:id for LineZone with attributes {fac_zone.attrib}")
                else:
                    line_zones[line_zone_id] = fac_zone
            elif any(sub in fac_zone_ana for sub in [
                'hc:TextZone', 'hc:TableZone']):
                text_zones_by_id[fac_zone.get(xml_ns / "id")] = fac_zone
            elif any(sub in fac_zone_ana for sub in [
                'hc:GraphicZone', 'hc:ImageZone']):
                image_zones_by_id[fac_zone.get(xml_ns / "id")] = fac_zone
            elif 'hc:GapZone' in fac_zone_ana:
                gap_zones_by_id[fac_zone.get(xml_ns / "id")] = fac_zone
        sourcedoc_el.append(surface)
    
    if len(gap_zones_by_id) > 0 or len(image_zones_by_id) > 0:
        milestone_elements_by_facs = dict()
        for milestone in root.xpath('.//tei:cb | //tei:milestone[contains(@ana,"hc:ZoneBeginning") or contains(@ana, "hc:ZoneShift")]', namespaces=ns):
            milestone_facs_trim = milestone.attrib['facs'][1:]
            milestone_elements_by_facs[milestone_facs_trim] = milestone
        # Process the gap zones
        if len(gap_zones_by_id) > 0:
            for gap_zone_id, gap_zone in gap_zones_by_id.items():
                gap_zone_milestone = milestone_elements_by_facs.get(gap_zone_id)
                if gap_zone_milestone is None:
                    warnings.warn(f"Could not find gapZone for {gap_zone_id}", HeiWarning)
                    continue
                for idx, gap_el in enumerate(gap_zone_milestone.itersiblings()):
                    if idx > 0:
                        break
                    gap_zone.append(gap_el)
        # Process figures
        if len(image_zones_by_id) > 0:
            for img_zone_id, img_zone in image_zones_by_id.items():
                img_zone_milestone = milestone_elements_by_facs.get(img_zone_id)
                if img_zone_milestone is None:
                    warnings.warn(f"Could not find a milestone for img_zone: {img_zone_id}. Skipping", HeiWarning)
                    continue
                for milestone_sibling in img_zone_milestone.itersiblings():
                    if milestone_sibling.tag == tei_ns / 'lb':
                        break
                    if milestone_sibling.tag == tei_ns / 'figure':
                        img_zone.append(milestone_sibling)  
                    
    
    # Build a <line> for every <lb> and gather the content following it (words, milestones,
    # marginal <add>/<del> excursions, ...) up to the next stopper.
    #
    # This is a single walk over the flattened body in document order - rather than grouping
    # <lb> by zone and processing each zone's lines independently - so that content following a
    # <milestone ana="hc:ZoneShift"> (i.e. text that resumes the SAME physical line after a
    # marginal excursion, with no <lb> of its own) can be appended back onto the line that was
    # already open for the target zone, instead of being silently dropped.
    body_children = [
        child for child in root
        if child.tag not in (tei_ns / 'teiHeader', tei_ns / 'facsimile')
    ]

    current_line_by_zone = dict()
    # lines for a <lb> without its own @facs go straight into the shared zone element and must
    # be ordered by @n rather than document order (zone_milestones.xml deliberately encodes
    # lines out of physical order), so they are collected here and appended afterwards
    pending_lines_by_zone = defaultdict(list)
    active_line = None
    # set once we stop at a pb/cb/LineSegmentBeginning, so a later ZoneBeginning/ZoneShift
    # marker (still meant for the dedicated LineSegmentBeginning pass below) can't resume a line
    suspended = False

    for node in body_children:
        tag = node.tag
        if isinstance(tag, type(et.Comment)):
            continue
        if tag == tei_ns / 'lb':
            lb = node
            lb_atts = lb.attrib
            belongs_to_zone = lb_atts.get(hei_belongs_to_zone)
            if belongs_to_zone is None:
                print(f"lb with no hei_belongs_to_zone! {lb_atts}")
                active_line = None
                suspended = False
                continue
            zone = text_zones_by_id.get(belongs_to_zone[1:])
            if zone is None:
                zone = image_zones_by_id.get(belongs_to_zone[1:])
                if zone is None:
                    warnings.warn(f"Could not find zone for {belongs_to_zone, lb_atts}. Maybe it is missing ana='hc:TextZone'?", HeiWarning)
                    active_line = None
                    suspended = False
                    continue
            line = et.Element(tei_ns / 'line', attrib={xml_ns / 'space': 'preserve'})
            line_zone = None
            lb_facs = lb.get('facs')
            if lb_facs is not None:
                line_zone = line_zones.get(lb_facs[1:])
                if line_zone is None:
                    warnings.warn(f"Could not find linezone for: {lb_facs}. The line is added to its zone instead.", HeiWarning)
            if line_zone is not None:
                line_zone_id = line_zone.get(xml_ns / 'id')
                if line_zone_id is not None:
                    line_zone.attrib.pop(xml_ns / 'id')
                    line.attrib[xml_ns / 'id'] = line_zone_id
                line_zone.append(line)
            else:
                pending_lines_by_zone[zone].append(line)

            for lb_att_name, lb_att_value in lb.attrib.items():
                if lb_att_name not in ['break', hei_belongs_to_zone, 'facs']:
                    line.set(lb_att_name, lb_att_value)
            if lb.tail is not None and lb.tail.strip() != '':
                line.text = lb.tail

            current_line_by_zone[belongs_to_zone] = line
            active_line = line
            suspended = False
        elif tag in (tei_ns / 'pb', tei_ns / 'cb'):
            active_line = None
            suspended = True
        elif tag == tei_ns / 'milestone':
            milestone_ana = node.get('ana') or ''
            if "hc:ZoneBeginning" in milestone_ana or "hc:ZoneShift" in milestone_ana:
                if not suspended:
                    active_line = current_line_by_zone.get(node.get('facs'))
            elif "hc:LineSegmentBeginning" in milestone_ana:
                if node.get(hei_ns / "belongsToLine") is None:
                    print(f"Could not find line for {node}, with attributes {node.attrib}")
                active_line = None
                suspended = True
            elif active_line is not None:
                active_line.append(node)
        elif active_line is not None:
            active_line.append(node)

    for zone, lines in pending_lines_by_zone.items():
        for line in sorted(lines, key=_line_number):
            zone.append(line)


    # Get all the milestones Segment Beginning
    segment_beginnings = defaultdict(list)
    for segment_beginning in root.iter(tei_ns / 'milestone'):
        if "hc:LineSegmentBeginning" not in (segment_beginning.get('ana') or ''):
            continue
        belongs_to = segment_beginning.get(hei_ns / "belongsToZone")
        if belongs_to is None:
            warnings.warn(f"LineSegmentBeginning without hei:belongsToZone: {segment_beginning.attrib}. Skipping", HeiWarning)
            continue
        segment_beginnings[belongs_to].append(segment_beginning)
    for zone_id, segment_list_zone in segment_beginnings.items():
        corresp_zone = text_zones_by_id.get(zone_id[1:])
        if corresp_zone is None:
            raise KeyError(f"Could not find {zone_id[1:]} in {text_zones_by_id}")
        segments_by_line = defaultdict(list)
        for segment in segment_list_zone:
            segments_by_line[segment.get(hei_ns / 'belongsToLine')].append(segment)
        for line_number, segment_list in segments_by_line.items():       
            corresp_line = corresp_zone.xpath(f'./tei:zone[@ana="hc:LineZone"][@n="{line_number}"]/tei:line | ./tei:line[@n="{line_number}"]', namespaces=ns)
            if len(corresp_line) < 1:
                warnings.warn(f"Could not find zone for line number {line_number} in zone {zone_id}. Segment line: {[(x.tag, x.attrib) for x in segment_list]}. Skipping")
                continue
            corresp_line = corresp_line[0]
            sorted_segments = sorted(segment_list, key= lambda x: int(x.get('n')))
            for segm in sorted_segments:
                if segm.tail is not None:
                    append_text(corresp_line, segm.tail)
                process_following(segm, corresp_line)
    
    
    for delenda in root[1:]:
        # if delenda.tag not in [tei_ns / x for x in ['facsimile', 'pb', 'cb', 'lb', 'milestone']]:
        #     raise ValueError(f"There is an unexpected element leftover after moving the facsimile to the sourceDoc: {delenda}, {delenda.attrib}")
        root.remove(delenda)
    root.append(sourcedoc_el)

    return tree


def append_text(element, text):
    if len(element):  # has child elements
        last = element[-1]
        last.tail = (last.tail or "") + text
    else:  # no child elements
        element.text = (element.text or "") + text


def process_following(lb, line):
    for following_el in lb.itersiblings():
        if following_el.tag in stopper_tags:
            break
        if isinstance(following_el.tag, type(et.Comment)):
            # Do not include comment nodes
            continue
        if following_el.tag == tei_ns / 'milestone':
            milestone_ana = following_el.get('ana')
            if "hc:ZoneBeginning" in milestone_ana or "hc:ZoneShift" in milestone_ana:
                break
            if "hc:LineSegmentBeginning" in milestone_ana:
                if following_el.get(hei_ns / "belongsToLine") is None:
                    print(f"Could not find line for {following_el}, with attributes {following_el.attrib}")
                break
        line.append(deepcopy(following_el))
        following_el.getparent().remove(following_el)
        


def get_step():
    return PythonStep(combine_facsimile_text, name="combine_facsimile_and_text_to_sourcedoc")
