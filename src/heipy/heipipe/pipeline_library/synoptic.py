from ..steps import Pipeline, DeleteStep
from ..step_library import revision_spans, mark_note_as_editorial, container2milestone, move_note, \
    move_layout_milestones, ptr2ref, filter_visual_information, add_id_2_note, whitespaces, \
    number_line_segment_beginnings, suppress_first_cb, delete_comments
from ..step_library.synoptic import change_prefixdef_ref



milestone_element_map = {
        'ab' : 'hc:Chunk',
        'back' : 'hc:ExpressionBack',
        'body' : 'hc:ExpressionBody',
        'div' : 'hc:SemanticLogicalDivision',
        'docDate' : 'hc:ExpressionDate',
        'docTitle' : 'hc:ExpressionTitle',
        'front' : 'hc:ExpressionFront',
        'list' : 'hc:List',
        'trailer' : 'hc:Trailer',
    }

class SynopticPipe(Pipeline):
    def __init__(self):
        # Add any steps that need specific parameters
        mark_note_as_editorial_step = mark_note_as_editorial.get_step()
        mark_note_as_editorial_step.set_parameter('note_classes',
                                                          "hc:TextCriticalNote hc:EditorialNote hc:TranscriptionNote hc:TextConstitutionNote hc:Comment hc:FontesNote hc:VariantNote hc:WitnessesNote")
        # List of elements to unwrap
        # to_unwrap = [{'element_name': x} for x in ['fw']]

        container2milestone_step = container2milestone.get_step()
        container2milestone_step.set_parameter('element_map', milestone_element_map)

        move_note_step = move_note.get_step()
        move_note_step.set_parameter('position', 'last')
        
        # SourceDoc Pipeline Standard
        pipe_steps = [
            # Index: 0
            delete_comments.get_step(),
            DeleteStep(elements=['tei:zone[@ana="hc:LineZone"]'], name="delete_facs"),
            DeleteStep(elements=['tei:metamark',
                                 'tei:fw',
                                 "tei:label[contains(@ana, 'hc:DivisionMark')]",
                                 "hei:cue"], name="delete_irrelevant_elements_for_semantic"),
            # UnwrapStep(elements=to_unwrap, name="Unwrap high level semantic elements", serial=True),
            ptr2ref.get_step(),
            
            filter_visual_information.get_step(),
            move_layout_milestones.get_step(),
            mark_note_as_editorial_step,
            add_id_2_note.get_step(),
            move_note_step,
            revision_spans.get_step(),
            container2milestone_step,
            whitespaces.get_step(),
            number_line_segment_beginnings.get_step(),
            # AddAttribute(match='tei:text', att_name=prefix_format('xml','space'), att_val='preserve'),

            # For first gap we add xml:id gap_leaf_1 if missing
            # AddAttribute()

            suppress_first_cb.get_step()
            
            ]
        
        description = "Synoptic Pipeline - Standard"
        super().__init__(steps=pipe_steps, name="synoptic_pipe", desc=description, serial=False)
        

class SynopticMapPipe(Pipeline):
    def __init__(self):
        pipe_steps= [
            change_prefixdef_ref.get_step()
        ]
        description = "Pipeline for the synoptic map"
        super().__init__(steps=pipe_steps, name="synoptic_map_pipe", desc=description, serial=False)

