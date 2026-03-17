import re
import warnings
from lxml import etree as et
from ..steps import PythonStep
from ...namespaces import ns, xml_ns
from ...heiwarning import HeiWarning

def transpose_funct(root, parameters=None):
    found_transpose = False
    id_dict = {}
    range_regex =  r"range\(#(\w+),\s*#(\w+)\)"
    for transpose in root.findall( ".//tei:transpose", namespaces=ns):
        
        if not found_transpose:
            found_transpose = True
            id_dict = create_id_dict(root)
            
        for ptr in transpose:
            ptr_target = ptr.get("target")
            if ptr_target.startswith("#"):
                # print(f"#: {ptr_target}")
                continue
            elif ptr_target.startswith("range"):
                # print(f"Range: {ptr_target}")
                ma = re.match(range_regex, ptr_target)
                rt_1, rt_2 = ma.group(1), ma.group(2)
                wrapper_id = wrap_range(id_dict, rt_1, rt_2)
            else:
               warnings.warn(f"Invalid target in ptr: {ptr_target}", HeiWarning) 
    
    for editorial_transposition in root.xpath(".//tei:link[contains(@ana, 'hc:EditorialTransposition')]", namespaces=ns):
        if not found_transpose:
            found_transpose = True
            id_dict = create_id_dict(root)
        full_target = editorial_transposition.get('target')
        new_target = []
        for target in re.split(r'(?<=[^,(])\s+', full_target):
            if target.startswith("range"):
                ma = re.match(range_regex, target)
                rt_1, rt_2 = ma.group(1), ma.group(2)
                wrapper_id = wrap_range(id_dict, rt_1, rt_2)
                target = '#' + wrapper_id
            new_target.append(target)
        editorial_transposition.attrib['target'] = " ".join(new_target)
            
        
        
    
    return root

def create_id_dict(root):
    id_dict = {}
    for elem in root.iter():
        elem_id = elem.get(xml_ns / "id")
        if elem_id is not None:
            id_dict[elem_id] = elem
    return id_dict

def wrap_range(id_dict, first_id, second_id):
    elem1 = id_dict[first_id]
    elem2 = id_dict[second_id]
    
    parent1 = elem1.getparent()
    parent2 = elem2.getparent()
    
    if parent1 is not parent2:
        raise ValueError(f"Elements {first_id} and {second_id} included as range of a ptr in a transpose are not siblings!")
    
    parent = parent1
    children = list(parent)
    
    idx1 = children.index(elem1)
    idx2 = children.index(elem2)
    
    if idx1 > idx2:
        idx1, idx2 = idx2, idx1
    
    # Determine wrapper element based on tag names
    tags = {et.QName(elem1).localname, et.QName(elem2).localname}
    if tags & {"div"}:
        wrapper_tag = "div"
    elif tags & {"p", "l", "lg", "ab"}:
        wrapper_tag = "ab"
    else:
        wrapper_tag = "seg"
    
    wrapper = et.Element(wrapper_tag)
    wrapper_id = f"range__{first_id}__{second_id}"
    wrapper.attrib[xml_ns / "id"] = wrapper_id
    parent.insert(idx1, wrapper)
    
    for i in range(idx2 - idx1 + 1):
        wrapper.append(parent[idx1 + 1])
    
    return wrapper_id
    


def get_step():
    return PythonStep(transpose_funct, name="transpose")
