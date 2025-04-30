# steps.py
import importlib
import os
import time
from lxml import etree as et
import sys
import io
import codecs
from abc import abstractmethod
from icecream import ic
import warnings

from ..namespaces import ns
from ..parsers import apply_xslt, heiparse, HeiEditionsParser, validate_xml_with_heieditions_schema
from ..colors import *
from ..heiwarning import HeiWarning


class BaseStep:
    """ Base class for all steps """
    def __init__(self, name=None, desc=None, serial=False, parameters=None):
        self.name = name if name is not None else "__None__"
        self.desc = desc
        self.serial = serial
        self.parameters = parameters
        self.index = -1 # When outside of pipeline

    def add_parameter(self, param:dict):
        self.parameters.append(param)
        return 

    def get_desc(self):
        return self.desc

    def get_index(self):
        return self.index

    def get_name(self):
        return self.name

    def get_parameter_by_name(self, name:str):
        if self.parameters is None:
            return None
        for param in self.parameters:
            key = [*param][0]
            if key == name:
                return param[key]
        return None

    def get_parameters(self):
        """
        Get the parameters for the current instance.
        Args:
            parameters (dict): A dictionary containing the parameters to be set.
        """
        return self.parameters

    def get_serial(self):
        return self.serial

    def set_index(self, idx):
        self.index = idx

    def set_parameters(self, parameters:list):
        """
        Set the parameters for the current instance.
        Parameters should be a list, one item per parameter. 
        The parameters are dictionaries. The key is the name of the parameter, the value the content. Can be of the type number, string, dictionary or boolean.
        Args:
            parameters (dict): A dictionary containing the parameters to be set.
        """
        self.parameters = parameters

    def set_parameter_by_name(self, name:str, content):
        parameter_names = [(list(d.keys())[0], idx) for idx, d in enumerate(self.parameters)]
        for param in parameter_names:
            if param[0] != name:
                continue
            self.parameters[param[1]] = {name: content}
            return
        self.parameters.append({name: content})
        return       

    def set_serial(self, value: bool):
        self.serial = value

    def _serialize(self, xml_string, file_name=None):
        if not self.serial:
            pass
        if file_name is None:
            file_name = f"tmp/{self.index}_{self.name}.xml"
        if not file_name.endswith('.xml'):
            file_name += '.xml'
        output_file_serial = codecs.open(f"{file_name}", "w", "utf-8")
        output_file_serial.write(xml_string)
        output_file_serial.close()

    @abstractmethod
    def execute(self, input_string):
        pass


