from ..steps import Pipeline
from ..step_library import delete_comments
from ..step_library.public import pub_date


class PublicPipe(Pipeline):
    def __init__(self, parameters = None):
        pipe_steps = [
            delete_comments.get_step(),
            pub_date.get_step()
            
        ]
        description = "Public Pipeline - Standard"
        super().__init__(steps=pipe_steps, name="public_pipe", desc=description, serial=False)
