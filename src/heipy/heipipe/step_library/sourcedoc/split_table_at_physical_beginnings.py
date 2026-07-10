from ....namespaces import ns
from ...steps import PythonStep
from copy import deepcopy
import uuid
import random

from lxml import etree as et

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"


def split_at_physical_beginnings_func(tree, parameters=None):
    ''' Aim: split tables at pb/cb elements.

    Tables can span across page/column breaks. This step splits such tables
    into separate <table> elements at these break points, so that each
    resulting table belongs to a single page/column.

    This step runs before container2milestone and split_everything_at_physical_beginnings.

    # Author: Gustavo Riva
    '''

    root = tree.getroot()
    random.seed(42)

    def find_tables_with_breaks():
        return root.xpath('.//tei:table[tei:pb or tei:cb]', namespaces=ns)

    while True:
        tables = find_tables_with_breaks()
        if not tables:
            break

        # Process only the first match, then re-check (splitting may produce new matches)
        table = tables[0]
        parent = table.getparent()
        children = list(table)

        # Find the first pb/cb child — start of the break group
        break_start = None
        for i, child in enumerate(children):
            if child.tag in (f"{{{TEI_NS}}}pb", f"{{{TEI_NS}}}cb"):
                break_start = i
                break

        if break_start is None:
            # Shouldn't happen given the XPath, but be safe
            break

        # Collect consecutive pb/cb elements starting at break_start
        break_end = break_start
        for j in range(break_start + 1, len(children)):
            if children[j].tag in (f"{{{TEI_NS}}}pb", f"{{{TEI_NS}}}cb"):
                break_end = j
            else:
                break

        # Split into three groups:
        before = children[:break_start]
        break_group = children[break_start:break_end + 1]
        after = children[break_end + 1:]

        # Create first table (with children before the break)
        first_table = et.Element(table.tag, attrib=table.attrib)
        first_table.text = table.text
        element_uuid = uuid.UUID(int=random.getrandbits(128))
        first_table_id = "table_" + str(element_uuid)
        first_table.set(f"{{{XML_NS}}}id", first_table_id)

        for child in before:
            first_table.append(deepcopy(child))

        # Create second table (with children after the break)
        second_table = et.Element(table.tag, attrib=table.attrib)
        element_uuid2 = uuid.UUID(int=random.getrandbits(128))
        second_table_id = "table_" + str(element_uuid2)
        second_table.set(f"{{{XML_NS}}}id", second_table_id)

        # The text content after the last break element (its tail) becomes
        # the text of the second table
        if break_group:
            last_break = break_group[-1]
            # Find the original element to get its tail
            original_last_break = children[break_end]
            if original_last_break.tail:
                second_table.text = original_last_break.tail

        for child in after:
            second_table.append(deepcopy(child))

        # The original table's tail goes on the second table
        second_table.tail = table.tail

        # Link first → second via @next
        first_table.set("next", "#" + second_table_id)

        # Replace original table with the sequence: first_table, break elements, second_table
        parent.replace(table, first_table)

        # Insert break elements and second table after first_table (in reverse order for addnext)
        insert_after = first_table
        for brk in break_group:
            brk_clone = deepcopy(brk)
            # Clear the tail on break clones (tail text was handled above for the last one)
            brk_clone.tail = None
            insert_after.addnext(brk_clone)
            insert_after = brk_clone

        insert_after.addnext(second_table)

    return tree


def get_step():
    return PythonStep(
    funct=split_at_physical_beginnings_func,
    name="sourcedoc.split_table_at_physical_beginnings"
)
