# heipy Repository Overview

## Introduction

heipy is a Python package designed for digital scholarly editing, providing a flexible and powerful pipeline system for transforming TEI-XML documents. The package implements an XProc-like architecture using Python, combining XSLT 3.0 transformations with custom Python processing steps to handle complex editorial workflows.

## Repository Structure

```
heipy/
├── bin/                           # Shell scripts for eXist-db integration
├── src/heipy/                     # Main source code
│   ├── heipipe/                   # Pipeline system (core module)
│   │   ├── steps.py               # Core step and pipeline classes
│   │   ├── cli_utils.py           # Command-line interface utilities
│   │   ├── step_library/          # Pre-built transformation steps (~35 steps)
│   │   │   ├── synoptic/          # Synoptic-specific steps
│   │   │   ├── validation.py      # Validation step
│   │   │   ├── whitespaces.py     # Whitespace normalization
│   │   │   ├── initials.py        # Initial handling
│   │   │   ├── container2milestone.py  # Container to milestone conversion
│   │   │   ├── inject_structure_new.py # Structure injection
│   │   │   └── ... (~30 more steps)
│   │   ├── pipeline_library/      # Pre-configured pipelines
│   │   │   ├── semantic.py        # Semantic pipeline
│   │   │   ├── sourcedoc.py       # Source document pipeline
│   │   │   ├── synoptic.py        # Synoptic pipeline
│   │   │   ├── plaintext.py       # Plain text extraction
│   │   │   └── index.py           # Index generation
│   │   └── xslt/                  # XSLT transformation files
│   │       └── index/             # Index-specific XSLT files
│   ├── schema/                    # TEI heiEDITIONS schema files
│   │   ├── heieditions-entities.txt  # Entity definitions
│   │   └── catalog.xml            # Schema catalog
│   ├── templates/                 # XML templates
│   │   ├── cmif_template.xml      # CMIF export template
│   │   └── synoptic_map.xml       # Synoptic map template
│   ├── xquery/                    # XQuery scripts
│   ├── synopse.py                 # Synoptic text alignment functionality
│   ├── cmif.py                    # CMIF (Correspondence Metadata) export
│   ├── combine.py                 # Combining multiple TEI documents
│   ├── parsers.py                 # XML parsing utilities
│   ├── validation.py              # Validation utilities
│   ├── namespaces.py              # XML namespace definitions
│   ├── colors.py                  # Terminal color utilities
│   └── heiwarning.py              # Warning utilities
├── tests/                         # Test files
│   ├── conftest.py                # Pytest fixtures (hei_parser, basic_tei, tei_with_entities)
│   ├── fixtures/                  # Test fixture files
│   │   ├── minimal/               # Basic TEI documents
│   │   │   ├── basic_tei.xml      # Simple TEI without entities
│   │   │   └── tei_with_entities.xml  # TEI with heiEDITIONS entities
│   │   └── README.md              # Fixture documentation
│   ├── helpers/                   # Test helper utilities
│   │   ├── xml_compare.py         # XML comparison functions
│   │   └── fixture_loader.py      # Fixture loading utilities
│   ├── unit/                      # Unit tests
│   │   ├── test_base_step.py      # BaseStep tests
│   │   ├── test_python_step.py    # PythonStep tests
│   │   ├── test_delete_step.py    # DeleteStep tests
│   │   ├── test_unwrap_step.py    # UnwrapStep tests
│   │   └── test_add_attribute_step.py  # AddAttribute tests
│   ├── parsers/                   # Parser I/O tests
│   │   └── test_parser_io.py      # Entity preservation & roundtrip tests
│   ├── steps/                     # Step-specific tests (placeholder)
│   └── integration/               # Integration tests (placeholder)
├── knowledge/                     # Project documentation
│   ├── repository_overview.md     # This file
│   ├── FIXTURE_STRATEGY.md        # Test fixture strategy
│   ├── DATA_ANALYSIS.md           # TEI data structure analysis
│   └── external/                  # External reference files
├── setup.py                       # Package installation configuration
├── requirements.txt               # Python dependencies
├── README.md                      # Documentation
└── tutorial.ipynb                 # Jupyter notebook tutorial
```

## Core Components

### 1. Pipeline System (heipipe)

The heart of heipy is its pipeline system, which provides an XProc-like processing architecture implemented in pure Python. This allows complex XML transformations to be composed from reusable, modular steps.

#### Key Classes

**BaseStep** (Abstract Base Class)
- Provides common functionality for all step types
- Manages parameters, serialization, and execution
- Base for all specific step implementations

