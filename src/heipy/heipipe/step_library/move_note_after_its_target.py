from copy import deepcopy
from uuid import uuid4
from ...namespaces import ns, prefix_format
from ..steps import PythonStep




def move_note_after_its_target_func(root, parameters=None):
    # aim:
    #   Process "note" alements carrying the target attribute in this way:
    #   - move the "note" (wherever it is) directly after the element stated as target
    #   - the target can be indicated either by pointing to a @xml:id or to a range
    #       expressed by the first and last @xml:id of the range
    #   - if several targets are indicated in @target, the "note" element
    #       has to be multiplied and placed (with a unique @xml:id) after each of the
    #       targeted elements

    # CAVEAT:
    #   The script expects that all "note" elements already carry an @xml:id.
    #   This must be handled beforehand using text_addXmlidToNote.xsl
    #
    #   The script can process range() pointer in @target of "note" elements
    #   but it expects only one range in a range(), i.e. just two IDs separated by comma.
    #   It then puts the "note" behind the last element of the range.

    # author: Jakub Šimek

    # a list of all notes carrying a @target:
    notes_list = root.xpath("//tei:note[contains(@ana, 'hc:EditorialContent')][@target]", namespaces=ns)

    # a dictionary of xml:ids to make lookup faster
    id_index = {el.attrib[prefix_format('xml','id')]: el for el in root.iter() if prefix_format('xml','id') in el.attrib}
    # function for moving a note from its original context to become the first following sibling of its target:
    def move_note(note, target):
        # in case the note does not have a tail, the following variable is initialized as empty string:
        note_tail = ""
        if note.tail != None:
            note_tail = note.tail
        target_tail = target.tail
        # if the note does not have a preceding sibling, i.e. its tail mus be attached to the text of its parent:
        if note.getprevious() == None:
            # if the parent does not have a text:
            if note.getparent().text == None:
                note.getparent().text = note_tail
            # if the parent does have a text:
            else:
                note.getparent().text = note.getparent().text + note_tail
        # if the note does have a preceding sibling:
        else:
            # if the preceding sibling does not have a tail:
            if note.getprevious().tail == None:
                note.getprevious().tail = note_tail
            # if the preceding sibling does have a tail:
            else:
                note.getprevious().tail = note.getprevious().tail + note_tail
        # move the target's tail to become the note's tail:
        note.tail = target_tail
        target.tail = None
        # move the note after the target:
        target_parent = target.getparent()
        target_index = target_parent.index(target)
        target_parent.insert(target_index + 1, note)

    # function for placing a virtually multiplied note after its target 
    # (multiplying notes is done when a note has several targets):
    def paste_duplicated_note(note, target):
        # move the target's tail to become the note's tail:
        target_tail = target.tail
        note.tail = target_tail
        target.tail = None
        # place the note after the target:
        target_parent = target.getparent()
        target_index = target_parent.index(target)
        target_parent.insert(target_index + 1, note)

    # iterate over the list of "note" elements:
    for note in notes_list:
        note_id = note.get('{http://www.w3.org/XML/1998/namespace}id')
        target_raw = note.get('target')
        target_splitted = target_raw.split()
        # list for just the IDs of the targets (for ranges, this is the last element of the range):
        target_ids = []
        for i in target_splitted:
            if i.startswith('#range'):
                # string after the comma and without the last parenthesis:
                last_id = i.split(',')[1][0:-1]
                target_ids.append(last_id)
            else:
                # string after the hash:
                target_ids.append(i[1:])
        # if there is just one target, then the note can stay the same and is just moved:
        if len(target_ids) == 1:
            target = id_index.get(target_ids[0])
            move_note(note, target)
        # if there are several targets, then the note needs to be multiplied (with different IDs):
        else:
            # make a copy of the note (needed for duplicates):
            note_copy = deepcopy(note)
            # iterate over the enumerated target IDs:
            for target_id_enum in enumerate(target_ids):
                # for the first target the note is moved from its original position: 
                if target_id_enum[0] == 0:
                    # the new @target must contain just this one specific target (which is the first one):
                    new_target = target_splitted[0]
                    note.set('target', new_target)
                    # find the target:
                    target = id_index.get(target_id_enum[1])
                    move_note(note, target)
                else:
                    # for all other targets copies of the note with different IDs must be made:
                    specific_note_copy = deepcopy(note_copy)
                    # the new_id adds an underscore and the current number of the target_id to the original ID:
                    new_id = note_id + "_" + str(target_id_enum[0])
                    specific_note_copy.set('{http://www.w3.org/XML/1998/namespace}id', new_id)
                    # the new @target must contain just this one specific target:
                    new_target = target_splitted[target_id_enum[0]]
                    specific_note_copy.set('target', new_target)
                    # find the target:
                    target = id_index.get(target_id_enum[1])
                    paste_duplicated_note(specific_note_copy, target)

    return root

def get_step():
    return PythonStep(
        funct=move_note_after_its_target_func,
        name="move_note_after_its_target"
    )
