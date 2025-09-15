import os
from copy import deepcopy
from ...namespaces import ns, prefix_format
from ..steps import PythonStep
from ...colors import RED, RESET


def move_note_func(root, parameters):
    # aim:
    #   Process "note" alements carrying the target attribute in this way:
    #   - move the "note" (wherever it is) directly after the element stated as target
    #   - the target can be indicated either by pointing to a @xml:id or to a range
    #       expressed by the first and last @xml:id of the range
    #   - if several targets are indicated in @target, the "note" element
    #       has to be multiplied and placed (with a unique @xml:id) after each of the
    #       targeted elements  
    # parameters: 
    #       position: 'after' or 'last'

    # a list of all notes carrying a @target:
    notes_list = root.xpath(".//tei:note[contains(@ana, 'hc:EditorialContent')][@target]", namespaces=ns)

    # a dictionary of xml:ids to make lookup faster
    id_index = {el.attrib[prefix_format('xml','id')]: el for el in root.iter() if prefix_format('xml','id') in el.attrib}

    # iterate over the list of "note" elements:
    for i, note in enumerate(notes_list):
        target_raw = note.get('target')
        note_id = note.get('{http://www.w3.org/XML/1998/namespace}id', f"note_auto_{i}")
        target_splitted = target_raw.split()
        # list for just the IDs of the targets (for ranges, this is the last element of the range):
        target_ids = []
        for t in target_splitted:
            if t.startswith('#range'):
                # string after the comma and without the last parenthesis:
                last_id = t.split(',')[1][0:-1]
                target_ids.append(last_id)
            else:
                # string after the hash:
                target_ids.append(t[1:])
        
        # We move or create and move the notes:
        for j, target_id_enum in enumerate(target_ids):
            # If this is not the first target, we create a copy to move
            if j != 0:
                note = deepcopy(note)
                new_id = note_id + "_" + str(j)
                note.set(prefix_format('xml','id'), new_id)
            new_target = target_splitted[j]
            note.set('target', new_target)
            # Find the target
            target = id_index.get(target_id_enum)             
            if target is None:
                print(f"{RED}Could not find target for note: {target_id_enum}{RESET}")
                with open('tmp/errors.log', 'a') as error_file:
                    error_file.write(f"\nCould not find target for note: {target_id_enum}")
                continue
            
            note_tail = note.tail if note.tail is not None else ""
            target_tail = target.tail if target.tail is not None else ""

            # Here we manage what happens in the place that the note is leaving.
            # If the note does not have a preceding sibling, i.e. its tail mus be attached to the text of its parent:
            if note.getprevious() is None:
                if note.getparent() is not None:
                    # if the parent does not have a text:
                    if note.getparent().text is None:
                        note.getparent().text = note_tail
                    # if the parent does have a text:
                    else:
                        note.getparent().text += note_tail
            # if the note does have a preceding sibling:
            else:
                # if the preceding sibling does not have a tail:
                if note.getprevious().tail is None:
                    note.getprevious().tail = note_tail
                # if the preceding sibling does have a tail:
                else:
                    note.getprevious().tail += note_tail
            
            position = parameters[0].get('position')
            match position:
                case 'after':
                    # move the target's tail to become the note's tail:
                    note.tail = target_tail
                    target.tail = None
                    # move the note after the target:
                    target_parent = target.getparent()
                    target_index = target_parent.index(target)
                    target_parent.insert(target_index + 1, note)
                case 'last':
                    note.tail = None
                    target.insert(len(target), note)


    return root

def get_step():
    return PythonStep(
        funct=move_note_func,
        name="move_note"
    )
