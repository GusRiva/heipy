from ..steps import PythonStep
from ...namespaces import ns

def move_physical_beginnings(root, parameters=None):
    ''''''
    pb_list = root.xpath("""//tei:pb
    [not(preceding-sibling::* or preceding-sibling::text()[normalize-space() != ''])]""", namespaces=ns)

    for pb in pb_list:
        _move_before(pb, pb.getparent(), root)

    cb_list = root.xpath("""//tei:cb
        [not(preceding-sibling::* or preceding-sibling::text()[normalize-space() != ''])]""", namespaces=ns)

    for cb in cb_list:
        _move_before(cb, cb.getparent(), root)

    zone_beginning_list = root.xpath("""//tei:milestone
        [contains(@ana, 'hc:ZoneBeginning')]
        [not(preceding-sibling::* or preceding-sibling::text()[normalize-space() != ''])]""", namespaces=ns)

    for milestone in zone_beginning_list:
        _move_before(milestone, milestone.getparent(), root)

    zone_shift_list = root.xpath("""//tei:milestone
        [contains(@ana, 'hc:ZoneShift')]
        [not(preceding-sibling::* or preceding-sibling::text()[normalize-space() != ''])]""", namespaces=ns)

    for milestone in zone_shift_list:
        _move_before(milestone, milestone.getparent(), root)

    lb_list = root.xpath("""//tei:lb
        [not(preceding-sibling::* or preceding-sibling::text()[normalize-space() != ''])]""", namespaces=ns)

    for lb in lb_list:
        _move_before(lb, lb.getparent(), root)

    line_segment_list = root.xpath("""//tei:milestone
        [contains(@ana, 'hc:LineSegmentBeginning')]
        [not(preceding-sibling::* or preceding-sibling::text()[normalize-space() != ''])]""", namespaces=ns)

    for milestone in line_segment_list:
        _move_before(milestone, milestone.getparent(), root)

    return root

def _move_before(movendum, target, root):
    # $movendum: the element to be moved
    # $target: the element before which $movendum is to be moved, here the $movendum's parent
    # $root: document root
    tail_text = movendum.tail
    if tail_text is not None:
        if tail_text.strip() != "":
            if target.text is not None:
                # Vom Gustavo am 11.01.2023 geändert. Original: target.text = target.tail + tail_text
                target.text = target.text + tail_text
            else:
                target.text = tail_text
            movendum.tail = ""
    # check whether the target has a preceding sibling,
    #   i.e. whether it is not itself again only the first child in a bigger container
    #   (because if it is, $movendum needs to be moved before the bigger container and not $target):
    if target.getprevious() is not None:
        # this moves $movendum before the target:
        target.addprevious(movendum)
    else:
        parent = target.getparent()
        # (the recursive moving process has to stop before the document root:)
        if parent is not root:
            _move_before(movendum, parent, root)

def get_step():
    return PythonStep(funct=move_physical_beginnings, name="move_physical_beginnings")
