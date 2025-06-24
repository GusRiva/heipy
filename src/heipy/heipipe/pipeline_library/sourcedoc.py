from ..steps import Pipeline
from ..step_library import *


milestone_element_map = {
        'ab' : 'hc:Chunk',
        'address' : 'hc:Address',
        'addrLine' : 'hc:AddressLine',
        'back' : 'hc:ExpressionBack',
        'byline' : 'hc:Byline',
        'body' : 'hc:ExpressionBody',
        'closer' : 'hc:Closer',
        'cue' : 'hc:Cue',
        'date' : 'hc:DateIndication',
        'dateline' : 'hc:Dateline',
        'div' : 'hc:SemanticLogicalDivision',
        'docDate' : 'hc:ExpressionDate',
        'docTitle' : 'hc:ExpressionTitle',
        'epigraph' : 'hc:Epigraph',
        'front' : 'hc:ExpressionFront',
        'fw' : 'OrientationControlIndicator',
        'head' : 'hc:Heading',
        'item' : 'hc:ListItem',
        'l' : 'hc:Verse',
        'label' : 'hc:LabelLikeHeading',
        'lg' : 'hc:VerseGroup',
        'list' : 'hc:List',
        'name' : 'hc:Name',
        'note' : 'hc:Note',
        'orgName' : 'hc:OrganizationName',
        'opener' : 'hc:Opener',
        'p' : 'hc:Paragraph',    
        'persName' : 'hc:PersonName',
        'placeName' : 'hc:PlaceName',
        'postscript' : 'hc:Postscript',
        'rs' : 'hc:ReferencingString',
        'salute' : 'hc:Salutation',
        'signed' : 'hc:Signature',
        'term' : 'hc:SubjectReference',
        'text' : 'hc:TextualExpression',
        'title' : 'hc:WorkTitle', 
        'titlePage' : 'hc:TitlePage',
        'titlePart' : 'hc:ExpressionTitlePart',
        'trailer' : 'hc:Trailer'
    }

class SourceDocPipe(Pipeline):
    def __init__(self):
        # Add any steps that need specific parameters
        mark_note_as_editorial_step = mark_note_as_editorial.get_step() 
        mark_note_as_editorial_step.add_parameter(
            {'note_classes': "hc:TextCriticalNote hc:TranscriptionNote hc:TextConstitutionNote hc:Comment hc:FontesNote hc:VariantNote hc:WitnessesNote"})
        container2milestone_step = container2milestone.get_step()
        container2milestone_step.set_parameter_by_name('element_map', milestone_element_map)
        container2milestone_step.set_parameter_by_name('randomDocId', False)
        
        # SourceDoc Pipeline Standard
        pipe_steps = [
            # Index: 0
            initials.get_step(),
            transcription_note.get_step(),
            connect_lb_and_segment.get_step(),
            move_physical_beginnings.get_step(),
            whitespaces.get_step(),
            # Index: 5
            mark_note_as_editorial_step,
            number_line_segment_beginnings.get_step(),
            container2milestone_step,
            split_word_at_physical_beginnings.get_step(),
            split_everything_at_physical_beginnings.get_step(),
            # Index: 10
            remove_gap_page.get_step(),
            wrap_resolved_content.get_step(),
            prepare_figure_4_source_doc.get_step(),
            combine_facsimile_and_text_to_sourcedoc.get_step(),
            ]
        
        description = "Source Doc Pipeline"
        super().__init__(steps=pipe_steps, name="sourcedoc_pipe", desc=description, serial=False)
