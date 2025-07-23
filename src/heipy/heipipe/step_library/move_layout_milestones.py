from ..steps import PythonStep
from ...namespaces import ns, prefix_format

from lxml import etree as et

# Moves pb and cb to the beginning of next vers, for the synopsis


def move_milestones(root, parameters):
    new_container_xpath = '(./following::*[name() = "l" or name() = "titlePart"])[1]'
    movenda = ['cb', 'pb']
    move_context = [prefix_format('tei', x) for x in ['body', 'front', 'back', 'text', 'lg', 'div', 'ab']]
    for mov in movenda:
        for mov_el in root.iter(prefix_format('tei', mov)):
            parent_tag = mov_el.getparent().tag
            if parent_tag not in move_context:
                continue
            next_l = mov_el.xpath(new_container_xpath, namespaces= ns)
            if len(next_l) < 1:
                continue
            next_l[0].insert(0, mov_el)
    return root

def get_step():
    return PythonStep(
        funct=move_milestones, 
        name="move_layout_milestones")
