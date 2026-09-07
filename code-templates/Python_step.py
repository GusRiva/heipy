from ..steps import PythonStep


def #{function_name}_func(tree, parameters=None):
    return tree
    
def get_step():
    return PythonStep(funct=#{function_name}_func, name="#{function_name}")
