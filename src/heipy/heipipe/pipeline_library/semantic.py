from ...namespaces import prefix_format
from ..step_library import (
    add_id_2_note,
    break_no,
    delete_comments,
    filter_visual_information,
    mark_note_as_editorial,
    move_note,
    number_line_segment_beginnings,
    ptr2ref,
    reg_levels,
    resolve_index_references,
    revision_spans,
    whitespaces,
)
from ..step_library.semantic import (
    final_cleanup,
    generate_pb_ids,
    inject_structure,
    supply_id_divisions,
    transpose,
)
from ..steps import AddAttribute, DeleteStep, Pipeline


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
            delete_comments.get_step(),
            DeleteStep(elements=['tei:zone[@ana="hc:LineZone"]'], name="delete_facs"),
            DeleteStep(elements=['tei:metamark',
                                 'tei:fw',
                                 "tei:label[contains(@ana, 'hc:DivisionMark')]",
                                 "hei:cue",
                                 "tei:ab[contains(@ana, 'hc:Shelfmark')]",
                                 "tei:ab[contains(@ana, 'hc:OwnershipInscription')]"
                                 ], 
                       name="delete_irrelevant_elements_for_semantic"),
            filter_visual_information.get_step(),
            break_no.get_step(),
            reg_levels.get_step(),
            transpose.get_step(),
            ptr2ref.get_step(),
            revision_spans.get_step(),
            mark_note_as_editorial_step,
            add_id_2_note.get_step(),
            move_note_step,
            supply_id_divisions.get_step(),
            whitespaces.get_step(),
            number_line_segment_beginnings.get_step(),
            resolve_index_references.get_step(),
            generate_pb_ids.get_step(),
            final_cleanup.get_step(),
            # validation.get_step(),
            
            ]
        
        if preserve_space:
            pipe_steps.insert(-2,
                        AddAttribute(match='tei:text', 
                                     att_name=prefix_format('xml','space'), 
                                     att_val='preserve'))
        
        if isinstance(parameters, dict) and parameters.get('inject_structure'):
            inject_structure_step = inject_structure.get_step()
            pipe_steps.insert(3, inject_structure_step)
        
        description = "Semantic Pipeline - Standard"
        super().__init__(steps=pipe_steps, name="semantic_pipe", desc=description, serial=serial)
        