**Pipeline** (extends BaseStep)
- Container for sequential processing steps
- Can contain XsltStep, PythonStep, or nested Pipeline objects
- Features:
  - Dynamic step management (add, remove, get by name/index)
  - Parameter setting for individual steps
  - Optimized batch execution for consecutive XSLT steps
  - Debug options (timing, serialization)
  - XInclude and egXML support

**XsltStep** (extends BaseStep)
- Executes one or more XSLT transformations in sequence
- Uses SaxonHE via saxonche (Saxon C API for Python)
- Supports XSLT 3.0 features
- Can load XSLT files from package resources or external paths
- Supports parameter passing to XSLT stylesheets

**PythonStep** (extends BaseStep)
- Executes custom Python functions on XML documents
- Receives lxml ElementTree root and parameters
- Returns modified root element
- Allows for complex transformations not easily expressed in XSLT

**Specialized Steps**
- **UnwrapStep**: Removes wrapper elements while preserving children
- **DeleteStep**: Removes specified elements from the XML tree
- **AddAttribute**: Adds attributes to elements matching XPath expressions
- **ValidationStep**: Validates XML against heiEDITIONS RelaxNG schema

#### Pipeline Execution Flow

1. **Input Processing**: Parse input file with optional XInclude resolution and egXML preprocessing
2. **Step Batching**: Group consecutive XSLT steps for optimized execution
3. **Batch Execution**:
   - Create single Saxon processor for batch
   - Keep intermediate results as XDM nodes (avoids serialization/parsing overhead)
   - Only serialize to string at batch end
4. **Python Steps**: Execute with full serialization round-trip
5. **Output**: Return result in requested format (string/etree/bytes)

#### Performance Optimizations

The pipeline implements sophisticated optimizations to minimize overhead:

- **XSLT Batching**: Consecutive XSLT steps are executed within a single Saxon processor instance, keeping intermediate results as XDM nodes rather than serializing to strings
- **Lazy Serialization**: XML is only serialized when switching between XSLT and Python steps or for final output
- **Processor Reuse**: Saxon processors are reused within batches to avoid initialization overhead

### 2. Integration of XSLT and Python Steps

#### XSLT Step Pattern

XSLT steps are defined in the `step_library/` directory and load transformations from the `xslt/` folder:

```python
# Example: filter_visual_information.py
from ..steps import XsltStep

def get_step():
    return XsltStep(
        files=["text_filterVisualInformation.xsl"],
        name="filter_visual_information",
        pipe_files=True  # Load from package resources
    )
```

#### Python Step Pattern

Python steps wrap custom transformation functions:

```python
# Example: inject_structure_new.py
from ..steps import PythonStep
from lxml import etree as et

def inject_structure_func(root: et.Element, parameters=None):
    """Custom transformation logic"""
    structure_file = parameters['structure_file_path']
    # ... transformation logic ...
    return root

def get_step():
    return PythonStep(
        funct=inject_structure_func,
        name="inject_structure_new"
    )
```

#### Parameter Passing

Parameters flow seamlessly from Pipeline to XSLT or Python:

```python
# Setting parameters in pipeline
step.set_parameter_by_name('note_classes',
    "hc:TextCriticalNote hc:TranscriptionNote")

# In XSLT
<xsl:param name="note_classes" select="''"/>

# In Python function
def my_transform(root, parameters=None):
    note_classes = parameters.get('note_classes', '')
```

### 3. Pre-configured Pipelines

The package provides three main transformation workflows:

#### Semantic Pipeline (`pipeline_library/semantic.py`)
**Purpose**: Generate reading editions (semantic view)

Transformations:
- Removes visual/layout information
- Filters facsimile data
- Moves editorial notes
- Adds IDs to divisions
- Normalizes whitespace
- Validates against schema

**Use case**: Creating clean, readable editions focused on textual content rather than document appearance.

#### SourceDoc Pipeline (`pipeline_library/sourcedoc.py`)
**Purpose**: Generate document-focused editions with layout information

Transformations:
- Preserves initials and visual features
- Connects line breaks with zones
- Handles physical/logical boundaries
- Splits content at page/column breaks
- Converts containers to milestones for overlap handling
- Combines facsimile and transcription

**Use case**: Creating diplomatic editions that preserve document layout and visual features.

#### Synoptic Pipeline (`pipeline_library/synoptic.py`)
**Purpose**: Prepare texts for synoptic comparison

Transformations:
- Removes non-comparative elements
- Converts structure to milestones
- Adds IDs for alignment
- Suppresses first column break
- Prepares for synoptic linking

**Use case**: Preparing multiple witnesses for side-by-side comparison in synoptic editions.

### 4. Step Library

The `step_library/` contains approximately 35 specialized transformation steps:

**Structural transformations:**
- `inject_structure_new`: Reorganizes document structure based on configuration
- `container2milestone`: Converts overlapping elements to milestone pairs
- `resolve_semantic_logical_elements_to_milestones`: Handles TEI overlap problems