class Pipeline(BaseStep):
    """
    A class to represent a sequence of processing steps in a pipeline.

    Attributes:
    -----------
    steps : list
        A list of steps to be executed in the pipeline. These can be an instance of any of the subclasses of BaseStep (XsltStep, PythonStep, etc.), including another instance of Pipeline.
    name : str
        The name of the pipeline.
    desc : str
        A description of the pipeline.
    serial : bool
        A flag indicating whether after finishing processing, a serialized version of the result should be written. It output file is written in a /tmp directory and has the format {index number of the step}_{step name}.

    Methods:
    --------
    __str__():
        Returns a string representation of the pipeline.
    add_step(step, at_index=None,  after_step:str=None, before_step:str=None, serial=False, parameters=None):
        Adds a step to the pipeline either at the specified index or in relation to another step. If no index nor after_step not before_step is given, the step will be add as the last in the pipeline. You can add the parameters if this is an XSLT transformation or any other transformation that would accept them.
    execute(input):
        Executes the pipeline on the given input.
    get_steps():
        Returns the list of steps in the pipeline.
    get_step_by_name(name:str):
        Returns the step by its name.
    remove_step(step_name=None, step_index=None):
        Removes a step from the pipeline by its name or index.
    set_pipestep_parameter(step, parameter_name, parameter_value):
        Sets a parameter for a specific pipeline step by name or index.
    """
    def __init__(self, steps=None, name=None, desc=None, serial=False):
        super().__init__(name, desc, serial)
        if steps is None:
            steps = []
        elif not isinstance(steps, list):
            raise TypeError('steps must be a list')
        self.steps = steps
        if len(self.steps) > 0:
            for idx, step in enumerate(self.steps):
                step.set_index(idx)
        return

    def __str__(self):
        return f"Pipeline »{self.name}« containing {len(self.steps)} steps."

    def add_step(self, step, at_index:int=None, after_step:str=None, before_step:str=None, serial=False, parameters=None):
        """
        Adds a step to the pipeline. 

        Parameters:
        step (Step): The step to be added to the pipeline. The step can be an instance of any of the subclasses of BaseStep.
        at_index (int, optional): The index at which to insert the step. If None, the step is appended to the end.
        after_step (str, optional): The step after which the new step should be added.
        before_step (str, optional): The step before which the new step should be added.
        serial (bool, optional): If True, the output while be written to file.
        parameters (list, optional): A list of parameters to be set for the step (for example, as XSLT parameters). Defaults to an empty list if None.

        Returns:
        None

        Raises:
        Warning: If at_index is not a positive integer or is out of bounds, a warning is issued and the step is not added.
        """
        if serial:
            step.set_serial(serial)
        if parameters is None:
            parameters = step.get_parameters() or []
        step.set_parameters(parameters)


        pos_params = (at_index, after_step, before_step)
        if pos_params.count(None) < 2:
            raise SyntaxError(f'You can only use one positional paramter for your new step. You are currently using: at_index={at_index}, after_step={after_step}, before_step={before_step}.')      

        if step.get_name() in [x.get_name() for x in self.get_steps()]:
            raise NameError(f"Step with the name »{step.get_name()}« already exists in the Pipeline.")
        
        if isinstance(step, Pipeline):
            print(step) # Here should add handle when a pipeline is added as a step to another pipeline

        def add_step_intern(idx):
            step.set_index(idx) 
            if step.get_name() == '__None__':
                step.name = '__None__' + str(idx)
            self.steps.insert(idx, step)

        if at_index is not None:
            if at_index > len(self.steps) - 1:
                warnings.warn(f"Step  »{step.name}«: was added with an index higher than possible: {at_index}. This pipeline has now {len(self.steps)}. Step will not be added.")
                return
            if at_index < 0:
                warnings.warn(f"Step  »{step.name}«: Index must be a positive integer (0 or higher). Index now is {at_index}. Step will not be added.")
                return
            add_step_intern(at_index)
        
        elif after_step or before_step is not None:
            try:
                idx_mod = 1 if after_step is not None else 0
                new_step_idx = [x.get_name() for x in self.get_steps()].index(after_step or before_step)
                step_index = new_step_idx + idx_mod
                add_step_intern(step_index)
            except ValueError:
                warnings.warn(f"Could not find step »{after_step}« in pipeline {self.name}, in relation to which you want to add step {step}. Step will not be added.")
        
        else:
            step_index = len(self.steps)
            add_step_intern(step_index)

    def execute(self, input, xinclude=False):
        """
        Executes the pipeline on the given input file.

        Args:
            input (str): The XML document in its string representation.
            xinclude (bool): Does the starting file contain xinclude elements that need to be resolved at the start of the pipeline? Defaults to False.

        Returns:
            str: The processed string after all pipeline steps have been executed.
        """
        print(f"Starting Pipeline {self.name} for {input[:60]}")
        if not os.path.isfile(input):
            warnings.warn(f'Could not find file {input}, skipping...', HeiWarning)
            return None
        if xinclude == False:
            input_file = codecs.open(input, "r", "utf-8")
            input_string = input_file.read()
        else:
            input_string = heiparse(input, output_format='str')
        for step in self.steps:
            input_string = step.execute(input_string)
        return input_string

    def get_steps(self):
        return self.steps
    
    def get_step_by_name(self, name:str):
        for step in self.get_steps():
            step_name = step.get_name()
            if step_name != name:
                continue
            return step
        return

    def remove_step(self, step_name:str=None, step_index:int=None):
        if (step_name, step_index).count(None) != 1:
            raise SyntaxError(f"The function remove_step() must contain only one of the parameters step_name or step_index. Currently step_name={step_name} , step_index={step_index} .")
        if step_index is not None:
            return self.steps.pop(step_index)

        if step_name is not None:
            for i, step in enumerate(self.steps):
                if step.get_name() == step_name:
                    return self.steps.pop(i)
            warnings.warn(f"Could not find step with name »{step_name}« to remove in pipeline.")
        return

    def set_pipestep_parameter(self, step: str | int, parameter_name: str, parameter_value):
        """
        Sets a parameter for a specific pipeline step.

        This method allows you to set a parameter for a pipeline step by either 
        providing the step's name (as a string) or its index (as an integer).

        Args:
            step (str or int): The name or index of the pipeline step.
                - If a string, it should match the name of an existing step.
                - If an integer, it should be a valid index within the pipeline steps.
            parameter_name (str): The name of the parameter to set.
            parameter_value: The value to assign to the parameter.

        Raises:
            ValueError: If the step name provided as a string does not match any existing step.
            IndexError: If the step index provided as an integer is out of range.
            TypeError: If the `step` argument is neither a string nor an integer.
        """
        if isinstance(step,str):
            step_obj = self.get_step_by_name(step)
            if step_obj is None:
                raise ValueError(f'Could not find parameter with the name {step}')
        elif isinstance(step, int):
            if len(self.get_steps()) <= step:
                raise IndexError(f'The pipeline: {self}, contains only {len(self.get_steps())} steps and you are trying to access step at index {step}.')
            step_obj = self.get_steps()[step]
        else:
            raise TypeError(f'{step} should be string of integer')
        step_obj.set_parameter_by_name(parameter_name, parameter_value)
        return


