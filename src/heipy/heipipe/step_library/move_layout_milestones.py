from lxml import etree as et

from ..steps import PythonStep
from ...namespaces import ns, prefix_format


# Moves pb and cb to the beginning of next vers, for the synopsis


def move_milestones(tree, parameters=None):
    """
    Moves page break (pb) and column break (cb) elements to the beginning of the next
    verse (l), titlePart, or paragraph (p) element.

    This is necessary for proper synopsis formatting where layout milestones should
    appear at the start of textual content rather than between structural elements.
    """
    root = tree.getroot()
    # Parent contexts where we should move milestones (pre-compute as set for O(1) lookup)
    valid_parent_contexts = set([prefix_format('tei', x) for x in ['body', 'front', 'back', 'text', 'lg', 'div', 'ab']])

    # Target containers (pre-compute as set for O(1) lookup)
    target_tags = set([prefix_format('tei', x) for x in ['l', 'titlePart', 'p']])

    # Collect all elements to move first, to avoid modifying tree while iterating
    elements_to_move = []

    # Elements to move (page breaks and column breaks)
    for milestone_type in ['cb', 'pb']:
        milestone_tag = prefix_format('tei', milestone_type)

        for milestone_el in root.iter(milestone_tag):
            parent_tag = milestone_el.getparent().tag
            if parent_tag not in valid_parent_contexts:
                continue

            # Find next target container by walking forward through siblings and their descendants
            next_container = find_next_target(milestone_el, target_tags)
            if next_container is None:
                continue

            # Find the best descendant element to place the milestone
            target = find_better_descendant(next_container)
            elements_to_move.append((milestone_el, target))

    # Now perform all moves
    for milestone_el, target in elements_to_move:
        target.insert(0, milestone_el)

    return tree


def find_next_target(element, target_tags):
    """
    Find the next element matching target_tags by iterating forward through the tree.
    This replaces the XPath which was causing performance issues.

    Args:
        element: Starting element
        target_tags: Set of tag names to search for

    Returns:
        The next matching element, or None if not found
    """
    # Start searching from the element after this one
    for next_el in element.itersiblings(preceding=False):
        # Check if this element matches
        if next_el.tag in target_tags:
            return next_el
        # Check descendants
        for desc in next_el.iter():
            if desc.tag in target_tags:
                return desc

    # If not found in siblings, walk up and search from parent's siblings
    parent = element.getparent()
    if parent is not None:
        return find_next_target(parent, target_tags)

    return None

def find_better_descendant(container, max_depth=10):
    """
    Recursively find the best descendant element to place a milestone.

    The "best" descendant is the deepest element that doesn't yet have text content
    and isn't a milestone/word element itself. This ensures milestones are placed
    as close as possible to actual text content.

    Args:
        container: The initial container element to search
        max_depth: Maximum recursion depth to prevent infinite loops

    Returns:
        The best element to insert the milestone into
    """
    if max_depth <= 0:
        return container

    # If container has text content, stop here
    if container.text is not None and container.text.strip() != '':
        return container

    # Get element children (not text nodes)
    children = [x for x in container.iterchildren(et.Element)]
    if len(children) < 1:
        return container

    first_child = children[0]

    # Stop at certain element types where we shouldn't go deeper
    stop_at_tags = [prefix_format('tei', x) for x in ['cb', 'lb', 'milestone', 'w']]
    if first_child.tag in stop_at_tags:
        return container

    # Recurse into first child
    return find_better_descendant(first_child, max_depth - 1)


def get_step():
    return PythonStep(
        funct=move_milestones, 
        name="move_layout_milestones")
