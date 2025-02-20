from lxml import etree

from ..steps import PythonStep
from ...namespaces import ns

def revision_span_func(root, parameters=None):
    # Aim: process all nodes between
    # addSpan|delSpan|milestone[@ana="hc:EditorialAdditionSpan"]|milestone[@ana="hc:EditorialDeletionSpan"]
    # and the corresponding anchor and annotate them with information about the revision
    # using a class at @ana and a pointer to the anchor via @hei:revisionRef

    # Author: Jakub Šimek

    # list of all starting points belonging to revision spans:
    beginnings = root.xpath(
        "//tei:delSpan|//tei:addSpan|//tei:milestone[contains(@ana, 'hc:EditorialDeletionSpan') or contains(@ana, 'hc:EditorialAdditionSpan')]", namespaces=ns)

    # list of all descendant elements inside of text in document order:
    text_descendants = [descendant for descendant in root.xpath(
        "//tei:text", namespaces=ns)[0].iterdescendants()]


    def markAsSpanPart(spanTo, current, revisionClass):
        """Function for processing elements identified as relevant parts of a revision span.
        Text nodes are not processed directly by this function but are prepared by the main code first
        and then sent to this function as elements.
        Parameters:
        spantTo: value of the @spanTo attribute on the span beginning, including "#" (i.e. reference to the end-point anchor) (as string)
        current: the element to be processed (as element)
        revisionClass: one of the four types of revision spans, e.g. hc:AdditionSpan (as string)
        """
        # empty elements and editorial content are excluded from the processing
        if "".join(current.itertext()) != "" and (current.get("ana") is None or not "hc:EditorialContent" in current.get("ana")):
            # prepare and set @hei:revisionRef as a connection between each revision span part and the revision as such;
            # connections to multiple revisions are possible, therefore a possibly already existing @hei:revisionRef
            # is analyzed first and joined with the current revision in the attribute:
            existingRevisionReferences = current.get(
                "{https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS}revisionRef")
            if existingRevisionReferences is not None:
                existingRevisionReferencesList = existingRevisionReferences.split()
                existingRevisionReferencesList.append(spanTo)
                newRevisionReferencesList = list(
                    set(existingRevisionReferencesList))
                newRevisionReferences = " ".join(newRevisionReferencesList)
            else:
                newRevisionReferences = spanTo
            current.set(
                "{https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS}revisionRef", newRevisionReferences)
            # prepare and set @ana with the current revision span class, respecting possibly existing
            # classes on the element; if the current element belongs to multiple revision spans of the same class,
            # the class is stated only once:
            existingClasses = current.get("ana")
            if existingClasses is not None:
                existingClassesList = existingClasses.split()
                existingClassesList.append(revisionClass)
                newClassesList = list(set(existingClassesList))
                newClasses = " ".join(newClassesList)
            else:
                newClasses = revisionClass
            current.set("ana", newClasses)


    # loop for every revision marked up as a span between two points:
    for beginning in beginnings:
        # assign a revision class according to the start-point element used:
        if beginning.tag == "{http://www.tei-c.org/ns/1.0}delSpan":
            revisionClass = "hc:DeletionSpan"
        elif beginning.tag == "{http://www.tei-c.org/ns/1.0}addSpan":
            revisionClass = "hc:AdditionSpan"
        elif beginning.tag == "{http://www.tei-c.org/ns/1.0}milestone" and "hc:EditorialDeletionSpan" in beginning.get('ana'):
            revisionClass = "hc:EditorialDeletionSpan"
        elif beginning.tag == "{http://www.tei-c.org/ns/1.0}milestone" and "hc:EditorialAdditionSpan" in beginning.get('ana'):
            revisionClass = "hc:EditorialAdditionSpan"
        # variables for the reference to the anchor, the anchor ID and the anchor element:
        spanTo = beginning.get('spanTo')
        anchorID = spanTo.split("#")[1]
        anchor = root.xpath(
            "//tei:anchor[@xml:id='" + anchorID + "']", namespaces=ns)[0]
        # processing a possible text node following directly the start-point:
        if not (beginning.tail is None or beginning.tail.isspace() or beginning.tail == ''):
            beginning_tail = beginning.tail
            beginning.tail = ''
            seg = etree.Element("{http://www.tei-c.org/ns/1.0}seg")
            seg.text = beginning_tail
            markAsSpanPart(spanTo, seg, revisionClass)
            beginning.addnext(seg)
        # determine the indexes of the start-point and the end-point in the list of all descendants of tei:text:
        for index, text_descendant in enumerate(text_descendants):
            if text_descendant is beginning:
                beginning_index = index
            if text_descendant is anchor:
                anchor_index = index
        # a list of all elements between the start-point and the end-point in document order:
        span_elements = text_descendants[beginning_index + 1: anchor_index]
        # separate lists of elements containing the anchor or not:
        elements_containing_anchor = []
        elements_not_containing_anchor = []
        for span_element in span_elements:
            span_element_descendants = [
                descendant for descendant in span_element.iterdescendants()]
            if anchor in span_element_descendants:
                elements_containing_anchor.append(span_element)
            else:
                elements_not_containing_anchor.append(span_element)
        # process span elements not containing the anchor:
        for span_element in elements_not_containing_anchor:
            # check if an ancestor of this element is also relevant for processing:
            span_element_ancestors = [
                ancestor for ancestor in span_element.iterancestors()]
            relevant_ancestors = set(span_element_ancestors).intersection(
                set(elements_not_containing_anchor))
            # process only elements which do not have an ancestor also relevant for processing:
            if len(relevant_ancestors) == 0:
                markAsSpanPart(spanTo, span_element, revisionClass)
                # if the element has a non-whitespace text tail, process the text tail:
                if not (span_element.tail is None or span_element.tail.isspace() or span_element.tail == ''):
                    span_element_tail = span_element.tail
                    span_element.tail = ''
                    seg = etree.Element("{http://www.tei-c.org/ns/1.0}seg")
                    seg.text = span_element_tail
                    markAsSpanPart(spanTo, seg, revisionClass)
                    span_element.addnext(seg)
        # process text nodes at the beginning of elements containing the anchor:
        for element_containing_anchor in elements_containing_anchor:
            if not (element_containing_anchor.text is None or element_containing_anchor.text.isspace() or element_containing_anchor.text == ''):
                text_at_the_beginning = element_containing_anchor.text
                element_containing_anchor.text = ''
                seg = etree.Element("{http://www.tei-c.org/ns/1.0}seg")
                seg.text = text_at_the_beginning
                markAsSpanPart(spanTo, seg, revisionClass)
                element_containing_anchor.insert(0, seg)
    
    return root


def get_step():
    return PythonStep(funct=revision_span_func, name="revision_spans_for_reading")