class XsltStep(BaseStep):
    """
    A step in a pipeline that applies one or more XSLT transformations to an input string.

    Attributes:
        files (list): A list of XSLT file paths to be applied in sequence. Defaults to an empty list.
        parameters (list): A list of parameters to be passed to the XSLT transformations. Defaults to an empty list.
        name (str): The name of the step. Defaults to None.
        desc (str): A description of the step. Defaults to None.
        serial (bool): Whether to serialize the output after execution. Defaults to False.
        pipe_files (bool): Whether to load XSLT files from a package resource. Defaults to False.

    Methods:
        __str__():
            Returns a string representation of the step, including the number of transformations and parameters.
        get_files() -> list:
            Returns the list of XSLT file paths.
        execute(input_string: str) -> str:
            Applies the XSLT transformations to the input string in sequence and returns the transformed string.
            If `pipe_files` is True, the XSLT files are loaded from package resources.
            If `serial` is True, the output is serialized after each transformation.
    """
    def __init__(self, files=None, parameters=None, name=None, desc=None, serial=False, pipe_files=False):
        super().__init__(name, desc, serial)
        self.files = [] if files is None else files
        self.pipe_files = pipe_files
        self.parameters = [] if parameters is None else parameters

    def __str__(self):
        return f"XSLStep »{self.name}« containing {len(self.files)} transformations {self.files} and {len(self.parameters)} parameters {self.parameters if len(self.parameters) > 0 else ''}."

    def get_files(self) -> list:
        return self.files

    def execute(self, input_string) -> str:
        for file in self.files:
            start_time = time.time()  # Record start time
            true_xslt_file = None
            if self.pipe_files == True:
                with importlib.resources.path('heipy.heipipe.xslt', file) as xslt_file_path:
                    true_xslt_file = str(xslt_file_path)
            else:
                true_xslt_file = str(file)
            if true_xslt_file is None:
                warnings.warn(f"{RED}Could not find the xslt file: {file}")
                return input_string
            input_string = apply_xslt(input_string, true_xslt_file, self.get_parameters())
            end_time = time.time()  # Record end time
            elapsed_time = end_time - start_time  # Calculate elapsed time
            # Make this printing conditional on a parameter
            # print(f"{GREEN}Time for {file}: {elapsed_time:.4f} seconds{RESET}")
            if self.serial:
                super()._serialize(input_string)
        return input_string


class AddAttribute(BaseStep):
    """
    A step that adds a specified attribute with a given value to all matching XML elements.

    Attributes:
        match (str): The XPath expression to match elements in the XML.
        att_name (str): The name of the attribute to add to the matched elements.
        att_val (str): The value of the attribute to add to the matched elements.
        name (str, optional): The name of the step. Defaults to None.
        desc (str, optional): A description of the step. Defaults to None.
        serial (bool, optional): Whether to serialize the result. Defaults to None.

    Returns:
        str: The modified XML string with the added attributes.
    """
    def __init__(self, match:str, att_name:str, att_val:str, name=None, desc=None, serial=None):
        super().__init__(name, desc, serial)
        self.match = match
        self.att_name = att_name
        self.att_val = att_val

    def __str__(self):
        return f"Add Attribute Step »{self.name}«. match: {self.match}, att_name: {self.att_name}, att_val: {self.att_val}"

    def execute(self, input_string):
        input_string_enc = input_string.encode('utf-8')
        root = et.fromstring(input_string_enc, parser=HeiEditionsParser())
        matches = root.xpath(f"{self.match}", namespaces=ns)
        for match in matches:
            match.set(self.att_name, self.att_val)
        result = et.tostring(root, encoding='unicode')
        if self.serial:
            super()._serialize(result)
        return result


