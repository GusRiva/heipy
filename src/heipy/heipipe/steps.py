# steps.py
import codecs
import importlib
import io
import os
import sys
import time
import warnings
from abc import abstractmethod
from typing import Literal
from lxml import etree as et
from saxonche import PySaxonProcessor

from ..namespaces import ns
from ..colors import BLUE, RED, RESET
from ..heiwarning import HeiWarning, HeiDeprecationWarning
from ..parsers import (
    apply_xslt,
    heiparse,
    HeiEditionsParser,
    validate_xml_with_heieditions_schema,
    normalize_parameters,
    OutputFormat
)


class BaseStep:
    """Base class for all steps"""

    def __init__(self, name=None, desc=None, serial=False, parameters=None):
        self.name = name if name is not None else "__None__"
        self.desc = desc
        self.serial = serial
        self.parameters = normalize_parameters(parameters if parameters is not None else {})
        self.index = None # Outside of pipeline

    def add_parameter(self, *args, **kwargs):
        """
        Add a parameter to the step.

        Supports two calling styles:
        1. add_parameter(name, value) - Recommended
        2. add_parameter({'key': 'value'}) - Legacy, deprecated

        Args:
            *args: Either (name, value) or (dict,)
            **kwargs: Not used, for future compatibility
        """
        if len(args) == 1 and isinstance(args[0], dict):
            # Legacy format: add_parameter({'key': 'value'})
            warnings.warn(
                "Passing a dictionary to add_parameter is deprecated. "
                "Please use add_parameter(name, value) instead.",
                HeiDeprecationWarning,
                stacklevel=2
            )
            self.parameters.update(args[0])
        elif len(args) == 2:
            # New format: add_parameter('key', 'value')
            name, value = args
            if not isinstance(name, str):
                raise TypeError(f"name must be a string, got {type(name)}")
            self.parameters[name] = value
        else:
            raise TypeError(
                f"add_parameter() takes 1 (dict) or 2 (name, value) positional arguments "
                f"but {len(args)} were given"
            )
        return

    def add_parameters(self, parameters: dict):
        """
        Add multiple parameters at once from a dictionary.

        This is the recommended way to add multiple parameters.

        Args:
            parameters (dict): Dictionary of parameter name-value pairs to add

        Example:
            step.add_parameters({
                'param1': 'value1',
                'param2': 'value2',
                'param3': 'value3'
            })
        """
        if not isinstance(parameters, dict):
            raise TypeError(f"parameters must be a dict, got {type(parameters)}")
        self.parameters.update(parameters)
        return

    def get_desc(self):
        return self.desc

    def get_index(self):
        return self.index

    def get_name(self):
        return self.name

    def get_parameter_by_name(self, name: str):
        """
        Get a parameter value by name.

        Args:
            name: Parameter name to retrieve

        Returns:
            Parameter value or None if not found
        """
        if self.parameters is None:
            return None
        return self.parameters.get(name)

    def get_parameters(self):
        """
        Get the parameters for the current instance.

        Returns:
            dict: A dictionary containing the parameters
        """
        return self.parameters

    def get_serial(self):
        return self.serial

    def set_index(self, idx):
        self.index = idx

    def set_parameters(self, parameters):
        """
        Set the parameters for the current instance.

        Args:
            parameters (dict or list): A dictionary containing the parameters to be set.
                Legacy list format [{'key1': 'val1'}, {'key2': 'val2'}] is also supported
                but deprecated. Use {'key1': 'val1', 'key2': 'val2'} instead.
        """
        self.parameters = normalize_parameters(parameters)

    def set_parameter(self, key: str, content):
        """
        Set a specific parameter by name.
        Args:
            name: Parameter name
            content: Parameter value
        """
        self.parameters[key] = content
        return

    def set_parameter_by_name(self, name: str, content):
        """
        Set a specific parameter by name.
        DEPRECATED: Use set_parameter() instead.
        Args:
            name: Parameter name
            content: Parameter value
        """
        warnings.warn(
            "set_parameter_by_name() is deprecated. "
            "Please use set_parameter(key, value) instead.",
            HeiDeprecationWarning,
            stacklevel=2
        )
        self.parameters[name] = content
        return

    def set_serial(self, value: bool):
        self.serial = value

    def _serialize(self, xml_string, file_name=None):
        if not self.serial:
            pass
        if file_name is None:
            file_name = f"tmp/{self.index}_{self.name}.xml"
        if not file_name.endswith(".xml"):
            file_name += ".xml"
        output_file_serial = codecs.open(f"{file_name}", "w", "utf-8")
        output_file_serial.write(xml_string)
        output_file_serial.close()

    @abstractmethod
    def execute(self, input_string, serial=False):
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
            raise TypeError("steps must be a list")
        self.steps = steps
        if len(self.steps) > 0:
            for idx, step in enumerate(self.steps):
                step.set_index(idx)
        return

    def __str__(self):
        return f"Pipeline »{self.name}« containing {len(self.steps)} steps."

    def add_step(
        self,
        step,
        at_index: int = None,
        after_step: str = None,
        before_step: str = None,
        serial=False,
        parameters=None,
    ):
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
            raise SyntaxError(
                f"You can only use one positional paramter for your new step. You are currently using: at_index={at_index}, after_step={after_step}, before_step={before_step}."
            )

        if step.get_name() in [x.get_name() for x in self.get_steps()]:
            raise NameError(
                f"Step with the name »{step.get_name()}« already exists in the Pipeline."
            )

        if isinstance(step, Pipeline):
            print(
                step
            )  # Here should add handle when a pipeline is added as a step to another pipeline

        def add_step_intern(idx):
            step.set_index(idx)
            if step.get_name() == "__None__":
                step.name = "__None__" + str(idx)
            self.steps.insert(idx, step)

        if at_index is not None:
            if at_index > len(self.steps) - 1:
                warnings.warn(
                    f"Step  »{step.name}«: was added with an index higher than possible: {at_index}. This pipeline has now {len(self.steps)}. Step will not be added."
                )
                return
            if at_index < 0:
                warnings.warn(
                    f"Step  »{step.name}«: Index must be a positive integer (0 or higher). Index now is {at_index}. Step will not be added."
                )
                return
            add_step_intern(at_index)

        elif after_step or before_step is not None:
            try:
                idx_mod = 1 if after_step is not None else 0
                new_step_idx = [x.get_name() for x in self.get_steps()].index(
                    after_step or before_step
                )
                step_index = new_step_idx + idx_mod
                add_step_intern(step_index)
            except ValueError:
                warnings.warn(
                    f"Could not find step »{after_step}« in pipeline {self.name}, in relation to which you want to add step {step}. Step will not be added."
                )

        else:
            step_index = len(self.steps)
            add_step_intern(step_index)

    def execute(self, 
                input, 
                xinclude=False, 
                egxml=False,
                output_format: Literal["str", "etree", "bytes"] = "str", 
                debug_options=None):
        """
        Executes the pipeline on the given input file with optimized batching.

        Args:
            input (str): The XML document in its string representation.
            xinclude (bool): Does the starting file contain xinclude elements that need to be resolved at the start of the pipeline? Defaults to False.
            egxml (bool): Does the starting file contain <egXML> elements?
            debug_options (list): Which debug options should be active. Available options: time, serial.

        Returns:
            str: The processed string after all pipeline steps have been executed.
        """
        output_format = OutputFormat(output_format)
        print(f"Starting Pipeline {BLUE}{self.name}{RESET} for {BLUE}{input[:60]}{RESET}")
        if not os.path.isfile(input):
            warnings.warn(f"Could not find file {input}, skipping...", HeiWarning)
            return None
        
        debug_options = debug_options if debug_options is not None else []
        input_string = heiparse(
            input, output_format=OutputFormat.STR, xinclude=xinclude, egxml=egxml, base_url=input
        )
        pipe_serial = True if self.serial or 'serial' in debug_options else False

        # Process steps with batching optimization
        i = 0
        current_data = input_string
        is_xdm = False
        proc = None

        while i < len(self.steps):
            step = self.steps[i]
            start_time = time.time()

            # Check if we can batch XSLT steps
            if isinstance(step, (XsltStep, UnwrapStep)):
                # Look ahead for consecutive XSLT-based steps
                j = i + 1
                while j < len(self.steps) and isinstance(self.steps[j], (XsltStep, UnwrapStep)):
                    j += 1

                # Create processor for batch using context manager
                with PySaxonProcessor(license=False) as proc:
                    # Execute batch
                    for k in range(i, j):
                        batch_step = self.steps[k]
                        output_xdm = (k < j - 1)  # Keep XDM until last step in batch

                        current_data = batch_step.execute(
                            input_string=current_data if not is_xdm else None,
                            serial=pipe_serial,
                            input_xdm=current_data if is_xdm else None,
                            output_xdm=output_xdm,
                            proc=proc
                        )
                        is_xdm = output_xdm

                # Processor automatically closed after context
                i = j

            else:
                # Non-XSLT step - use regular execute
                if is_xdm:
                    # This shouldn't happen if batching logic is correct
                    raise RuntimeError("Non-XSLT step received XDM input")

                current_data = step.execute(current_data, pipe_serial)
                i += 1

            end_time = time.time()
            elapsed_time = end_time - start_time
            if 'time' in debug_options:
                print(f"Elapsed time for '{step.get_name()}': {elapsed_time}")
        # if egxml:
        #     current_data = unscape_egxml(current_data)
        if output_format == OutputFormat.STR:
            return current_data
        if output_format == OutputFormat.ETREE:
            return current_data

    def get_steps(self):
        return self.steps

    def get_step_by_name(self, name: str) -> BaseStep:
        for step in self.get_steps():
            step_name = step.get_name()
            if step_name != name:
                continue
            return step
        return

    def remove_step(self, step_name: str = None, step_index: int = None):
        if (step_name, step_index).count(None) != 1:
            raise SyntaxError(
                f"The function remove_step() must contain only one of the parameters step_name or step_index. Currently step_name={step_name} , step_index={step_index} ."
            )
        if step_index is not None:
            return self.steps.pop(step_index)

        if step_name is not None:
            for i, step in enumerate(self.steps):
                if step.get_name() == step_name:
                    return self.steps.pop(i)
            warnings.warn(
                f"Could not find step with name »{step_name}« to remove in pipeline."
            )
        return

    def set_pipestep_parameter(
        self, step: str | int, parameter_name: str, parameter_value
    ):
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
        if isinstance(step, str):
            step_obj = self.get_step_by_name(step)
            if step_obj is None:
                raise ValueError(f"Could not find parameter with the name {step}")
        elif isinstance(step, int):
            if len(self.get_steps()) <= step:
                raise IndexError(
                    f"The pipeline: {self}, contains only {len(self.get_steps())} steps and you are trying to access step at index {step}."
                )
            step_obj = self.get_steps()[step]
        else:
            raise TypeError(f"{step} should be string of integer")
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

    def __init__(
        self,
        files=None,
        parameters=None,
        name=None,
        desc=None,
        serial=False,
        pipe_files=False,
    ):
        # Set default name to __XsltStep__ instead of __None__
        if name is None:
            name = "__XsltStep__"
        super().__init__(name, desc, serial, parameters)
        self.files = [] if files is None else files
        self.pipe_files = pipe_files

        # Warn if no XSLT files provided
        if len(self.files) == 0:
            warnings.warn(
                "An XsltStep with no XSLT files does nothing and is skipped",
                HeiWarning,
                stacklevel=2
            )

    def __str__(self):
        return f"XSLStep »{self.name}« containing {len(self.files)} transformations {self.files} and {len(self.parameters)} parameters {self.parameters if len(self.parameters) > 0 else ''}."

    def get_files(self) -> list:
        return self.files

    def execute(self, input_string=None, serial=False, input_xdm=None, output_xdm=False, proc=None):
        """
        Execute XSLT transformation(s).

        Args:
            input_string: XML string (if input_xdm is None)
            serial: Whether to serialize output to file
            input_xdm: PyXdmNode input (optional, for batched execution)
            output_xdm: If True, return XDM instead of string
            proc: PySaxonProcessor instance (optional, for batched execution)

        Returns:
            str or PyXdmNode depending on output_xdm
        """
        current_data = input_xdm if input_xdm is not None else input_string
        is_xdm = input_xdm is not None

        for file in self.files:
            # start_time = time.time()
            true_xslt_file = None
            file_name = file

            # Resolve file path
            if self.pipe_files:
                base_xsl_location = "heipy.heipipe.xslt"
                if "/" in file:
                    file_path_parts = file.split('/')
                    file_name = file_path_parts[-1]
                    relpath2file = '.'.join(file_path_parts[:-1])
                    base_xsl_location += f'.{relpath2file}'
                xslt_files = importlib.resources.files(base_xsl_location)
                true_xslt_file = str(xslt_files.joinpath(file_name))
            else:
                true_xslt_file = str(file)

            if true_xslt_file is None:
                warnings.warn(f"{RED}Could not find the xslt file: {file}")
                return current_data

            # Determine if this is the last file in this step
            is_last_file = (file == self.files[-1])
            # Keep as XDM during processing, only convert to string on last file if output_xdm=False
            should_output_xdm = (not is_last_file) or output_xdm

            # Apply transformation
            current_data = apply_xslt(
                input_string=current_data if not is_xdm else None,
                xslt_file=true_xslt_file,
                parameters=self.get_parameters(),
                input_xdm=current_data if is_xdm else None,
                output_xdm=should_output_xdm,
                proc=proc
            )
            is_xdm = should_output_xdm

            # end_time = time.time()
            # elapsed_time = end_time - start_time
            # print(f"Time for {file}: {elapsed_time:.4f} seconds")

        # Result is already in the requested format
        result = current_data

        if self.serial or serial:
            if not output_xdm:
                super()._serialize(result)

        return result


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


    def __init__(

        self, match:  str, att_name:  str, att_val:  str, name=None, desc=None, serial=None

    ):
        # Set default name to __AddAttribute__ instead of __None__
        if name is None:
            name = "__AddAttribute__"
        super().__init__(name, desc, serial)
        self.match = match
        self.att_name = att_name
        self.att_val = att_val

    def __str__(self):
        return f"Add Attribute Step »{self.name}«. match: {self.match}, att_name: {self.att_name}, att_val: {self.att_val}"

    def execute(self, input_string, serial=False):
        input_string_enc = input_string.encode("utf-8")
        root = et.fromstring(input_string_enc, parser=HeiEditionsParser())
        matches = root.xpath(f"{self.match}", namespaces=ns)
        for match in matches:
            match.set(self.att_name, self.att_val)
        result = et.tostring(root, encoding="unicode")
        if self.serial or serial:
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

    def __init__(self, elements: list, name=None, desc=None, serial=None):
        # Set default name to __Delete__ instead of __None__
        if name is None:
            name = "__Delete__"
        super().__init__(name, desc, serial)
        self.elements = elements

        # Warn if no elements provided
        if len(self.elements) == 0:
            warnings.warn(
                "A DeleteStep with no elements does nothing and is skipped",
                HeiWarning,
                stacklevel=2
            )

    def __str__(self):
        return f"DeleteStep »{self.name}«. Deletes: {self.elements}"

    def execute(self, input_string, serial=False):
        if len(self.elements) < 1:
            return input_string
        input_stream = io.BytesIO(input_string.encode("utf-8"))
        tree = et.parse(input_stream, parser=HeiEditionsParser())
        root = tree.getroot()
        for elem_name in self.elements:
            if elem_name[:1] != "/":
                elem_name = "//" + elem_name
            xpath_ex = f".{elem_name}"
            for elem in root.xpath(xpath_ex, namespaces=ns):
                parent = elem.getparent()
                if elem.tail:
                    prev = elem.getprevious()
                    if prev is not None:
                        # Append the tail text to the previous sibling’s tail
                        if prev.tail:
                            prev.tail += elem.tail
                        else:
                            prev.tail = elem.tail
                    else:
                        # If no previous sibling, append to parent’s text
                        if parent.text:
                            parent.text += elem.tail
                        else:
                            parent.text = elem.tail
                parent.remove(elem)
        result = et.tostring(tree, encoding="utf-8").decode("utf-8")
        if self.serial or serial:
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
        # Set default name to __PythonStep__ instead of __None__
        if name is None:
            name = "__PythonStep__"
        super().__init__(name, desc, serial, parameters)
        self.funct = funct

    def __str__(self):
        return f"Python step »{self.name}«, using: {self.funct}"

    def execute(self, input_string, serial=False):
        input_string_enc = input_string.encode("utf-8")
        root = et.fromstring(input_string_enc, parser=HeiEditionsParser())
        if self.parameters is None or len(self.parameters) == 0:
            result = self.funct(root)
        else:
            result = self.funct(root, self.parameters)
        result = et.tostring(result, encoding="unicode")
        if self.serial or serial:
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

    def __init__(self, elements: list, name=None, desc=None, serial=None):
        # Set default name to __Unwrap__ instead of __None__
        if name is None:
            name = "__Unwrap__"
        super().__init__(name, desc, serial)
        self.elements = elements if len(elements) > 0 else []

        # Warn if no elements provided
        if len(self.elements) == 0:
            warnings.warn(
                "An UnwrapStep with no elements does nothing and is skipped",
                HeiWarning,
                stacklevel=2
            )

    def __str__(self):
        return f"UnwrapStep »{self.name}«. Unwraps: {self.elements}"

    def execute(self, input_string=None, serial=False, input_xdm=None, output_xdm=False, proc=None):
        """
        Execute unwrap transformation(s).

        Args:
            input_string: XML string (if input_xdm is None)
            serial: Whether to serialize output to file
            input_xdm: PyXdmNode input (optional, for batched execution)
            output_xdm: If True, return XDM instead of string
            proc: PySaxonProcessor instance (optional, for batched execution)

        Returns:
            str or PyXdmNode depending on output_xdm
        """
        from saxonche import PySaxonProcessor

        if len(self.elements) < 1:
            return input_xdm if input_xdm is not None else input_string

        current_data = input_xdm if input_xdm is not None else input_string
        is_xdm = input_xdm is not None

        xslt_files = importlib.resources.files("heipy.heipipe.xslt")
        true_xslt_file = str(xslt_files.joinpath("unwrapFromElements.xsl"))

        # Define inner function to process all elements with a shared processor
        def _process_elements(shared_proc):
            nonlocal current_data, is_xdm

            for idx, element in enumerate(self.elements):
                params = [
                    {
                        "delenda_name": element.get("element_name"),
                        "delenda_attr_name": element.get("attrib_name"),
                        "delenda_attr_val": element.get("attrib_val"),
                    }
                ]
                # Determine if this is the last element
                is_last_element = (idx == len(self.elements) - 1)
                # Keep as XDM during processing, only convert to string on last element if output_xdm=False
                should_output_xdm = (not is_last_element) or output_xdm

                # Apply transformation with shared processor
                current_data = apply_xslt(
                    input_string=current_data if not is_xdm else None,
                    xslt_file=true_xslt_file,
                    parameters=params,
                    input_xdm=current_data if is_xdm else None,
                    output_xdm=should_output_xdm,
                    proc=shared_proc
                )
                is_xdm = should_output_xdm

            return current_data

        # If processor provided (batched mode), use it; otherwise create one for all iterations
        if proc is not None:
            result = _process_elements(proc)
        else:
            with PySaxonProcessor(license=False) as shared_proc:
                result = _process_elements(shared_proc)

        if self.serial or serial:
            if not output_xdm:
                super()._serialize(result)

        return result


class ValidationStep(BaseStep):
    """Validates the xml file. Returns the input to keep processing, but provides warnings in case of failed validation."""

    def __init__(
        self, name="validation", desc="Validate the files", serial=None, parameters=None
    ):
        super().__init__(name, desc, serial, parameters)

    def __str__(self):
        return f"Validation step »{self.name}«"

    def execute(self, input_string, serial=False):
        try:
            validate_xml_with_heieditions_schema(input_str=input_string)
            print("Validation successful")
        except Exception as e:
            warnings.warn(f"{RED}Validation failed. {e}{RESET}")
            sys.exit(1)
        return input_string
