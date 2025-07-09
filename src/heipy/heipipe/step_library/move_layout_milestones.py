from ..steps import PythonStep
from ...namespaces import ns, prefix_format

from lxml import etree as et

# Moves pb and cb to the beginning of next vers, for the synopsis


def move_milestones(root, parameters):
    new_container_xpath = '(./following::*[name() = "l" or name() = "titlePart"])[1]'
    movenda = ['pb', 'cb']
    for mov in movenda:
        for mov_el in root.iter(prefix_format('tei', mov)):
            next_l = mov_el.xpath(new_container_xpath, namespaces= ns)
            if len(next_l) < 1:
                continue
            next_l[0].append(mov_el)
    return root

def get_step():
    return PythonStep(
        funct=move_milestones, 
        name="move_layout_milestones")
