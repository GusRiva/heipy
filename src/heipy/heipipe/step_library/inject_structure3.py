from lxml import etree as et

from ..steps import PythonStep
from ...namespaces import ns
from ...colors import RED, RESET

def inject_structure3_func(root, parameters=None):
    milestones_list = root.xpath("//tei:milestone[@type = 'structure_div' or @type = 'structure_front' or @type = 'structure_body' or @type = 'structure_back']", namespaces=ns)

    for milestone in milestones_list:
        # create a new container element (depending on the milestone's type):
        new_div = None
        match milestone.get("type"):
            case "structure_div":
                new_div = et.Element("{http://www.tei-c.org/ns/1.0}div")
            case "structure_front":
                new_div = et.Element("{http://www.tei-c.org/ns/1.0}front")
            case "structure_body":
                new_div = et.Element("{http://www.tei-c.org/ns/1.0}body")
            case "structure_back":
                new_div = et.Element("{http://www.tei-c.org/ns/1.0}back")
        if new_div is None:
            raise ValueError(f"{RED}Incorrect value for structure: {milestone.get('type')}{RESET}")
        # copy the attributes from milestone (except @type):
        for attribute in milestone.attrib:
            if attribute != "type":
                new_div.set(attribute, milestone.attrib[attribute])
        # get the xml:id of the milestone:
        xmlid = milestone.get("{http://www.w3.org/XML/1998/namespace}id")
        if xmlid is None:
            raise KeyError(f"{RED}Could not find milestone {milestone.attrib}. Please check the 'structure_' file.{RESET}")
        # get the anchor (marking the end of the children of the future <div>):
        anchor_xpath = "//tei:anchor[@spanFrom = '#" + xmlid + "']"
        anchor = root.xpath(anchor_xpath, namespaces=ns)
        if len(anchor) < 1:
            raise IndexError(f"{RED}Could not find anchor: {anchor_xpath}. Check the 'structure_' file.{RESET}")
        anchor = anchor[0]
        # get the index of the milestone in its parent element:
        milestone_index = milestone.getparent().index(milestone)
        # get the index of the anchor in its parent element:
        anchor_index = anchor.getparent().index(anchor)
        # get the right "slice" of elements between the milestone and the anchor
        # and put it into the new container:
        for new_child in milestone.getparent()[milestone_index + 1:anchor_index]:
            new_div.append(new_child)
        # insert the new container after the milestone:
        milestone.addnext(new_div)
        # remove the milestone and the anchor:
        milestone.getparent().remove(milestone)
        anchor.getparent().remove(anchor)

    return root

def get_step():
    return PythonStep(funct=inject_structure3_func, name="inject_structure3")
