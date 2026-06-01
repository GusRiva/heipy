from lxml import etree as et
from collections import defaultdict
from copy import deepcopy
import warnings
from ....heiwarning import HeiWarning
from ...steps import PythonStep
from ....namespaces import ns, hei_ns, xml_ns, tei_ns

hei_belongs_to_zone = hei_ns / "belongsToZone"
stopper_tags = [tei_ns / x for x in ["lb", 'pb', 'cb']]
def combine_facsimile_text(root: et.Element, parameters=None):
    sourcedoc_el = et.Element( tei_ns / 'sourceDoc')
    facsimile_el = root.find('tei:facsimile', ns)
    if facsimile_el is None:
        root.append(sourcedoc_el)
        return root
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
                    
    
    # Get all the lb in a dict based on the zones
    lb_by_belongsto = defaultdict(list)
    for lb in root.xpath("//tei:lb", namespaces=ns):
        lb_atts = lb.attrib
        if hei_belongs_to_zone in lb_atts:
            belongs_to_zone = lb_atts.get(hei_belongs_to_zone)
            lb_by_belongsto[belongs_to_zone].append(lb)
        else:
            print(f"lb with no hei_belongs_to_zone! {lb_atts}")
              
    
    for zone_id, lbs in lb_by_belongsto.items():
        zone = text_zones_by_id.get(zone_id[1:])
        if zone is None:
            zone = image_zones_by_id.get(zone_id[1:])
            if zone is None:
                warnings.warn(f"Could not find zone for {zone_id, [x.attrib for x in lbs]}. Maybe it is missing ana='hc:TextZone'?", HeiWarning)
                continue
        lbs_sorted = sorted(lbs, key = lambda x: float(x.get('n')))
        for lb in lbs_sorted:
            line = et.Element(tei_ns /'line', attrib= {xml_ns / 'space': 'preserve'})
            if lb.get('facs') is not None:
                line_zone = line_zones.get(lb.get('facs')[1:])
                if line_zone is None:
                    print(f"Could not find linezone for: {lb.get('facs')}")
                line_zone.append(line)
            else:
                zone.append(line)

            for lb_att_name, lb_att_value in lb.attrib.items():
                if lb_att_name not in ['break', hei_ns /'belongsToZone', 'facs']:
                    line.set(lb_att_name, lb_att_value)
            if lb.tail is not None and lb.tail.strip() != '':
                line.text = lb.tail
            
            process_following(lb, line)
                

    # Get all the milestones Segment Beginning
    segment_beginnings = defaultdict(list)
    for segment_beginning in root.xpath("//tei:milestone[@ana='hc:LineSegmentBeginning']", namespaces=ns):
        belongs_to = segment_beginning.get(hei_ns / "belongsToZone")
        segment_beginnings[belongs_to].append(segment_beginning)
    for zone_id, segment_list_zone in segment_beginnings.items():
        corresp_zone = text_zones_by_id.get(zone_id[1:])
        if corresp_zone is None:
            raise KeyError(f"Could not find {zone_id[1:]} in {text_zones_by_id}")
        segments_by_line = defaultdict(list)
        for segment in segment_list_zone:
            segments_by_line[segment.get(hei_ns / 'belongsToLine')].append(segment)
        for line_number, segment_list in segments_by_line.items():       
            corresp_line = corresp_zone.xpath(f'./tei:zone[@ana="hc:LineZone"][@n="{line_number}"] | ./tei:line[@n="{line_number}"]', namespaces=ns)
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

    return root


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
