from ..steps import Pipeline
from ..step_library import *

class SourceDocPipe(Pipeline):
    def __init__(self):
        # Add any steps that need specific parameters
        mark_note_as_editorial_step = mark_note_as_editorial.get_step() 
        mark_note_as_editorial_step.add_parameter(
            {'note_classes': "hc:TranscriptionNote hc:TextConstitutionNote"})
        container2milestone_step = container2milestone.get_step()
        container2milestone_step.set_parameter_by_name('randomDocId', True)
        
        # SourceDoc Pipeline Standard
        pipe_steps = [
            # Index: 0
            # validation.get_step(),
            initials.get_step(),
            transcription_note.get_step(),
            connect_lb_and_segment.get_step(),
            move_physical_beginnings.get_step(),
            # Index: 5
            whitespaces.get_step(),
            mark_note_as_editorial_step,
            number_line_segment_beginnings.get_step(),
            container2milestone_step,
            split_word_at_physical_beginnings.get_step(),
            # Index: 10
            split_everything_at_physical_beginnings.get_step(),
            remove_gap_page.get_step(),
            wrap_resolved_content.get_step(),
            prepare_figure_4_source_doc.get_step(),
            combine_facsimile_and_text_to_sourcedoc.get_step(),
            # validation.get_step()
            ]
        
        description = "Source Doc Pipeline - Standard"
        super().__init__(steps=pipe_steps, name="sourcedoc_pipe", desc=description, serial=False)


