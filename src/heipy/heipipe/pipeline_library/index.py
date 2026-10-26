from ..step_library import delete_comments, index_essential_steps, whitespaces
from ..steps import Pipeline


class IndexPipe(Pipeline):
    def __init__(self, parameters = None):
        pipe_steps = [
            delete_comments.get_step(),
            whitespaces.get_step(),
            index_essential_steps.get_step()
        ]
        description = "Index Pipeline - Standard"
        super().__init__(steps=pipe_steps, name="index_pipe", desc=description, serial=False)