**Layout processing:**
- `add_vertical_layout`: Adds vertical reading order to facsimile
- `connect_lb_and_segment`: Links line breaks to text segments
- `move_physical_beginnings`: Repositions physical boundary markers

**Content processing:**
- `initials`: Handles decorated initials
- `whitespaces`: Normalizes whitespace according to schema rules
- `filter_visual_information`: Removes rendition attributes

**Synoptic processing:**
- `append_synoptic_links`: Adds linkGrp elements from synoptic map
- `move_layout_milestones`: Repositions layout markers for synoptic view

**Utilities:**
- `validation`: Schema validation step
- `final_cleanup`: Post-processing cleanup
- `tei2plaintext`: Extracts plain text from TEI

### 5. Supporting Modules

#### Synoptic Analysis (`synopse.py`)

Provides functionality for aligning multiple text witnesses:

- **`create_synopse()`**: Creates abbreviated synoptic map
  - Aligns multiple text witnesses by verse numbers or xml:ids
  - Generates `<link>` elements with targets across witnesses
  - Handles gaps and missing verses

- **`transform_synopse()`**: Expands abbreviated to full synoptic map
  - Converts `<link>` elements to `<linkGrp>` collections
  - Generates bidirectional pointers between witnesses

- **`create_synopse_graphs()`**: Graph-based synoptic alignment
  - Uses NetworkX to build directed graphs for each witness
  - Finds maximal cliques for verse correspondence
  - More robust for complex gap situations

#### CMIF Export (`cmif.py`)

Exports correspondence metadata to CMIF format for the correspSearch portal:

- Extracts correspondence metadata from TEI files
- Validates document types (letters, postcards, etc.)
- Generates CMIF-compliant XML
- Includes Geonames IDs for places
- Maps heiEDITIONS correspondence types to CMIF types

#### Document Combining (`combine.py`)

Merges multiple TEI sourceDoc files into a single document:

- Adds prefixes to xml:ids to avoid collisions
- Merges duplicate surfaces
- Sorts zones by line number
- Maintains references (corresp, target attributes)

#### XML Parsing (`parsers.py`)

Provides specialized XML parsing and transformation utilities:

- **`heiparse()`**: Main XML parsing function with custom entity resolution
- **`apply_xslt()`**: XSLT transformation executor with flexible I/O formats
- **`HeiEditionsParser`**: Custom lxml parser with DTD support
- **`HeiEditionsResolver`**: Custom entity resolver for heiEDITIONS schema

## Dependencies

```
lxml~=5.3.0              # XML processing
saxonche~=12.6.0         # XSLT 3.0 processor
networkx~=3.5            # Graph algorithms for synoptic analysis
requests~=2.32.3         # HTTP for schema fetching
icecream~=2.1.3          # Debugging
colorama~=0.4.6          # Terminal colors
Pygments~=2.18.0         # Syntax highlighting
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install package
pip install .  # From heipy directory
```

## Usage Examples

### Basic Pipeline Usage

```python
from heipy.heipipe.pipeline_library.semantic import SemanticPipe

# Execute semantic pipeline
semantic_pipeline = SemanticPipe()
result = semantic_pipeline.execute(
    input='path/to/input.xml',
    xinclude=False,
    egxml=False,
    output_format='str',
    debug_options=['time', 'serial']
)

# Write result
with open('output.xml', 'w') as f:
    f.write(result)
```

### Custom Pipeline

```python
from heipy.heipipe.steps import Pipeline, XsltStep, PythonStep, DeleteStep
from heipy.heipipe.step_library import filter_visual_information, validation

# Create custom pipeline
custom_pipe = Pipeline(name="my_custom_pipeline")

# Add steps
custom_pipe.add_step(validation.get_step())
custom_pipe.add_step(
    DeleteStep(elements=['tei:fw'], name="delete_form_work")
)
custom_pipe.add_step(filter_visual_information.get_step())

# Add XSLT step with parameters
xslt_step = XsltStep(
    files=['my_transform.xsl'],
    name="custom_transform",
    pipe_files=False  # Use external file
)
xslt_step.set_parameter_by_name('param1', 'value1')
custom_pipe.add_step(xslt_step)

# Execute
result = custom_pipe.execute('input.xml', output_format='str')
```

### Synoptic Map Creation

