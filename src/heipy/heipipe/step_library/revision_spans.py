from lxml import etree as et

from ..steps import PythonStep
from ...namespaces import prefix_format


def revision_spans_funct(root, parameters):
        # Map span types to their ana values
    span_config = {
        prefix_format('tei','delSpan'): 'hc:DeletionSpan',
        prefix_format('tei','addSpan'): 'hc:AdditionSpan'
    }
    
    # Track currently active spans: list of (anchor_id, ana_value)
    active_spans = []
    
    # Collect elements to process (to avoid modifying while iterating)
    elements_to_process = []
    
    for elem in root.iter():
        elements_to_process.append((elem, list(active_spans)))
        
        # Check if this is an anchor that closes any active span
        if elem.tag == prefix_format('tei', 'anchor'):
            xml_id = elem.get(prefix_format('xml','id'))
            if xml_id:
                # Remove any spans that target this anchor
                active_spans = [(aid, ana) for aid, ana in active_spans if aid != xml_id]
        
        # Check if this is a span element that opens a new span
        elif elem.tag in span_config:
            span_to = elem.get('spanTo')
            if span_to:
                anchor_id = span_to.lstrip('#')
                ana_value = span_config[elem.tag]
                active_spans.append((anchor_id, ana_value))
    
    # Now process elements (apply ana attributes and wrap tails)
    for elem, spans_at_elem in elements_to_process:
        # Skip span and anchor elements themselves
        if elem.tag in span_config or elem.tag == prefix_format('tei', 'anchor'):
            # But handle their tails if in a span
            if spans_at_elem and elem.tail and elem.tail.strip():
                wrap_tail(elem, spans_at_elem)
            continue
        
        # Apply ana attributes from active spans to this element
        if spans_at_elem:
            ana_values = {ana for _, ana in spans_at_elem}
            current_ana = elem.get('ana', '')
            
            if current_ana:
                existing_values = set(current_ana.split())
                all_values = existing_values | ana_values
                elem.set('ana', ' '.join(sorted(all_values)))
            else:
                elem.set('ana', ' '.join(sorted(ana_values)))
            
            # Wrap tail if it exists and has content
            if elem.tail and elem.tail.strip():
                wrap_tail(elem, spans_at_elem)
    return root

def wrap_tail(elem, active_spans):
    """
    Wrap element's tail text in a <seg> element with appropriate ana attribute.
    """
    parent = elem.getparent()
    if parent is None:
        return
    
    ana_values = {ana for _, ana in active_spans}
    
    # Create seg element for the tail
    seg = et.Element('seg')
    seg.set('ana', ' '.join(sorted(ana_values)))
    seg.text = elem.tail
    seg.tail = None  # seg will inherit any following tail
    
    # Find position of elem in parent
    elem_index = list(parent).index(elem)
    
    # Insert seg after elem
    parent.insert(elem_index + 1, seg)
    
    # Clear the original tail
    elem.tail = None

def get_step():
    return PythonStep(
        funct=revision_spans_funct, 
        name="revision_spans")
