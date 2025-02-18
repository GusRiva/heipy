from ...namespaces import ns
from ..steps import PythonStep
from copy import deepcopy
from uuid import uuid4
from lxml import etree as et

def split_at_physical_beginnings_func(root, parameters=None):
    ''' Aim: split elements containing physical beginnings at these beginnings

    # The script works recursively - it goes on splitting elements upwards
    # in the XML tree until it reaches the TEI root element.
    # The splitted partial elements are provided with IDs and connected with each other
    # using the @next attribute.

    # CAVEAT: The script splits all elements including <text>. If this behavior isn't
    # desirable care must be taken of dealing with such elements before.
    # In a heiEDITIONS Pipeline this script should typically be placed after
    # all semantic-logical elements (including <text>) have been resolved in milestone-anchor pairs.
    # The remaining elements to be splitted by this script should be
    # only elements expected to appear as children of <line> in the sourceDoc
    # encoding.

    # Author: Jakub Šimek'''

    def check():
        # function checking whether there are any cases to be dealt with;
        # it is used to run the split() function recursively
        relevant_elements = root.xpath(
            "//*[not(self::tei:TEI or self::tei:subst)][tei:lb or tei:milestone[contains(@ana, 'hc:LineSegmentBeginning')]]",
            namespaces=ns)
        if len(relevant_elements) > 0:
            return True
        else:
            return False

    # function doing the actual splitting
    def split():
        # list of all elements which have <lb> or <milestone ana="hc:LineSegmentBeginning"> as a child
        # (except elements which contain descendant elements fulfilling the above condition - such elements
        # must be splitted first):
        relevant_elements = root.xpath(
            """//*[not(self::tei:TEI or self::tei:subst)]
                [tei:lb or tei:milestone[contains(@ana, 'hc:LineSegmentBeginning')]]
                [not(descendant::*[tei:lb or tei:milestone[contains(@ana, 'hc:LineSegmentBeginning')]])]
                """, namespaces=ns)
        # loop over elements identified as to be splitted:
        for relevant_element in relevant_elements:
            # the elements parent:
            parent = relevant_element.getparent()
            # the element name including the namespace in the Clark notation, e.g. "{http://www.tei-c.org/ns/1.0}p":
            tag = relevant_element.tag
            # just the element name without namespace, e.g. "p":
            element_name = tag.split("}")[1]
            # the first child text node in the element:
            text = relevant_element.text
            # the text node following directly after the element:
            relevant_element_tail = relevant_element.tail
            # print(tag)

            # little auxiliary list with ones and zeros:
            # 1: content child, 0: separator child (i.e. <lb>, <cb>, <pb> or <milestone ana="hc:ZoneBeginning"> etc.)
            analysis = []
            for child in relevant_element:
                # if it is one of the defined separator elements, append "0"":
                if (
                        child.tag == "{http://www.tei-c.org/ns/1.0}pb"
                        or
                        child.tag == "{http://www.tei-c.org/ns/1.0}cb"
                        or
                        (
                                child.tag == "{http://www.tei-c.org/ns/1.0}milestone"
                                and
                                (
                                        "hc:ZoneBeginning" in child.get("ana")
                                        or
                                        "hc:ZoneShift" in child.get("ana")
                                        or
                                        "hc:LineSegmentBeginning" in child.get("ana")
                                )
                        )
                        or
                        child.tag == "{http://www.tei-c.org/ns/1.0}lb"
                ):
                    analysis.append(0)
                # otherwise append "1":
                else:
                    analysis.append(1)
            # print(analysis)

            # list of all indexes of "analysis" items which are different from their previous siblings,
            # e.g. [2, 5, 6] for analysis [1, 1, 0, 0, 0, 1, 0]:
            changes = []
            for i, value in enumerate(analysis):
                # if it isn't the first item:
                if i != 0:
                    if value != analysis[i - 1]:
                        changes.append(i)
            # print(changes)

            # list of content or separator blocs,
            # e.g. [['content', 0, 1], ['separators', 2, 4], ['content', 5, 5], ['separators', 6, 6]]
            # following the schema [type, start index, end index]:
            summary = []
            # if there is no change at all (i.e. there is only a separator block and text nodes in the relevant element):
            if len(changes) == 0:
                summary_item = []
                summary_item.append("separators")
                summary_item.append(0)
                summary_item.append(len(analysis) - 1)
                summary.append(summary_item)
            else:
                for i, change in enumerate(changes):
                    # if there is only one change altogether
                    # (e.g. when there is one content bloc before one separator bloc):
                    if len(changes) == 1:
                        # information about the block BEFORE this change:
                        summary_item = []
                        if analysis[change - 1] == 1:
                            summary_item.append("content")
                        else:
                            summary_item.append("separators")
                        summary_item.append(0)
                        summary_item.append(change - 1)
                        summary.append(summary_item)
                        # information about the bloc starting with this change (i.e. the last bloc):
                        last_summary_item = []
                        if analysis[change] == 1:
                            last_summary_item.append("content")
                        else:
                            last_summary_item.append("separators")
                        last_summary_item.append(change)
                        last_summary_item.append(len(analysis) - 1)
                        summary.append(last_summary_item)
                    # if there are two changes:
                    elif len(changes) == 2:
                        # for the first change:
                        if i == 0:
                            # information about the first block (block BEFORE this change):
                            summary_item = []
                            if analysis[change - 1] == 1:
                                summary_item.append("content")
                            else:
                                summary_item.append("separators")
                            summary_item.append(0)
                            summary_item.append(change - 1)
                            summary.append(summary_item)
                        # for the second and last change:
                        else:
                            # information about the second block (block BEFORE this change):
                            summary_item = []
                            if analysis[change - 1] == 1:
                                summary_item.append("content")
                            else:
                                summary_item.append("separators")
                            index_of_last_change = changes[i - 1]
                            summary_item.append(index_of_last_change)
                            summary_item.append(change - 1)
                            summary.append(summary_item)
                            # information about the third and last block:
                            last_summary_item = []
                            if analysis[change] == 1:
                                last_summary_item.append("content")
                            else:
                                last_summary_item.append("separators")
                            last_summary_item.append(change)
                            last_summary_item.append(len(analysis) - 1)
                            summary.append(last_summary_item)
                    # for more than two changes:
                    else:
                        # for the first change:
                        if i == 0:
                            # information about the first block (block BEFORE this change):
                            summary_item = []
                            if analysis[change - 1] == 1:
                                summary_item.append("content")
                            else:
                                summary_item.append("separators")
                            summary_item.append(0)
                            summary_item.append(change - 1)
                            summary.append(summary_item)
                        # for all changes except the first and last:
                        elif i > 0 and i < len(changes) - 1:
                            # information about the block BEFORE this change:
                            summary_item = []
                            if analysis[change - 1] == 1:
                                summary_item.append("content")
                            else:
                                summary_item.append("separators")
                            index_of_last_change = changes[i - 1]
                            summary_item.append(index_of_last_change)
                            summary_item.append(change - 1)
                            summary.append(summary_item)
                        # for the last change:
                        elif i == len(changes) - 1:
                            # information about the block BEFORE this change:
                            summary_item = []
                            if analysis[change - 1] == 1:
                                summary_item.append("content")
                            else:
                                summary_item.append("separators")
                            index_of_last_change = changes[i - 1]
                            summary_item.append(index_of_last_change)
                            summary_item.append(change - 1)
                            summary.append(summary_item)
                            # information about the last block:
                            last_summary_item = []
                            if analysis[change] == 1:
                                last_summary_item.append("content")
                            else:
                                last_summary_item.append("separators")
                            last_summary_item.append(change)
                            last_summary_item.append(len(analysis) - 1)
                            summary.append(last_summary_item)

            # print(summary)

            ### constructing the sequence to replace the original element ###

            # constructing the first partial element:
            first_part = et.Element(tag, attrib=relevant_element.attrib)
            # the first child text node (if present) of the original element
            # becomes the first child text node of this first partial element:
            first_part.text = text 
            # new id for the element, if no id is set:
            if "{http://www.w3.org/XML/1998/namespace}id" not in first_part.keys():
                first_part_id = element_name + "_" + str(uuid4())
                first_part.set(
                    "{http://www.w3.org/XML/1998/namespace}id", first_part_id)
            # if the first part doesn't consist just of a text node, i.e. the first bloc has type "content":
            if len(summary) > 0 and summary[0][0] == "content":
                for child in relevant_element[summary[0][1]:summary[0][2] + 1]:
                    child_clone = deepcopy(child)
                    first_part.append(child_clone)

            # list of blocs (new elements or separator element sequences) to replace the original element:
            result_list = []
            if len(summary) > 0:
                for i, bloc in enumerate(summary):
                    # if it is a content bloc but not the one which would be the first bloc in the sequence:
                    if bloc[0] == "content" and i != 0:
                        new_part = et.Element(
                            tag, attrib=relevant_element.attrib)
                        new_part_id = element_name + \
                                      "_" + str(uuid4())
                        new_part.set(
                            "{http://www.w3.org/XML/1998/namespace}id", new_part_id)
                        for child in relevant_element[bloc[1]:bloc[2] + 1]:
                            child_clone = deepcopy(child)
                            new_part.append(child_clone)
                        # if this content block is the last block in the sequence,
                        # give the original tail to it as tail
                        if i == len(summary) - 1:
                            new_part.tail = relevant_element_tail
                        result_list.append(new_part)
                    # if it is a separator bloc:
                    elif bloc[0] == "separators":
                        # for every separator element in the bloc but the last one:
                        for child in relevant_element[bloc[1]:bloc[2]]:
                            child_clone = deepcopy(child)
                            result_list.append(child_clone)
                        # for the last separator element in the bloc
                        # extract the tail (first following text node) if present,
                        # then append the element to the result list
                        # and finally append the extracted text node to the result list:
                        last_separator = relevant_element[bloc[2]]
                        if last_separator.tail != None:
                            if last_separator.tail.strip() != "":
                                lastseptail = last_separator.tail
                                last_separator.tail = None
                                last_separator_clone = deepcopy(
                                    last_separator)
                                result_list.append(last_separator_clone)
                                result_list.append(lastseptail)
                            else:
                                last_separator_clone = deepcopy(
                                    last_separator)
                                result_list.append(last_separator_clone)
                        else:
                            last_separator_clone = deepcopy(
                                last_separator)
                            result_list.append(last_separator_clone)

            for index, result in enumerate(result_list):
                # move the previously extracted tails of separator elements
                # into the following partial elements as their respective
                # first child text node:
                if type(result) == str and index != len(result_list) - 1:
                    result_list[index + 1].text = result
                    result_list.pop(index)

            # if the sequence ends with a text node (previously extracted from
            # the tail of the last separator element), then create a last
            # partial element, set its inner text node to this text node and
            # append the original tail text to this new partial element:
            if type(result_list[-1]) == str:
                last_new_element = et.Element(
                    tag, attrib=relevant_element.attrib)
                last_new_element_id = element_name + "_" + str(uuid4())
                last_new_element.set(
                    "{http://www.w3.org/XML/1998/namespace}id", last_new_element_id)
                last_new_element.text = result_list[-1]
                last_new_element.tail = relevant_element_tail
                result_list[-1] = last_new_element

            # set @next attributes referring to the respective next following
            # partial element, for all new partial elements except the first one
            # which is stored in the first_part variable:
            for index, result in enumerate(result_list):
                next_id = None
                if result.tag == tag:
                    # search for the first following partial element:
                    for item in result_list[index + 1:]:
                        if item.tag == tag:
                            next_id = item.get(
                                "{http://www.w3.org/XML/1998/namespace}id")
                            result.set("next", "#" + next_id)
                            break
            # now look for the first partial element (not counting first_part) and set its ID
            # into the @next attribute on first_part:
            for result in result_list:
                if result.tag == tag:
                    second_id = result.get(
                        "{http://www.w3.org/XML/1998/namespace}id")
                    first_part.set("next", "#" + second_id)
                    break

            # replace the old element with the new sequence:
            parent.replace(relevant_element, first_part)
            result_list.reverse()
            for child in result_list:
                first_part.addnext(child)

    # run the split() function as many times as necessary:
    # round = 1
    while check() == True:
        # print("Runde:")
        # print(round)
        # round += 1
        split()

    return root


def get_step():
    return PythonStep(
    funct=split_at_physical_beginnings_func,
    name="split_everything_at_physical_beginnings"
)