from ....namespaces import ns
from ...steps import PythonStep

def prepare_figure_4_source_doc(tree, parameters=None):
    root = tree.getroot()
    # aim:
    # prepare figure and table elements for transformation from "text" to "sourceDoc"
    # mainly by extracting content not belonging to a corresponding figure or table zone
    # outside (i.e. after) the figure or table element

    # logic:
    # 1. identify sequences of ZoneBeginning or ZoneShift milestone with following nodes until
    # one of these appears: graphic, ZoneBeginning or ZoneShift milestone, end of the figure element
    # 2. move these sequences outside (after) the figure element
    
    # Update GFR: Move also the label with lb elements outside the figure

    figures_list = root.xpath(".//tei:figure", namespaces=ns)

    for figure in figures_list:
        # list for figure children to be extracted:
        extract = []
        # iterate over the children of figure:
        i = 0
        while i < len(figure):
            # if the child element has @ana (this two-step check is necessary due to lxml limitations):
            if figure[i].get("ana") != None:
                # if @ana contains "hc:ZoneBeginning" or "hc:ZoneShift":
                if "hc:ZoneBeginning" in figure[i].get("ana") or "hc:ZoneShift" in figure[i].get("ana"):
                    # start index of the sequence to be extracted:
                    start = int(i)
                    # end index of the sequence to be extracted:
                    end = int(i)
                    # shifting one child forward:
                    i += 1
                    # checking if the following child is to be included in the sequence as well:
                    while i < len(figure):
                        if figure[i].tag == "{http://www.tei-c.org/ns/1.0}graphic":
                            i += 1
                            break
                        elif figure[i].get("ana") != None:
                            if "hc:ZoneBeginning" in figure[i].get("ana") or "hc:ZoneShift" in figure[i].get("ana"):
                                i += 1
                                continue
                            else:
                                end = i
                                i += 1
                        else:
                            end = i
                            i += 1
                    if start != end:
                        extract.append(figure[start: end + 1])
                    else:
                        extract.append(figure[start])
                else:
                    i += 1
            
            else:
                i += 1
        # flattening the list "extract" (because it can contains lists itself):
        flattenedExtract = []
        for item in extract:
            if type(item) is list:
                for subitem in item:
                    flattenedExtract.append(subitem)
            else:
                flattenedExtract.append(item)
        # reverting the order of the element list
        flattenedExtract.reverse()
        # adding the extracted content after "figure" in reverse order
        for extracted in flattenedExtract:
            figure.addnext(extracted)

    return tree

def get_step():
    return PythonStep(funct=prepare_figure_4_source_doc, name="Prepare Figure for SourceDoc")
