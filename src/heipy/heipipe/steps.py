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
from ..parsers import apply_xslt, HeiEditionsParser, validate_xml_with_heieditions_schema
from ..colors import *
from ..heiwarning import HeiWarning


class BaseStep:
    """ Base class for all steps """
    def __init__(self, name=None, desc=None, serial=False, parameters=None):
        self.name = name
        self.desc = desc
        self.serial = serial
        self.parameters = parameters
        self.index = -1

    def add_parameter(self, param:dict):
        self.parameters.append(param)
        return 

    def get_desc(self):
        return self.desc

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
    add_step(step, at_index=None, serial=False, parameters=None):
        Adds a step to the pipeline at the specified index.
    execute(input):
        Executes the pipeline on the given input.
    get_steps():
        Returns the list of steps in the pipeline.
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
        return f"Pipeline '{self.name}'"

    def add_step(self, step, at_index=None, serial=False, parameters=None):
        """
        Adds a step to the pipeline. 

        Parameters:
        step (Step): The step to be added to the pipeline. The step can be an instance of any of the subclasses of BaseStep.
        at_index (int, optional): The index at which to insert the step. If None, the step is appended to the end.
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
        step_idx = len(self.steps)
        step.set_index(step_idx)
        step.set_parameters(parameters)
        if isinstance(step, Pipeline):
            print(step) # Here should add handle when a pipeline is added as a step to another pipeline
        if at_index is None:            
            step.set_index(len(self.steps) - 1) 
            self.steps.append(step)
        else:
            if not isinstance(at_index, int):
                Warning.warn(f"Step  {step.name}: Index must be a positive integer. Now: {at_index}. Step will not be added.")
                return
            if at_index > len(self.steps) - 1:
                Warning.warn(f"Step:  {step.name} was added with an index higher than possible: {at_index}. This pipeline has now {len(self.steps)}. Step will not be added.")
                return
            if at_index < 0:
                Warning.warn(f"Step  {step.name}: Index must be a positive integer (0 or higher). Index now is {idx}. Step will not be added.")
                return
            step.set_index(at_index) 
            self.steps.insert(at_index, step)

    def execute(self, input):
        """
        Executes the pipeline on the given input file.

        Args:
            input (str): The XML document in its string representation.

        Returns:
            str: The processed string after all pipeline steps have been executed.
        """
        print(f"Starting Pipeline {self.name} for {input[:60]}")
        if not os.path.isfile(input):
            warnings.warn(f'Could not find file {input}, skipping...', HeiWarning)
            return None

        input_file = codecs.open(input, "r", "utf-8")
        input_string = input_file.read()
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
    def __init__(self, files=None, parameters=None, name=None, desc=None, serial=False, pipe_files=False):
        super().__init__(name, desc, serial)
        self.files = [] if files is None else files
        self.pipe_files = pipe_files
        self.parameters = [] if parameters is None else parameters

    def __str__(self):
        return f"XSLStep {self.name} containing {len(self.files)} transformations and {len(self.parameters)} parameters."

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
    """Removes all the tags in elements, keeping the children intact"""
    def __init__(self, match:str, att_name:str, att_val:str, name=None, desc=None, serial=None):
        super().__init__(name, desc, serial)
        self.match = match
        self.att_name = att_name
        self.att_val = att_val

    def __str__(self):
        return f"Add Attribute Step for: {self.match}, {self.att_name}, {self.att_val}"

    def execute(self, input_string):
        input_string_enc = input_string.encode('utf-8')
        root = et.fromstring(input_string_enc, parser=HeiEditionsParser())
        matches = root.xpath(f"//{self.match}", namespaces=ns)
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
        elements (list): A list of XML element names to be deleted, with optional filters in the xpath syntax of square brackets.
        name (str, optional): The name of the step. Defaults to None.
        desc (str, optional): A description of the step. Defaults to None.
        serial (bool, optional): A flag indicating whether to serialize the result. Defaults to None.

    Methods:
        __str__(): Returns a string representation of the DeleteStep instance.
        execute(input_string): Executes the deletion of specified XML elements from the input string.
            Args:
                input_string (str): The input XML string.
            Returns:
                str: The resulting XML string after deletion of specified elements.
    """
    def __init__(self, elements:list, name=None, desc=None, serial=None):
        super().__init__(name, desc, serial)
        self.elements = elements

    def __str__(self):
        return f"DeleteStep for: {self.elements}"

    def execute(self, input_string):
        if len(self.elements) < 1:
            return input_string
        input_stream = io.BytesIO(input_string.encode('utf-8'))
        tree = et.parse(input_stream, parser=HeiEditionsParser())
        root = tree.getroot()
        for elem_name in self.elements:
            xpath_ex = f".//{elem_name}"
            for elem in root.xpath(xpath_ex, namespaces=ns):
                elem.getparent().remove(elem)
        result = et.tostring(tree, encoding='utf-8').decode('utf-8')
        if self.serial:
            super()._serialize(result)
        return result


class PythonStep(BaseStep):
    def __init__(self, funct, parameters=None, name=None, desc=None, serial=False):
        super().__init__(name, desc, serial)
        self.funct = funct

    def __str__(self):
        return f"Python step using: {self.funct}"

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
    """Removes all the tags in elements, keeping the children intact"""
    def __init__(self, elements:list, name=None, desc=None, serial=None):
        super().__init__(name, desc, serial)
        self.elements = elements

    def __str__(self):
        return f"UnwrapStep for: {self.elements}"

    def execute(self, input_string):
        if len(self.elements) < 1:
            return input_string
        for element in self.elements:
            params = [{
                'delenda_name': element.get('element_name'),
                'delenda_attr_name': element.get('attrib_name'),
                'delenda_attr_val': element.get('attrib_val'),
            }]
            result = apply_xslt(input_string, xslt_file='unwrapFromElements.xsl',
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
        return "Validation step"
    
    def execute(self, input_string):
        try:
            validate_xml_with_heieditions_schema(input_str=input_string)
            print(f"Validation succesful")
        except Exception as e:
            warnings.warn(f"{RED}Validation failed. {e}{RESET}")
            sys.exit(1)
        return input_string
