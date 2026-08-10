from ..steps import PythonStep
from ...editions_utils import create_langusage

def langusage_funct(tree, parameters=None):
    return create_langusage(tree)
    
def get_step():
    return PythonStep(funct=langusage_funct, name="langusage")
