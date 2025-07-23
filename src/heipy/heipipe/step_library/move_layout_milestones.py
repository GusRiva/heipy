from ..steps import PythonStep
from ...namespaces import ns, prefix_format

from lxml import etree as et

# Moves pb and cb to the beginning of next vers, for the synopsis


def move_milestones(root, parameters):
    new_container_xpath = '(./following::*[name() = "l" or name() = "titlePart" or name() = "p"])[1]'
    movenda = ['cb', 'pb']
    move_context = [prefix_format('tei', x) for x in ['body', 'front', 'back', 'text', 'lg', 'div', 'ab']]
    for mov in movenda:
        for mov_el in root.iter(prefix_format('tei', mov)):
            parent_tag = mov_el.getparent().tag
            if parent_tag not in move_context:
                continue
            next_container = mov_el.xpath(new_container_xpath, namespaces= ns)
            if len(next_container) < 1:
                continue
            best_fit = find_better_descendant(next_container[0]) # Sometimes it is better in a descendant of the first following
            best_fit.insert(0, mov_el)
    return root  

def find_better_descendant(container):
    if container.text.strip() != '':
        return container
    children = container.getchildren()
    if len(children) < 1:
        return container
    first_child = children[0]
    if first_child.tag in [prefix_format('tei', x) for x in ['cb', 'lb', 'milestone', 'w']]:
        # Elements where we don't go further
        return container
    return find_better_descendant(first_child)


def get_step():
    return PythonStep(
        funct=move_milestones, 
        name="move_layout_milestones")
