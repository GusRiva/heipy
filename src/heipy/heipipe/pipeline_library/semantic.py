from ..steps import Pipeline, AddAttribute, DeleteStep
from ..step_library import mark_note_as_editorial, move_note, filter_visual_information,ptr2ref, add_id_2_note, supply_id_divisions, whitespaces,number_line_segment_beginnings,final_cleanup, inject_structure, transpose
from ..step_library import revision_spans
from ...namespaces import prefix_format


class SemanticPipe(Pipeline):
    def __init__(self, parameters = None, serial=False, preserve_space=True):
        # Add any steps that need specific parameters
        mark_note_as_editorial_step = mark_note_as_editorial.get_step()
        mark_note_as_editorial_step.set_parameter('note_classes',
                                                          "hc:TextCriticalNote hc:TranscriptionNote hc:TextConstitutionNote hc:Comment hc:FontesNote hc:VariantNote hc:WitnessesNote hc:EditorialNote")
        move_note_step = move_note.get_step()
        move_note_step.set_parameter('position', 'after')
        # SourceDoc Pipeline Standard
        pipe_steps = [
            # Index: 0
            # validation.get_step(),
            DeleteStep(elements=['tei:zone[@ana="hc:LineZone"]'], name="delete_facs"),
            DeleteStep(elements=['tei:metamark',
                                 'tei:fw',
                                 "tei:label[contains(@ana, 'hc:DivisionMark')]",
                                 "hei:cue"], name="delete_irrelevant_elements_for_semantic"),
            filter_visual_information.get_step(),
            transpose.get_step(),
            ptr2ref.get_step(),
            revision_spans.get_step(),
            mark_note_as_editorial_step,
            add_id_2_note.get_step(),
            move_note_step,
            supply_id_divisions.get_step(),
            whitespaces.get_step(),
            number_line_segment_beginnings.get_step(),
            final_cleanup.get_step(),
            # validation.get_step(),
            ]
        
        if preserve_space:
            pipe_steps.insert(-2,
                        AddAttribute(match='tei:text', 
                                     att_name=prefix_format('xml','space'), 
                                     att_val='preserve'))
        
        if isinstance(parameters, dict):
            if parameters.get('inject_structure'):
                inject_structure_step = inject_structure.get_step()
                pipe_steps.insert(3, inject_structure_step)
            
            
        
        description = "Semantic Pipeline - Standard"
        super().__init__(steps=pipe_steps, name="semantic_pipe", desc=description, serial=serial)
        

