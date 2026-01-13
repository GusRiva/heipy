"""
Fixture loading utilities for heipy tests.

This module provides standardized ways to load test fixtures, particularly
for step library tests that follow the pattern of input/expected output pairs.

Classes:
- StepFixtureLoader: Load fixtures for transformation step tests
"""

from pathlib import Path
from typing import Tuple, Dict, Any, Optional, Union
from lxml import etree as et
import json

from heipy.parsers import HeiEditionsParser


class StepFixtureLoader:
    """
    Load test fixtures for transformation steps.

    This class provides a standardized interface for loading input/expected
    XML pairs and configuration files for step tests.

    Fixture Directory Structure:
        step_library/
            step_name/
                input.xml           # Default input
                expected.xml        # Default expected output
                input_variant.xml   # Named variant input
                expected_variant.xml # Named variant expected
                config.xml          # Optional configuration file
    """

    def __init__(self, fixtures_base: Path):
        """
        Initialize the fixture loader.

        Args:
            fixtures_base: Base directory for step fixtures
        """
        self.fixtures_base = Path(fixtures_base)
        self.parser = HeiEditionsParser()

    def load_step_fixture(self,
                         step_name: str,
                         fixture_name: str = "input",
                         must_exist: bool = True) -> Optional[et._ElementTree]:
        """
        Load a single fixture file for a step.

        Args:
            step_name: Name of the step (directory name)
            fixture_name: Name of the fixture file (without .xml)
            must_exist: If True, raise error if file doesn't exist

        Returns:
            Parsed XML tree, or None if file doesn't exist and must_exist=False

        Raises:
            FileNotFoundError: If file doesn't exist and must_exist=True

        Example:
            >>> loader = StepFixtureLoader(fixtures_dir)
            >>> input_tree = loader.load_step_fixture("move_note", "input")
            >>> variant_tree = loader.load_step_fixture("move_note", "input_edge_case")
        """
        fixture_path = self.fixtures_base / step_name / f"{fixture_name}.xml"

        if not fixture_path.exists():
            if must_exist:
                raise FileNotFoundError(
                    f"Fixture not found: {fixture_path}\n"
                    f"Expected fixture file for step '{step_name}' with name '{fixture_name}.xml'"
                )
            return None

        try:
            return et.parse(str(fixture_path), parser=self.parser)
        except et.XMLSyntaxError as e:
            raise ValueError(
                f"Invalid XML in fixture {fixture_path}: {e}"
            )

    def load_step_pair(self,
                      step_name: str,
                      variant: str = "") -> Tuple[et._ElementTree, et._ElementTree]:
        """
        Load input/expected pair for a step.

        Args:
            step_name: Name of the step
            variant: Optional variant name (e.g., "edge_case")

        Returns:
            Tuple of (input_tree, expected_tree)

        Raises:
            FileNotFoundError: If either input or expected file is missing

        Example:
            >>> loader = StepFixtureLoader(fixtures_dir)
            >>> input_tree, expected_tree = loader.load_step_pair("move_note")
            >>> # Load a variant
            >>> input_tree, expected_tree = loader.load_step_pair("move_note", "edge_case")
        """
        if variant:
            input_name = f"input_{variant}"
            expected_name = f"expected_{variant}"
        else:
            input_name = "input"
            expected_name = "expected"

        input_tree = self.load_step_fixture(step_name, input_name, must_exist=True)
        expected_tree = self.load_step_fixture(step_name, expected_name, must_exist=True)

        return input_tree, expected_tree

    def load_step_config(self,
                        step_name: str,
                        config_name: str = "config",
                        format: str = "xml") -> Union[et._ElementTree, Dict[str, Any]]:
        """
        Load configuration file for a step.

        Some steps (like inject_structure_new) require external configuration
        files. This method loads those configurations.

        Args:
            step_name: Name of the step
            config_name: Name of the config file (without extension)
            format: Format of config file ('xml' or 'json')

        Returns:
            Parsed config (ElementTree for XML, dict for JSON)

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If format is unsupported

        Example:
            >>> config = loader.load_step_config("inject_structure_new", "structure")
        """
        if format == "xml":
            return self.load_step_fixture(step_name, config_name, must_exist=True)
        elif format == "json":
            config_path = self.fixtures_base / step_name / f"{config_name}.json"
            if not config_path.exists():
                raise FileNotFoundError(f"Config not found: {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {format}")

    def load(self, relative_path: str, return_string: bool = False) -> Union[et._ElementTree, str]:
        """
        Load a fixture file using a relative path (hybrid API).

        This is a flexible method for loading any fixture within the fixtures_base
        directory using a simple relative path. It complements the structured
        methods (load_step_fixture, load_step_pair) by allowing direct path access.

        Args:
            relative_path: Path relative to fixtures_base (e.g., 'step_name/input_basic.xml'
                          or 'mark_note_as_editorial/input_basic.xml')
            return_string: If True, return XML as string instead of ElementTree

        Returns:
            Parsed XML ElementTree, or XML string if return_string=True

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not valid XML

        Example:
            >>> loader = StepFixtureLoader(fixtures_base)
            >>> # Load as ElementTree (default)
            >>> tree = loader.load('mark_note_as_editorial/input_basic.xml')
            >>> # Load as string
            >>> xml_str = loader.load('mark_note_as_editorial/input_basic.xml', return_string=True)
        """
        # Construct full path
        full_path = self.fixtures_base / relative_path

        # Check existence
        if not full_path.exists():
            raise FileNotFoundError(
                f"Fixture not found: {full_path}\n"
                f"Relative path: {relative_path}\n"
                f"Fixtures base: {self.fixtures_base}"
            )

        # Parse XML
        try:
            tree = et.parse(str(full_path), parser=self.parser)
        except et.XMLSyntaxError as e:
            raise ValueError(
                f"Invalid XML in fixture {full_path}: {e}"
            )

        # Return in requested format
        if return_string:
            return et.tostring(tree, encoding='unicode')
        return tree

    def tree_to_string(self, tree: Union[et._ElementTree, et._Element]) -> str:
        """
        Convert an ElementTree to XML string.

        Helper method for converting loaded fixtures to strings suitable
        for passing to step.execute().

        Args:
            tree: ElementTree or Element object

        Returns:
            XML string with unicode encoding

        Example:
            >>> tree = loader.load('step_name/input.xml')
            >>> xml_str = loader.tree_to_string(tree)
            >>> result = step.execute(xml_str)
        """
        if isinstance(tree, et._Element):
            return et.tostring(tree, encoding='unicode')
        elif isinstance(tree, et._ElementTree):
            return et.tostring(tree.getroot(), encoding='unicode')
        else:
            raise TypeError(f"Expected Element or ElementTree, got {type(tree)}")

    def get_step_fixture_path(self, step_name: str, fixture_name: str = "input") -> Path:
        """
        Get the path to a fixture file without loading it.

        Useful when you need to pass a file path to a function rather than
        loading the file content.

        Args:
            step_name: Name of the step
            fixture_name: Name of the fixture (without .xml)

        Returns:
            Path to the fixture file

        Example:
            >>> config_path = loader.get_step_fixture_path("inject_structure", "structure")
            >>> step.set_parameter_by_name("structure_file_path", str(config_path))
        """
        return self.fixtures_base / step_name / f"{fixture_name}.xml"

    def step_fixture_exists(self, step_name: str, fixture_name: str = "input") -> bool:
        """
        Check if a fixture file exists.

        Args:
            step_name: Name of the step
            fixture_name: Name of the fixture (without .xml)

        Returns:
            True if fixture exists, False otherwise

        Example:
            >>> if loader.step_fixture_exists("move_note", "edge_case"):
            ...     input_tree = loader.load_step_fixture("move_note", "edge_case")
        """
        fixture_path = self.fixtures_base / step_name / f"{fixture_name}.xml"
        return fixture_path.exists()

    def list_step_fixtures(self, step_name: str) -> Dict[str, list]:
        """
        List all available fixtures for a step.

        Returns:
            Dictionary with 'inputs', 'expected', and 'configs' lists

        Example:
            >>> fixtures = loader.list_step_fixtures("move_note")
            >>> print(fixtures['inputs'])  # ['input', 'input_edge_case', ...]
        """
        step_dir = self.fixtures_base / step_name
        if not step_dir.exists():
            return {'inputs': [], 'expected': [], 'configs': []}

        inputs = []
        expected = []
        configs = []

        for file in step_dir.glob("*.xml"):
            name = file.stem
            if name.startswith("input"):
                inputs.append(name)
            elif name.startswith("expected"):
                expected.append(name)
            elif name.startswith("config") or name == "structure":
                configs.append(name)

        return {
            'inputs': sorted(inputs),
            'expected': sorted(expected),
            'configs': sorted(configs)
        }

    def create_step_fixture_dir(self, step_name: str) -> Path:
        """
        Create a fixture directory for a step if it doesn't exist.

        Useful for generating fixtures programmatically.

        Args:
            step_name: Name of the step

        Returns:
            Path to the created directory

        Example:
            >>> fixture_dir = loader.create_step_fixture_dir("new_step")
            >>> # Now save fixtures to fixture_dir
        """
        step_dir = self.fixtures_base / step_name
        step_dir.mkdir(parents=True, exist_ok=True)
        return step_dir


