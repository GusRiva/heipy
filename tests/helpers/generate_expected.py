#!/usr/bin/env python3
"""
Generate auto_expected_*.xml output fixtures from input_*.xml fixtures.

This script automates the process of creating auto_expected_*.xml files by running
the actual step transformation on input_*.xml files. The 'auto_' prefix prevents
accidental overwriting of manually verified expected_*.xml files.

Workflow:
    1. Script generates auto_expected_*.xml files
    2. You manually review each auto_expected_*.xml file
    3. When verified correct, rename: auto_expected_*.xml → expected_*.xml

Configuration:
    Parameters can be provided via JSON config files (preferred) or command line:
    - config.json: Default config for all variants
    - config_{variant}.json: Config specific to a named variant

    Config file format (JSON):
    {
        "param_name": "param_value",
        "note_classes": "hc:TextCriticalNote hc:Comment"
    }

Usage:
    # Direct step: Generate all auto_expected_*.xml from all input_*.xml files
    python generate_expected.py combine_facsimile_and_text_to_sourcedoc

    # Nested step: Use full dotted path (uses matching config files)
    python generate_expected.py semantic.revision_spans_sem

    # Generate for a specific variant only (uses config_edge_case.json if present)
    python generate_expected.py semantic.revision_spans_sem --variant edge_case

    # With custom parameters (overrides config files)
    python generate_expected.py mark_note_as_editorial --params "note_classes='hc:TextCriticalNote hc:Comment'"
"""

import sys
import codecs
import argparse
from pathlib import Path
import json
import importlib

# Add src to path so we can import heipy
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from heipy.heipipe.steps import Pipeline


def load_step(step_name: str):
    """Dynamically load a step from step_library.

    Args:
        step_name: Step name, either direct (e.g., 'initials') or
                   nested with dot notation (e.g., 'semantic.revision_spans_sem')
    """
    try:
        module = importlib.import_module(f"heipy.heipipe.step_library.{step_name}")
        return module.get_step()
    except ImportError as e:
        print(f"Error: Could not import step '{step_name}'")
        print(f"For direct steps: src/heipy/heipipe/step_library/{step_name}.py")
        print(f"For nested steps: src/heipy/heipipe/step_library/{step_name.replace('.', '/')}.py")
        print(f"Use dot notation for nested steps (e.g., 'semantic.revision_spans_sem')")
        print(f"Error details: {e}")
        sys.exit(1)


def find_input_fixtures(step_dir: Path, variant: str = None) -> list:
    """Find input fixture files in a step directory."""
    if variant:
        pattern = f"input_{variant}.xml"
        files = list(step_dir.glob(pattern))
        if not files:
            print(f"Error: No file matching '{pattern}' found in {step_dir}")
            sys.exit(1)
        return files
    else:
        # Find all input_*.xml files
        files = list(step_dir.glob("input*.xml"))
        if not files:
            print(f"Error: No input_*.xml files found in {step_dir}")
            sys.exit(1)
        return sorted(files)


def load_config_for_variant(step_dir: Path, variant: str = None) -> dict:
    """
    Load configuration from config_*.json file for a specific variant.

    Looks for config files in this order:
    1. config_{variant}.json (if variant specified)
    2. config_basic.json (if no variant or variant is 'basic')
    3. config.json (fallback)

    Returns empty dict if no config file found.
    """
    config_files_to_try = []

    if variant:
        config_files_to_try.append(step_dir / f"config_{variant}.json")

    if not variant or variant == "basic":
        config_files_to_try.append(step_dir / "config_basic.json")

    config_files_to_try.append(step_dir / "config.json")

    for config_file in config_files_to_try:
        if config_file.exists():
            print(f"  Loading config from: {config_file.name}")
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

    return {}


def resolve_relative_paths(config: dict, step_dir: Path) -> dict:
    """
    Resolve relative file paths in config parameters relative to the step fixture directory.

    For any parameter that looks like a file path (contains 'path' or 'file' in the key),
    if the value is a relative path, it will be resolved relative to step_dir.

    Args:
        config: Configuration dictionary from JSON
        step_dir: The step's fixture directory path

    Returns:
        Updated config with resolved absolute paths
    """
    resolved_config = {}

    for key, value in config.items():
        # Check if this parameter looks like it contains a file path
        if isinstance(value, str) and ('path' in key.lower() or 'file' in key.lower()):
            # Check if it's a relative path (not absolute)
            path_value = Path(value)
            if not path_value.is_absolute():
                # Resolve relative to the step fixture directory
                resolved_path = (step_dir / value).resolve()
                resolved_config[key] = str(resolved_path)
                print(f"  Resolved relative path: {value} -> {resolved_path}")
            else:
                resolved_config[key] = value
        else:
            resolved_config[key] = value

    return resolved_config


