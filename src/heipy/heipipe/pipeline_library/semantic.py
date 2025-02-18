from ..steps import Pipeline
from ..step_library import *

class SemanticPipe(Pipeline):
    def __init__(self):
        # Add any steps that need specific parameters
                
        # SourceDoc Pipeline Standard
        pipe_steps = [
            # Index: 0
            validation.get_step(),
            header_listchange.get_step(),
            ptr2ref.get_step()


            # Index: 5
        




            # Index: 10
        




            # Index: 15
            ]
        
        description = "Semantic Pipeline - Standard"
        super().__init__(steps=pipe_steps, name="sourcedoc_pipe", desc=description, serial=False)


