from ..steps import Pipeline, AddAttribute, DeleteStep
from ..step_library import *
from ...namespaces import prefix_format

class SemanticPipe(Pipeline):
    def __init__(self, parameters = None):
        # Add any steps that need specific parameters
        mark_note_as_editorial_step = mark_note_as_editorial.get_step()
        mark_note_as_editorial_step.set_parameter_by_name('note_classes',
                                                          "hc:TextCriticalNote hc:TranscriptionNote hc:TextConstitutionNote hc:Comment hc:FontesNote hc:VariantNote hc:WitnessesNote")
        move_note_step = move_note.get_step()
        move_note_step.set_parameter_by_name('position', 'after')
        
        # SourceDoc Pipeline Standard
        pipe_steps = [
            # Index: 0
            # validation.get_step(),
            DeleteStep(elements=['tei:zone[@ana="hc:LineZone"]'], name="delete_facs"),
            # header_listchange.get_step(),
            ptr2ref.get_step(),
            DeleteStep(elements=['tei:metamark',
                                 'tei:fw',
                                 "tei:label[contains(@ana, 'hc:DivisionMark')]"], name="delete_irrelevant_elements_for_semantic"),
            filter_visual_information.get_step(),
            mark_note_as_editorial_step,
            add_id_2_note.get_step(),
            move_note_step,
            supply_id_divisions.get_step(),
            revision_spans.get_step(),
            whitespaces.get_step(),
            number_line_segment_beginnings.get_step(),
            AddAttribute(match='tei:text', att_name=prefix_format('xml','space'), att_val='preserve'),
            final_cleanup.get_step(),
            # validation.get_step(),
            ]
        
        if isinstance(parameters, dict):
            if parameters.get('inject_structure'):
                inject_structure_step = inject_structure.get_step()
                inject_structure3_step = inject_structure3.get_step()
                pipe_steps.insert(7, inject_structure3_step)
                pipe_steps.insert(7, inject_structure_step)
            
            
        
        description = "Semantic Pipeline - Standard"
        super().__init__(steps=pipe_steps, name="semantic_pipe", desc=description, serial=False)
        