```python
from heipy.synopse import create_synopse, transform_synopse

# Define witness files
files = [
    'texts/witness_A.xml',
    'texts/witness_B.xml',
    'texts/witness_C.xml'
]

# Sigla mapping configuration
sigla_mapping = {
    'witness_A.xml': {'siglum': 'A', 'synoptic_pre': 'wit.a'},
    'witness_B.xml': {'siglum': 'B', 'synoptic_pre': 'wit.b'},
    'witness_C.xml': {'siglum': 'C', 'synoptic_pre': 'wit.c'}
}

# Create abbreviated synoptic map
create_synopse(
    input=files,
    output='synoptic_map.xml',
    sigla_mapping=sigla_mapping,
    map_criterion='n'  # Align by @n attribute
)

# Transform to expanded format
transform_synopse(input='synoptic_map.xml')
```

### CMIF Export

```python
from heipy.cmif import create_cmif_export

files = [
    'letters/letter_001.xml',
    'letters/letter_002.xml'
]

create_cmif_export(
    files=files,
    project_name='MyEdition',
    output_path='export/'
)
# Creates: export/CMIF_Export.xml
```

### Command-Line Interface

```bash
# Run all pipelines (semantic, synoptic, sourcedoc)
python script.py file1.xml file2.xml

# Run specific pipeline
python script.py --semantic file.xml
python script.py -sem file.xml

# Debug options
python script.py --debug time serial file.xml  # Show timing and serialize steps
python script.py --debug file.xml              # Enable all debug options
```

## Key Features

1. **Modular Pipeline Architecture**: XProc-like system allowing flexible composition of transformation steps
2. **Performance Optimization**: Smart batching of XSLT transformations to minimize serialization overhead
3. **XSLT 3.0 Support**: Leverages modern XSLT features via SaxonHE
4. **Mixed Python/XSLT**: Combines declarative XSLT with imperative Python for complex transformations
5. **Scholarly Focus**: Built-in support for TEI overlap problems, synoptic editions, and correspondence metadata
6. **Integration Ready**: Scripts for eXist-db upload and DTS API generation
7. **Extensible**: Easy to add custom steps and pipelines for project-specific needs

## Use Cases

heipy is designed for institutional digital edition projects requiring:

- **Standardized Workflows**: Consistent, reproducible transformation pipelines
- **Multiple Output Formats**: Generate semantic, diplomatic, and synoptic editions from the same source
- **Complex TEI Processing**: Handle TEI overlap, milestone conversion, and structural transformations
- **Synoptic Editions**: Align and compare multiple text witnesses
- **Correspondence Projects**: Export to CMIF for integration with correspSearch
- **Custom Transformations**: Flexibility to add project-specific processing steps

## Architecture Strengths

- **Separation of Concerns**: Clear separation between pipeline structure (Python) and transformation logic (XSLT/Python)
- **Reusability**: Steps can be shared across multiple pipelines
- **Performance**: Optimized execution minimizes XML serialization overhead
- **Testability**: Modular steps can be tested independently
- **Maintainability**: XSLT and Python code separated into focused, single-purpose files
- **Flexibility**: Mix declarative (XSLT) and imperative (Python) approaches as needed

## Testing Infrastructure

### Test Organization

The test suite is organized by functional area:

**Parser Tests** (`tests/parsers/test_parser_io.py`)
- Entity preservation in heiEDITIONS documents
- DOCTYPE declaration handling
- Roundtrip load/write verification
- Prologue normalization for semantic comparison

**Test Fixtures** (`tests/fixtures/`)
- `minimal/basic_tei.xml`: Simple TEI document for basic tests
- `minimal/tei_with_entities.xml`: TEI with heiEDITIONS entities (`&bar;`, `&us;`, `&er;`)

**Pytest Configuration** (`tests/conftest.py`)
- `hei_parser`: HeiEditionsParser fixture
- `basic_tei`: Basic TEI document fixture
- `tei_with_entities`: TEI with entities fixture
- Path fixtures for accessing test data

### Key Testing Utilities

**normalize_prologue()** (`test_parser_io.py`)
- Separates XML prologue from content
- Normalizes quote style and whitespace
- Enables semantic comparison while ignoring formatting differences

**compare_elements()** (`test_parser_io.py`)
- Recursive element comparison
- Checks tags, attributes, text, tail, and children
- Used for strict content verification

## Additional Resources

- **Tutorial**: See `tutorial.ipynb` for interactive examples
- **README**: Comprehensive documentation in the repository root
- **Tests**: Example usage patterns in the `tests/` directory
- **Test Strategy**: See `knowledge/FIXTURE_STRATEGY.md` for testing approach
- **XSLT Files**: Well-documented transformations in `src/heipy/heipipe/xslt/`

## Summary

heipy is a sophisticated, production-ready framework for digital scholarly editing built on proven technologies (lxml, SaxonHE) with a clean architecture that balances flexibility, performance, and maintainability. Its pipeline system provides a modern, Python-based alternative to XProc while maintaining the benefits of declarative XML transformation through XSLT 3.0.
