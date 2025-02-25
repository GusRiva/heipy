from ..steps import XsltStep


def get_step():
    return XsltStep(files=[
    "text_transcriptionNote.xsl",
    ], name="transcription_note", pipe_files=True)
