from lxml import etree as et

from ..steps import PythonStep
from ...namespaces import tei_ns, xml_ns, hei_ns, ns


# This step expands the delSpan and addSpan and milestones in the semantic pipeline

# Map span types to their ana values
span_config = {
    tei_ns / "delSpan": {
        "ana": "hc:EditorialDeletionSpan", 
        "basic": "del"},
    tei_ns / "addSpan": {
        "ana": "hc:EditorialAdditionSpan", 
        "basic": "add"},
    "hc:EditorialAdditionSpan": {
        "ana": "hc:EditorialAdditionSpan",
        "basic": "supplied",
    },
    "hc:EditorialDeletionSpan": {
        "ana": "hc:EditorialDeletionSpan", 
        "basic": "surplus"},
}


def revision_spans_funct(root, parameters=None):
    start_element = root.find("tei:text", ns)
    if start_element is None:
        start_element = root.find("tei:sourceDoc", ns)
    if start_element is None:
        raise SyntaxError("Could not find a text or sourcedoc element.")
    spans_and_anchors = start_element.xpath(
        ".//tei:delSpan | .//tei:addSpan | .//tei:milestone[@ana='hc:EditorialAdditionSpan'] | .//tei:milestone[@ana='hc:EditorialDeletionSpan'] | .//tei:anchor",
        namespaces=ns,
    )
    for span in spans_and_anchors:
        if span.tag == tei_ns / "anchor":
            continue
        span_to = span.get("spanTo")
        if span_to is None:
            raise ValueError(f"Element {span} must have attribute spanTo.")
        # TODO: Improve this error checking also for starting with #
        try:
            span_to = span_to[1:]
        except IndexError:
            print("spanTo attribute must be ...")
        try:
            anchor = list(
                filter(lambda x: x.get(xml_ns / "id") == span_to, spans_and_anchors)
            )[0]
        except IndexError:
            print("Could not find anchor")  # TODO: Improve all these error messages
        
        this_span_config = span_config.get(span.tag) if span.tag in [tei_ns / 'delSpan', tei_ns / 'addSpan'] else span_config.get(span.attrib.get('ana'))
        this_ana = this_span_config.get('ana')
        wrap_tail(span, this_span_config, span_to)
                
        anchor_ancestors = list(anchor.iterancestors())
        elements_processed = set()
        for node in span.xpath("following::*"):
            processed_ancestor = False
            for node_ancestor in node.xpath("ancestor::*"):
                if node_ancestor in elements_processed:
                    processed_ancestor = True
                    continue
            if processed_ancestor:
                continue
            if node in anchor_ancestors:
                if node.text is not None and node.text.strip() != '':
                    new_wrap = et.Element(this_span_config.get('basic'))
                    new_wrap.attrib['ana'] = this_ana
                    new_wrap.attrib[hei_ns / 'belongsToRevision'] = f'#{span_to}'            
                    new_wrap.text = node.text
                    node.text = None
                    node.insert(0, new_wrap)            
                    elements_processed.add(new_wrap)
            elif node == anchor:
                break
            elif node.tag in [tei_ns / x for x in ['lb']] or (node.attrib.get('ana') is not None and 'hc:EditorialContent' in node.attrib.get('ana')):
                wrap_tail(node, this_span_config, span_to)
            elif node.tag == tei_ns / "line":
                continue
            else:
                previous_ana = node.attrib.get('ana')
                new_ana = this_ana
                node.attrib['ana'] = f"{previous_ana.replace(this_ana, '')} {new_ana}".strip() if previous_ana is not None else new_ana
                elements_processed.add(node)
                wrap_tail(node, this_span_config, span_to)
                    
    return root


def wrap_tail(element:et.Element, config:dict, span_to:str):
    tail_el = et.Element(config.get('basic')) if element.tail is not None and element.tail.strip() != '' else None
    if tail_el is not None:
        tail_el.text = element.tail
        element.tail = None
        tail_el.attrib['ana'] = config.get('ana')
        tail_el.attrib[hei_ns / 'belongsToRevision'] = f'#{span_to}'
        element.addnext(tail_el)
    return element


def get_step():
    return PythonStep(funct=revision_spans_funct, name="revision_spans")