class DeleteStep(BaseStep):
    """
    A step in a pipeline that deletes specified XML elements from an input string.

    Attributes:
        elements (list): A list of XPath expressions corresponding to the elements to be deleted.
        name (str, optional): The name of the step. Defaults to None.
        desc (str, optional): A description of the step. Defaults to None.
        serial (bool, optional): A flag indicating whether to serialize the result. Defaults to None.
    """
    def __init__(self, elements:list, name=None, desc=None, serial=None):
        super().__init__(name, desc, serial)
        self.elements = elements

    def __str__(self):
        return f"DeleteStep »{self.name}«. Deletes: {self.elements}"

    def execute(self, input_string):
        if len(self.elements) < 1:
            return input_string
        input_stream = io.BytesIO(input_string.encode('utf-8'))
        tree = et.parse(input_stream, parser=HeiEditionsParser())
        root = tree.getroot()
        for elem_name in self.elements:
            if elem_name[:1] != '/':
                elem_name = '//' + elem_name
            xpath_ex = f".{elem_name}"
            for elem in root.xpath(xpath_ex, namespaces=ns):
                elem.getparent().remove(elem)
        result = et.tostring(tree, encoding='utf-8').decode('utf-8')
        if self.serial:
            super()._serialize(result)
        return result


class PythonStep(BaseStep):
    """
    A class representing a processing step that executes a Python function on an XML input.

    Attributes:
        funct (callable): The Python function to be executed. It should accept an XML root element
            as its first argument and optionally a parameters dictionary as its second argument.
        parameters (dict, optional): A dictionary of parameters to be passed to the function.
            Defaults to None.
        name (str, optional): The name of the step. Defaults to None.
        desc (str, optional): A description of the step. Defaults to None.
        serial (bool, optional): A flag indicating whether the result should be serialized.
            Defaults to False.

    Methods:
        __str__():
            Returns a string representation of the PythonStep instance.

        execute(input_string):
            Executes the Python function on the given XML input string.

            Args:
                input_string (str): The XML input string to be processed.

            Returns:
                str: The resulting XML string after processing.
    """
    def __init__(self, funct, parameters=None, name=None, desc=None, serial=False):
        super().__init__(name, desc, serial)
        self.funct = funct

    def __str__(self):
        return f"Python step »{self.name}«, using: {self.funct}"

    def execute(self, input_string):
        input_string_enc = input_string.encode('utf-8')
        root = et.fromstring(input_string_enc, parser=HeiEditionsParser())
        if self.parameters is None:
            result = self.funct(root)
        else:
            result = self.funct(root, self.parameters)
        result = et.tostring(result, encoding='unicode')
        if self.serial:
            super()._serialize(result)
        return result


class UnwrapStep(BaseStep):
    """
    UnwrapStep is a processing step that removes specified tags from elements in an input xml string,
    while keeping the children of those tags intact.

    Attributes:
        elements (list): A list of dictionaries specifying the elements to be unwrapped.
            Each dictionary should contain:
            - 'element_name': The name of the element to be removed.
            - 'attrib_name': (Optional) The name of an attribute to match.
            - 'attrib_val': (Optional) The value of the attribute to match.
        name (str, optional): The name of the step. Defaults to None.
        desc (str, optional): A description of the step. Defaults to None.
        serial (bool, optional): Whether to serialize the result after execution. Defaults to None.

    """
    def __init__(self, elements:list, name=None, desc=None, serial=None):
        super().__init__(name, desc, serial)
        self.elements = elements if len(elements) > 0 else []

    def __str__(self):
        return f"UnwrapStep »{self.name}«. Unwraps: {self.elements}"

    def execute(self, input_string):
        if len(self.elements) < 1:
            return input_string
        with importlib.resources.path('heipy.heipipe.xslt', 'unwrapFromElements.xsl') as xslt_file_path:
            true_xslt_file = str(xslt_file_path)
        for element in self.elements:
            params = [{
                'delenda_name': element.get('element_name'),
                'delenda_attr_name': element.get('attrib_name'),
                'delenda_attr_val': element.get('attrib_val'),
            }]
            result = apply_xslt(input_string, xslt_file= true_xslt_file,
                            parameters=params)
        if self.serial:
            super()._serialize(result)
        return result


class ValidationStep(BaseStep):
    """Validates the xml file. Returns the input to keep processing, but provides warnings in case of failed validation."""
    def __init__(self, name="validation", desc="Validate the files", serial=None, parameters=None):
        super().__init__(name,desc,serial)
        self.parameters = [] if parameters == None else parameters

    def __str__(self):
        return f"Validation step »{self.name}«"
    
    def execute(self, input_string):
        try:
            validate_xml_with_heieditions_schema(input_str=input_string)
            print(f"Validation succesful")
        except Exception as e:
            warnings.warn(f"{RED}Validation failed. {e}{RESET}")
            sys.exit(1)
        return input_string
