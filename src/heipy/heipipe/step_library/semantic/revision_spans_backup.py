from lxml import etree as et

from ...steps import PythonStep
from ....namespaces import tei_ns, xml_ns, hei_ns


# This step expands the delSpan and addSpan and milestones in the semantic pipeline

# Map span types to their ana values
span_config = {
    tei_ns / "delSpan": {
        'ana': 'hc:DeletionSpan',
        'basic': 'del'
        },
    tei_ns / "addSpan": {
        'ana':'hc:AdditionSpan',
        'basic': 'add'},
    'hc:EditorialAdditionSpan': {
        'ana':'hc:EditorialAdditionSpan',
        'basic': 'supplied'},
    'hc:EditorialDeletionSpan': {
        'ana':'hc:EditorialDeletionSpan',
        'basic': 'surplus'}
    }

def revision_spans_funct(root, parameters=None):
    span_to = False
    write_atts = False
    sibling = None
    span_element = None
    span_type = None
    walk_context = et.iterwalk(root, events=("start", "end"))
    for event, element in walk_context:
        if element.tag in [tei_ns / 'teiHeader', tei_ns / 'facsimile']:
            walk_context.skip_subtree()
        elif element.tag == tei_ns / 'lb':
            continue

        if element.tag in [tei_ns / x for x in ["delSpan", "addSpan", "milestone"]] and event == 'start':
            span_tag = element.tag
            span_type = element.tag
            if element.tag == tei_ns /"milestone":
                if element.get('ana') not in ["hc:EditorialAdditionSpan", "hc:EditorialDeletionSpan"]:
                    continue
                span_type = element.get('ana')
            span_element = element
            span_to = element.get('spanTo')
            if not span_to:
                raise ValueError("Missing spanTo attribute in delSpan or add Span")
            if not span_to.startswith("#"):
                raise ValueError(f"spanTo attribute in {span_tag} must start with #")
            try:
                span_to = span_to[1:]
            except IndexError:
                raise ValueError(f"Invalid spanTo attribute in {span_tag}!")
            wrap_tail(element, span_type, span_to)
            write_atts = True
            sibling = element
                
        elif element.tag == tei_ns / "anchor" and element.get(xml_ns / 'id') == span_to:
            anchor = element
            ancestors = element.xpath("ancestor::*")
            _make_inner_add_or_del(sibling, 
                                   ancestors, 
                                   span_to, 
                                   anchor=anchor,
                                   span_type=span_type)
            span_to = False
            write_atts = False
            sibling = None
            span_element = None
            span_type = None

        elif span_to:
            if write_atts and event == 'start':
                write_atts = False
                if sibling is not None and sibling != span_element:
                    new_ana = span_config.get(span_type).get('ana')
                    previous_ana = sibling.attrib.get('ana')
                    if previous_ana and new_ana not in previous_ana:
                        new_ana += f' {previous_ana}'
                    sibling.attrib['ana'] = new_ana
                    new_belongs_to = f"#{span_to}"
                    previous_belongs_to = sibling.attrib.get(hei_ns /'belongsToRevision')
                    if previous_belongs_to and new_belongs_to not in previous_belongs_to:
                        new_belongs_to += f' {previous_belongs_to}'
                    sibling.attrib[hei_ns /'belongsToRevision'] = new_belongs_to
                sibling = element
            if sibling == element and event == 'end':
                wrap_tail(sibling,span_type, span_to)
                write_atts = True    
        
        
    return root


def wrap_tail(element, span_type, span_to):
    tail_del = et.Element(span_config.get(span_type).get('basic'))
    tail = element.tail
    if tail is not None:
        if tail.strip() != '':
            tail_del.attrib['ana'] = span_config.get(span_type).get('ana')
            tail_del.attrib[hei_ns / 'belongsToRevision'] = f'#{span_to}'
            tail_del.text = tail
            element.tail = ''
            element.addnext(tail_del)
    return tail_del


def _make_inner_add_or_del(element:et.Element, 
                    stop_list:list, 
                    span_to:str, 
                    anchor:et.Element,
                    span_type:str
                    ):
    new_del = et.Element(span_config.get(span_type).get('basic'), 
                {'ana': span_config.get(span_type).get('ana'),
                 hei_ns / 'belongsToRevision': f'#{span_to}'})
    if element.text:
        new_del.text = element.text
        element.text = ''
    
    for child in element:
        if child == anchor:
            break
        if child not in stop_list:
            new_del.append(child)
        else:
            _make_inner_add_or_del(child, stop_list, span_to, anchor, span_type)
    
    element.insert(0, new_del)
    return
    

def get_step():
    return PythonStep(
        funct=revision_spans_funct,
        name="semantic.revision_spans")
