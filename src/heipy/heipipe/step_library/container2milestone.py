from ..steps import XsltStep


element_map = {
    'element_map': {
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
    }

def get_step():
    step = XsltStep(
        files=["container2milestone.xsl",],
        name="container2milestone",)
    step.set_parameters([element_map])
    return step