def generate_expected(step_name: str, variant: str = None, params: dict = None):
    """Generate expected output from input fixture."""
    # Setup paths
    fixtures_base = project_root / "tests" / "fixtures" / "step_library"
    step_dir = fixtures_base / step_name

    if not step_dir.exists():
        print(f"Error: Step directory not found: {step_dir}")
        print("Please create the directory and add input_*.xml files.")
        print("For nested steps like 'semantic.revision_spans_sem', use dot notation in the directory name:")
        print("  tests/fixtures/step_library/semantic.revision_spans_sem/")
        sys.exit(1)

    print(f"Step: {step_name}")

    # Find input fixtures
    # If variant specified, only process that variant; otherwise process all
    if variant:
        input_files = find_input_fixtures(step_dir, variant)
        print(f"Processing variant: {variant}")
    else:
        input_files = find_input_fixtures(step_dir)
        print(f"Found {len(input_files)} input fixture(s)")

    # Process each input file
    for input_file in input_files:
        print(f"\nProcessing: {input_file.name}")

        # Extract variant from filename (input_variant.xml -> variant, input.xml -> None)
        file_variant = None
        if input_file.stem.startswith("input_"):
            file_variant = input_file.stem[6:]  # Remove "input_" prefix

        variant_name = input_file.stem.replace("input", "auto_expected")
        auto_expected_file = step_dir / f"{variant_name}.xml"

        # Load step fresh for each file
        print(f"  Loading step...")
        step = load_step(step_name)

        # Determine which parameters to use
        # Command-line params override config files
        if params is not None:
            # Use command-line params
            file_params = params
        else:
            # Load config for this specific file's variant
            file_params = load_config_for_variant(step_dir, file_variant)
            # Resolve any relative paths in the config relative to the fixture directory
            if file_params:
                file_params = resolve_relative_paths(file_params, step_dir)

        # Add parameters if any
        if file_params:
            for key, value in file_params.items():
                print(f"  Setting parameter: {key}={value}")
                step.add_parameter(key, value)

        # Execute step using a Pipeline
        try:
            print(f"  Executing transformation...")

            # Create a pipeline with just this step
            pipeline = Pipeline(name=f"generate_expected_{step_name}")
            pipeline.add_step(step)

            result_str = pipeline.execute(input_file)

        except Exception as e:
            print(f"  Error executing step: {e}")
            import traceback
            traceback.print_exc()
            continue

        # Save auto-generated output
        try:
            with codecs.open(auto_expected_file, 'wb', 'utf-8') as f:
                f.write(result_str)
            print(f"  ✓ Generated: {auto_expected_file.name}")
        except Exception as e:
            print(f"  Error saving output: {e}")
            continue

    print(f"\n{'='*60}")
    print("⚠️  IMPORTANT: Review and rename the generated files!")
    print("   1. Manually verify each auto_expected_*.xml file is correct")
    print("   2. Rename auto_expected_*.xml → expected_*.xml when verified")
    print("   This prevents accidental overwriting of verified fixtures.")
    print(f"{'='*60}")


def parse_params(param_string: str) -> dict:
    """Parse parameter string like "key1=val1 key2='val2'" into dict."""
    if not param_string:
        return {}

    params = {}
    # Simple parsing - split by spaces not inside quotes
    parts = []
    current = ""
    in_quotes = False

    for char in param_string:
        if char in ("'", '"'):
            in_quotes = not in_quotes
            current += char
        elif char == " " and not in_quotes:
            if current:
                parts.append(current)
                current = ""
        else:
            current += char
    if current:
        parts.append(current)

    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            # Remove quotes from value
            value = value.strip("'\"")
            params[key] = value

    return params


def main():
    parser = argparse.ArgumentParser(
        description="Generate expected output fixtures from input fixtures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output Files:
  Generates auto_expected_*.xml files (NOT expected_*.xml directly)
  This prevents accidental overwriting of verified fixtures.

  Workflow:
    1. Script creates auto_expected_*.xml
    2. You review the output
    3. Rename auto_expected_*.xml → expected_*.xml when verified

Configuration Files (preferred method):
  Parameters are automatically loaded from JSON config files:
  - config.json              (default for all variants)
  - config_basic.json        (for basic variant)
  - config_{variant}.json    (for specific variant)

  Config file format:
    {"param_name": "param_value"}

Examples:
  # Direct step: Generate all auto_expected_*.xml files
  python generate_expected.py combine_facsimile_and_text_to_sourcedoc

  # Nested step: Use full dotted path
  python generate_expected.py semantic.revision_spans_sem

  # Generate only specific variant
  python generate_expected.py mark_note_as_editorial --variant two_classes

  # With command-line parameters (overrides config files)
  python generate_expected.py mark_note_as_editorial --params "note_classes='hc:TextCriticalNote'"
        """
    )

    parser.add_argument(
        "step_name",
        help="Name of the step (must match directory name in tests/fixtures/step_library/)"
    )

    parser.add_argument(
        "--variant", "-v",
        help="Process only this specific variant (e.g., 'edge_case' for input_edge_case.xml). If not specified, all input_*.xml files are processed."
    )

    parser.add_argument(
        "--params", "-p",
        help="Step parameters as 'key1=val1 key2=val2' (overrides config files)"
    )

    args = parser.parse_args()

    # Parse parameters
    params = parse_params(args.params) if args.params else None

    # Generate expected outputs
    generate_expected(
        step_name=args.step_name,
        variant=args.variant,
        params=params
    )


if __name__ == "__main__":
    main()
