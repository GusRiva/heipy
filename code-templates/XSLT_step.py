from ..steps import XsltStep

   
def get_step():
    return XsltStep(files=[], 
                    name="#{file_name}", pipe_files=True)