class FixtureGenerator:
    """
    Helper class to generate test fixtures from actual transformations.

    This can be useful when:
    1. Creating initial fixtures for new tests
    2. Regenerating expected outputs after verified changes
    3. Creating regression test fixtures from bugs

    Warning: Always verify generated fixtures manually before using them!
    """

    def __init__(self, loader: StepFixtureLoader):
        """
        Initialize fixture generator.

        Args:
            loader: StepFixtureLoader instance
        """
        self.loader = loader

    def generate_expected_from_step(self,
                                    step,
                                    step_name: str,
                                    input_fixture_name: str = "input",
                                    expected_fixture_name: str = "expected") -> None:
        """
        Generate expected output by running a step on input fixture.

        WARNING: This should only be used for initial fixture creation or
        after manually verifying the step produces correct output!

        Args:
            step: Step instance to execute
            step_name: Name of the step (fixture directory)
            input_fixture_name: Name of input fixture
            expected_fixture_name: Name to save expected output as

        Example:
            >>> from heipy.heipipe.step_library import filter_visual_information
            >>> generator = FixtureGenerator(loader)
            >>> step = filter_visual_information.get_step()
            >>> # Only do this after verifying the step works correctly!
            >>> generator.generate_expected_from_step(step, "filter_visual_information")
        """
        # Load input
        input_tree = self.loader.load_step_fixture(step_name, input_fixture_name)
        input_str = et.tostring(input_tree, encoding='unicode')

        # Execute step
        result_str = step.execute(input_string=input_str)

        # Save expected
        expected_path = self.loader.get_step_fixture_path(step_name, expected_fixture_name)
        with open(expected_path, 'w', encoding='utf-8') as f:
            f.write(result_str)

        print(f"Generated expected output at: {expected_path}")
        print("WARNING: Manually verify this output before using it in tests!")

    def save_xml_as_fixture(self,
                           xml_tree: et._ElementTree,
                           step_name: str,
                           fixture_name: str) -> Path:
        """
        Save an XML tree as a fixture file.

        Args:
            xml_tree: XML tree to save
            step_name: Step name (fixture directory)
            fixture_name: Name for the fixture (without .xml)

        Returns:
            Path where fixture was saved

        Example:
            >>> tree = et.parse("some_file.xml")
            >>> path = generator.save_xml_as_fixture(tree, "move_note", "input")
        """
        # Ensure directory exists
        self.loader.create_step_fixture_dir(step_name)

        # Get path
        fixture_path = self.loader.get_step_fixture_path(step_name, fixture_name)

        # Save with proper formatting
        xml_tree.write(
            str(fixture_path),
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True
        )

        return fixture_path
