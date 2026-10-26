from ..step_library import delete_comments, whitespaces
from ..steps import Pipeline, XsltStep


class PlainTextPipe(Pipeline):
    def __init__(self, parameters = None):
        pipe_steps = [
            delete_comments.get_step(),
            whitespaces.get_step(),
            XsltStep(files=["tei2plaintext.xsl"], name = "plaintext_main" , pipe_files=True)
        ]
        description = "Platin Text Pipeline - Standard"
        super().__init__(steps=pipe_steps, name="plaintext_pipe", desc=description, serial=False)
