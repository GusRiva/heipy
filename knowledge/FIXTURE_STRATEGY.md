# Comprehensive Test Fixture Strategy for heipy

## Overview

This document outlines the fixture organization for testing heipy's pipeline transformations. The strategy balances:
- **Step-specific testing** - Isolated testing of individual transformations
- **Multi-purpose fixtures** - Realistic documents for integration testing
- **Scalability** - Easy to add new fixtures as needs emerge

---

## Fixture Directory Structure

```
tests/fixtures/
├── README.md                           # Overview of fixture categories
├── __init__.py                         # Fixture utilities
│
├── minimal/                            # ✅ EXISTS: Basic TEI structures
│   ├── basic_tei.xml                   # ✅ Simple TEI document
│   └── tei_with_entities.xml           # ✅ TEI with heiEDITIONS entities
│
├── step_library/                       # NEW: Fixtures for step_library steps
│   ├── README.md                       # Overview of all step_library fixtures
│   ├── [step_name_1]/                 # One directory per step
│   │   ├── README.md                   # What this step does, fixtures explain
│   │   ├── input_*.xml                 # Input test files
│   │   ├── expected_*.xml              # Expected outputs
│   │   └── config_*.xml                # Optional: step configuration files
│   ├── [step_name_2]/
│   └── ... (35 total steps)
│
├── intermediate/                       # NEW: Medium complexity documents
│   ├── README.md
│   ├── abbrev_manuscript.xml           # Abbreviations and expansions
│   ├── corrections_sample.xml          # Scribal corrections (add/del/subst)
│   ├── multicolumn_page.xml            # Multi-column layout with zones
│   ├── marginal_content.xml            # Main text + marginal annotations
│   └── damaged_text.xml                # Gaps, faded, illegible sections
│
├── advanced/                           # NEW: Complex production-like documents
│   ├── README.md
│   ├── damaged_fragment.xml            # Extensive damage, multiple gap types
│   ├── layout_complex.xml              # Multi-column, zones, run-over lines
│   ├── visual_features.xml             # Initials, highlighting, decorations
│   └── editorial_apparatus.xml         # Full editorial apparatus
│
└── integration/                        # NEW: End-to-end pipeline scenarios
    ├── README.md
    ├── simple_pipeline/
    │   ├── README.md                   # Describes pipeline scenario
    │   ├── source.xml                  # Input document
    │   ├── config.json                 # Pipeline configuration
    │   └── expected_output.xml         # Final expected result
    ├── diplomatic_to_normalized/
    ├── sourcedoc_generation/
    └── comparative_edition/
```

---

## Fixture Categories Explained

### 1. Minimal Fixtures (✅ Implemented)

**Purpose**: Basic TEI structures for unit testing core functionality and parser I/O operations

**Current Fixtures**:
1. **basic_tei.xml** - Simple TEI document without entities
   - Minimal valid TEI structure
   - teiHeader with required elements
   - Simple body with paragraphs
   - Used for basic roundtrip tests

2. **tei_with_entities.xml** - TEI with heiEDITIONS schema and entities
   - Full heiEDITIONS schema declarations (xml-model, DOCTYPE)
   - Contains common entities: `&bar;`, `&us;`, `&er;`
   - Used for entity preservation tests
   - Critical for testing parser I/O with entities

**Use Cases**:
- ✅ Parser I/O testing (tests/parsers/test_parser_io.py)
- ✅ Entity preservation verification
- ✅ DOCTYPE declaration handling
- ✅ Roundtrip load/write testing
- Testing BaseStep functionality (parameters, serialization, indexing)
- Testing step class initialization

**Tests Using These Fixtures**:
- `tests/parsers/test_parser_io.py`: Complete parser I/O test suite
  - Basic TEI roundtrip
  - Entity preservation in serialization
  - Prologue normalization
  - Content comparison

---

### 2. Step Library Fixtures

**Purpose**: Test the 35 predefined steps in `src/heipy/heipipe/step_library/`

**Characteristics**:
- One subdirectory per step_library function
- Input/expected output pairs
- Targeted at specific transformation behavior
- Small to medium size (50-200 lines)
- Configuration files where steps require them

**Directory Template**:
```
step_library/[step_name]/
├── README.md                 # What this step does, what fixtures test
├── input_basic.xml           # Simplest working case
├── expected_basic.xml        # Verified expected output (rename from auto_expected_*)
├── auto_expected_basic.xml   # Auto-generated (pending review, git-ignored)
├── config_basic.json         # Optional: parameters for basic variant
├── input_edge_*.xml          # Edge cases
├── expected_edge_*.xml       # Verified expected outputs
├── auto_expected_edge_*.xml  # Auto-generated (pending review, git-ignored)
├── config_edge_*.json        # Optional: parameters for edge case variants
└── config.json               # Optional: default parameters for all variants
```

**Note**: `auto_expected_*.xml` files are temporary outputs from `generate_expected.py` and should be git-ignored. Only commit `expected_*.xml` files after manual verification.

**Config File Format** (JSON):
```json
{
  "param_name": "param_value",
  "note_classes": "hc:TextCriticalNote hc:Comment"
}
```

**README Template** for each step:
```markdown
# [Step Name]

## Purpose
[One paragraph: what this step does]

## Source
`src/heipy/heipipe/step_library/[filename].py`

## Type
- XsltStep / PythonStep
- XSLT files: [list] OR Python function: [name]

## Parameters
[List any required parameters]

## Fixtures

### input_basic.xml → expected_basic.xml
Tests: [brief description]

### input_edge_*.xml → expected_edge_*.xml
Tests: [brief description]
```

**Use Cases**:
- Unit tests for step_library functions
- Regression testing
- Documentation via examples
- Used by tests in `tests/step/`

**Implementation Approach**:
1. Create input fixture demonstrating feature
2. Run step manually to generate expected output
3. Verify output is correct
4. Save as `expected_*.xml`
5. Write test comparing actual vs expected

---

### 3. Intermediate Fixtures

**Purpose**: Realistic but manageable documents for testing multiple features

**Characteristics**:
- Medium size (100-300 lines)
- Multiple features per document
- Based on actual TEI patterns from real manuscripts
- Self-contained (don't require external config)
- Schema-valid

**Planned Fixtures**:

| File | Features Tested |
|------|----------------|
| `abbrev_manuscript.xml` | Abbreviations (`<choice>`, `<am>`, `<ex>`), expansions, complex segments |
| `corrections_sample.xml` | Add/del/subst, various renditions, multi-element corrections |
| `multicolumn_page.xml` | Facsimile zones, multi-column layout, zone transitions |
| `marginal_content.xml` | Main text + marginal notes, zone milestones |
| `damaged_text.xml` | Gaps (lost, faded, illegible, cut-off), damage within words |

**Use Cases**:
- Testing interactions between features
- Integration testing with multiple steps
- Realistic transformation scenarios
- Used by tests in `tests/integration/`

---

### 4. Advanced Fixtures (NEW)

**Purpose**: Complex production-like documents approaching real manuscript complexity

**Characteristics**:
- Large size (300-1000 lines)
- Many features combined
- Closely based on actual manuscripts (Gregoire, Hartmann, etc.)
- May include edge cases and unusual combinations
- Schema-valid

**Planned Fixtures**:

| File | Features Tested |
|------|----------------|
| `damaged_fragment.xml` | Extensive damage, partial text, multiple gap types, irregular structure |
| `layout_complex.xml` | Multi-column, horizontal zones, run-over lines, interlinear additions |
| `visual_features.xml` | Initials (various types), highlighting, cadels, section markers, decorations |
| `editorial_apparatus.xml` | Full apparatus: orig/reg, supplied text, editorial notes, corrections |

**Use Cases**:
- Stress testing transformations
- Real-world scenario validation
- Performance testing
- End-to-end pipeline testing
- Used by tests in `tests/integration/`

---

### 5. Integration Fixtures

**Purpose**: Complete pipeline scenarios from input to final output

**Characteristics**:
- Full documents with supporting files
- Pipeline configuration included
- Multiple transformation steps
- Demonstrates real editorial workflows

**Directory Template**:
```
integration/[scenario_name]/
├── README.md              # Describes the editorial scenario
├── source.xml             # Input document (diplomatic transcription)
├── config.json            # Pipeline configuration
├── intermediate_*.xml     # Optional: intermediate step outputs
└── expected_output.xml    # Final expected result
```

**Planned Scenarios**:

#### `simple_pipeline/`
- **Input**: Clean diplomatic transcription
- **Steps**: Basic transformations (split at boundaries, combine facsimile, add structure)
- **Output**: Well-formed source document
- **Tests**: Standard editorial pipeline

#### `diplomatic_to_normalized/`
- **Input**: Diplomatic with orig/reg choices
- **Steps**: Regularization, choice resolution, cleanup
- **Output**: Normalized edition text
- **Tests**: Editorial regularization pipeline

#### `sourcedoc_generation/`
- **Input**: Transcription with facsimile
- **Steps**: Split, combine, zone management
- **Output**: Complete source document with zones
- **Tests**: Source document generation pipeline

#### `comparative_edition/`
- **Input**: Two witnesses of same text
- **Steps**: Synchronization, alignment, comparison
- **Output**: Aligned witnesses with variants marked
- **Tests**: Multi-witness handling

**README Template** for scenarios:
```markdown
# [Scenario Name]

## Editorial Context
[What kind of editorial work this represents]

## Input
[Description of source.xml]

## Pipeline Steps
1. Step 1: [purpose]
2. Step 2: [purpose]
...

## Output
[Description of expected_output.xml]

## Configuration
[Explain config.json parameters]

## Running
```bash
pytest tests/integration/test_[scenario_name].py
```
```

**Use Cases**:
- Full pipeline validation
- Real-world workflow testing
- Performance benchmarking
- User documentation (examples of complete workflows)

---

## Fixture Naming Conventions

### General Pattern
```
[purpose]_[feature]_[variant].xml
```

### Examples
- `input_basic.xml` / `expected_basic.xml`
- `input_abbrev_complex.xml` / `expected_abbrev_complex.xml`
- `damaged_fragment_cutoff.xml`
- `multicolumn_page_marginal.xml`

### Special Prefixes
- `input_` - Input to a transformation
- `expected_` - Manually verified expected output (committed to git)
- `auto_expected_` - Auto-generated output pending review (git-ignored, temporary)
- `config_` - Configuration file (JSON format containing step parameters)
- `structure_` - Structure definition file (for inject_structure step)

### Config File Naming
- `config.json` - Default configuration for all variants
- `config_basic.json` - Configuration for the basic variant
- `config_{variant}.json` - Configuration for specific variant (e.g., `config_edge_case.json`)

### Auto-Generated Files Workflow
1. **Generate**: `generate_expected.py` creates `auto_expected_*.xml` files
2. **Review**: Manually verify each `auto_expected_*.xml` file is correct
3. **Rename**: `mv auto_expected_*.xml expected_*.xml` when verified
4. **Git**: Only commit `expected_*.xml` files; `auto_expected_*.xml` should be git-ignored

---

## Fixture Creation Workflow

### For step_library Fixtures:

1. **Understand the step**
   - Read the source file
   - Identify what transformation it performs
   - Note any parameters or configuration needed

2. **Create minimal input**
   - Start with simplest case that demonstrates the transformation
   - Ensure schema-valid TEI
   - Create the fixture directory: `tests/fixtures/step_library/[step_name]/`
   - Save as `input_basic.xml` (or `input_[variant].xml` for specific cases)

3. **Generate expected output** using the CLI tool
   - Use the `generate_expected.py` helper script to automatically generate expected outputs
   - See "Automated Fixture Generation Tool" section below for detailed usage
   - **Verify correctness** (this is critical!) - Always manually review the generated output
   - The tool executes the actual transformation, so you must verify it produces correct results

4. **Create edge cases**
   - Identify boundary conditions
   - Create additional input/expected pairs (e.g., `input_edge_case.xml`)
   - Run `generate_expected.py` with `--variant edge_case` or `--all` to generate outputs

5. **Document**
   - Write README explaining what each fixture tests
   - Note any special requirements

### For intermediate/advanced Fixtures:

1. **Base on real manuscripts**
   - Use actual patterns from Gregoire, Hartmann, Max und Moritz
   - Refer to `knowledge/DATA_ANALYSIS.md` for structures

2. **Combine features realistically**
   - Don't artificially stuff every feature in one document
   - Group related features together

3. **Validate**
   - Ensure schema-valid
   - Test with actual transformations
   - Verify output makes sense

4. **Document**
   - README explaining features included
   - Note which tests use the fixture

---

## Automated Fixture Generation Tool

### Overview

The `tests/helpers/generate_expected.py` script automates the process of creating `expected_*.xml` files by running actual step transformations on `input_*.xml` files. This eliminates manual execution and ensures consistency.

**Location**: `tests/helpers/generate_expected.py`

**Important**: This tool executes the actual transformation pipeline. Always verify the generated output is correct before using it in tests!

### Configuration Files (Preferred Method)

**The tool automatically loads parameters from JSON config files.** This is the recommended approach for steps that require parameters.

**Config file priority** (first found wins):
1. `config_{variant}.json` - Variant-specific config (e.g., `config_edge_case.json`)
2. `config_basic.json` - Basic variant config
3. `config.json` - Default config for all variants

**Config file format:**
```json
{
  "param_name": "param_value",
  "note_classes": "hc:TextCriticalNote hc:Comment"
}
```

### Basic Usage

#### Generate expected output for a single step (basic variant)
```bash
python tests/helpers/generate_expected.py <step_name>
```

Example:
```bash
python tests/helpers/generate_expected.py combine_facsimile_and_text_to_sourcedoc
```

This will:
1. Look for `tests/fixtures/step_library/combine_facsimile_and_text_to_sourcedoc/input_basic.xml`
2. Automatically load parameters from `config_basic.json` or `config.json` if present
3. Execute the transformation with those parameters
4. **Save the result as `auto_expected_basic.xml`** (NOT `expected_basic.xml`)
5. You must manually review and rename: `auto_expected_basic.xml` → `expected_basic.xml`

### Advanced Usage

#### Generate for a specific variant
```bash
python tests/helpers/generate_expected.py <step_name> --variant <variant_name>
```

Example:
```bash
python tests/helpers/generate_expected.py mark_note_as_editorial --variant two_classes
```

This processes:
- `input_two_classes.xml` → **`auto_expected_two_classes.xml`**
- Automatically loads parameters from `config_two_classes.json` if present
- You must review and rename to `expected_two_classes.xml` when verified

#### Generate for all input files in a step directory
```bash
python tests/helpers/generate_expected.py <step_name> --all
```

Example:
```bash
python tests/helpers/generate_expected.py combine_facsimile_and_text_to_sourcedoc --all
```

This will:
- Process all `input_*.xml` files and generate corresponding **`auto_expected_*.xml`** files
- **Automatically load matching config files** for each variant (e.g., `config_basic.json` for `input_basic.xml`, `config_edge_case.json` for `input_edge_case.xml`)
- You must review each file and rename when verified

#### With command-line parameters (overrides config files)
```bash
python tests/helpers/generate_expected.py <step_name> --params "param1=value1 param2=value2"
```

Example:
```bash
python tests/helpers/generate_expected.py mark_note_as_editorial --params "note_classes='hc:TextCriticalNote hc:Comment'"
```

**Note**: Command-line `--params` override any config files. Use this for quick testing, but prefer config files for permanent fixtures.

### Workflow Example

**Complete workflow for creating a new step fixture:**

1. **Create the directory structure:**
```bash
mkdir -p tests/fixtures/step_library/my_new_step
```

2. **Create the input fixture:**
```bash
# Manually create input_basic.xml with test data
nano tests/fixtures/step_library/my_new_step/input_basic.xml
```

3. **Create config file if step requires parameters:**
```bash
# Create config_basic.json with parameters
cat > tests/fixtures/step_library/my_new_step/config_basic.json << 'EOF'
{
  "param_name": "param_value",
  "note_classes": "hc:TextCriticalNote hc:Comment"
}
EOF
```

4. **Generate the auto-expected output:**
```bash
# Automatically uses config_basic.json if present
# Creates auto_expected_basic.xml
python tests/helpers/generate_expected.py my_new_step
```

5. **Verify and rename:**
```bash
# Manually review the generated file
cat tests/fixtures/step_library/my_new_step/auto_expected_basic.xml

# If correct, rename to expected_basic.xml
mv tests/fixtures/step_library/my_new_step/auto_expected_basic.xml \
   tests/fixtures/step_library/my_new_step/expected_basic.xml
```

6. **Create additional variants (optional):**
```bash
# Create edge case input
nano tests/fixtures/step_library/my_new_step/input_edge_case.xml

# Create config for edge case variant
cat > tests/fixtures/step_library/my_new_step/config_edge_case.json << 'EOF'
{
  "param_name": "different_value"
}
EOF

# Generate auto-expected output for edge case (uses config_edge_case.json)
python tests/helpers/generate_expected.py my_new_step --variant edge_case

# Review and rename
mv tests/fixtures/step_library/my_new_step/auto_expected_edge_case.xml \
   tests/fixtures/step_library/my_new_step/expected_edge_case.xml
```

7. **Generate all at once:**
```bash
# After creating multiple input_*.xml and config_*.json files,
# generate all auto_expected outputs (each with matching config)
python tests/helpers/generate_expected.py my_new_step --all

# Review all files, then rename them when verified
for f in tests/fixtures/step_library/my_new_step/auto_expected_*.xml; do
  # Review each file first!
  cat "$f"
  # If correct, rename (remove 'auto_' prefix)
  mv "$f" "${f/auto_expected/expected}"
done
```

### Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `step_name` | (positional) | Name of the step (must match directory name in `tests/fixtures/step_library/`) |
| `--variant` | `-v` | Variant name (e.g., 'edge_case' for `input_edge_case.xml`). Loads `config_{variant}.json` if present. |
| `--all` | `-a` | Generate expected outputs for all `input_*.xml` files. Automatically loads matching `config_*.json` for each. |
| `--params` | `-p` | Step parameters as `'key1=val1 key2=val2'`. **Overrides config files**. |

### How It Works

The script:
1. Loads the step from `src/heipy/heipipe/step_library/<step_name>.py`
2. **Loads parameters from config file** (if present and `--params` not used):
   - For specific variant: `config_{variant}.json`
   - For basic variant: `config_basic.json` or `config.json`
   - When using `--all`: loads matching config for each input file
3. Applies parameters to the step
4. Creates a Pipeline containing just that step
5. Executes the pipeline on the input file
6. **Saves the output with pretty-printing as `auto_expected_*.xml`** (NOT `expected_*.xml`)

### Important Notes

⚠️ **Safety: Auto-generated files require manual verification!**
- The tool generates `auto_expected_*.xml` files to prevent accidental overwriting
- You MUST manually review each file before renaming to `expected_*.xml`
- If the step has a bug, the auto-generated output will be wrong
- Only commit `expected_*.xml` files after verification
- `auto_expected_*.xml` files should be git-ignored

✅ **Best practices:**
- **Use config files** (`config_*.json`) for steps that need parameters - it's cleaner and more maintainable than command-line params
- Start with simple `input_basic.xml` that clearly demonstrates the transformation
- Create corresponding `config_basic.json` if the step needs parameters
- **Always review `auto_expected_*.xml` files** before renaming to `expected_*.xml`
- Use `--all` to regenerate all auto_expected files after fixing a bug in the step
- Keep config files version-controlled alongside fixtures
- Add `auto_expected_*.xml` to `.gitignore` to prevent accidental commits

### Troubleshooting

**Error: Step directory not found**
- Make sure the directory exists: `tests/fixtures/step_library/<step_name>/`
- Check that the step name matches the directory name exactly

**Error: No input files found**
- Ensure at least one `input*.xml` file exists in the step directory
- For basic variant, create `input_basic.xml` or `input.xml`

**Error: Could not import step**
- Verify the step exists in `src/heipy/heipipe/step_library/<step_name>.py`
- Check that the step module has a `get_step()` function

**Error during transformation**
- Review the error message and traceback
- The input XML might be invalid or incompatible with the step
- Check if the step requires specific parameters (use `--params`)

---

## Implementation Priority

### Phase 1: Foundation (✅ COMPLETED)
- ✅ Minimal fixtures created
  - ✅ basic_tei.xml
  - ✅ tei_with_entities.xml
- ✅ Parser I/O tests implemented (tests/parsers/test_parser_io.py)
  - ✅ Entity preservation testing
  - ✅ Roundtrip testing with prologue normalization
  - ✅ HeiEditionsParser functionality tests
- ✅ Fixture helpers
  - ✅ normalize_prologue() function
  - ✅ compare_elements() function
  - ✅ conftest.py fixtures (hei_parser, basic_tei, tei_with_entities)
  - ✅ StepFixtureLoader class (tests/helpers/fixture_loader.py)
  - ✅ FixtureGenerator class (tests/helpers/fixture_loader.py)
  - ✅ generate_expected.py CLI tool (tests/helpers/generate_expected.py)

### Phase 2: Core Step Library (Immediate Priority)
**Goal**: Test the most critical step_library transformations

**Tier 1 Steps** (5 most important):
- Steps that perform fundamental transformations
- Used in most pipelines
- Complex XSLT or critical Python functions
- ~3 fixtures each = ~15 fixtures

**Approach**:
- Pick one step
- Create fixtures
- Generate expected outputs
- Write tests
- Move to next step

### Phase 3: Intermediate Documents
**Goal**: Provide realistic multi-feature test documents

- Create 5 intermediate fixtures
- Base on real manuscript patterns
- Use in integration tests

### Phase 4: Remaining Step Library
**Goal**: Complete step_library coverage

**Tier 2-5 Steps** (30 remaining):
- Less critical or simpler transformations
- ~2 fixtures each = ~60 fixtures

### Phase 5: Advanced & Integration
**Goal**: Full pipeline testing

- Create 4 advanced fixtures
- Create 4 integration scenarios
- Performance testing

---

## Testing Strategy by Fixture Type

### Minimal Fixtures
```python
# tests/unit/test_base_step.py
def test_init_with_name():
    step = XsltStep(files=[], name="test_step")
    assert step.get_name() == "test_step"
```
**Focus**: Class behavior, not transformation logic

### Step Library Fixtures
```python
# tests/steps/test_filter_visual_information.py
from tests.helpers.xml_compare import xml_equal

def test_basic_filtering(fixture_loader):
    """Test basic visual information filtering."""
    from heipy.heipipe.step_library import filter_visual_information

    step = filter_visual_information.get_step()

    # Load fixtures (returns ElementTrees)
    input_tree = fixture_loader.load('filter_visual_information/input_basic.xml')
    expected_tree = fixture_loader.load('filter_visual_information/expected_basic.xml')

    # Convert to string and execute
    input_string = fixture_loader.tree_to_string(input_tree)
    result_string = step.execute(input_string)

    # Compare
    assert xml_equal(result_string, expected_tree)
```
**Focus**: Specific transformation behavior

### Canonical Step Test Pattern

Use this pattern for all step_library tests:

```python
# tests/steps/test_[step_name].py
from tests.helpers.xml_compare import xml_equal

def test_basic_case(fixture_loader):
    """Test [step_name] with basic scenario."""
    from heipy.heipipe.step_library import [step_name]

    # 1. Get step instance
    step = [step_name].get_step()

    # 2. Set parameters if needed
    step.add_parameter('param_name', 'param_value')

    # 3. Load fixtures (returns ElementTrees)
    input_tree = fixture_loader.load('[step_name]/input_basic.xml')
    expected_tree = fixture_loader.load('[step_name]/expected_basic.xml')

    # 4. Convert input tree to string (steps accept strings)
    input_string = fixture_loader.tree_to_string(input_tree)

    # 5. Execute step (returns string)
    result_string = step.execute(input_string)

    # 6. Compare using xml_equal (handles string/tree conversion internally)
    assert xml_equal(result_string, expected_tree)

# Alternative: Using load_step_pair for input/expected pairs
def test_with_structured_api(fixture_loader):
    """Test using structured fixture API."""
    from heipy.heipipe.step_library import [step_name]

    step = [step_name].get_step()
    step.add_parameter('param_name', 'param_value')

    # Load as pair (returns tuple of trees)
    input_tree, expected_tree = fixture_loader.load_step_pair('[step_name]', variant='')

    input_string = fixture_loader.tree_to_string(input_tree)
    result_string = step.execute(input_string)

    assert xml_equal(result_string, expected_tree)

# Parametrized test for multiple variants
import pytest

@pytest.mark.parametrize('variant', ['basic', 'two_classes', 'nested_notes'])
def test_multiple_variants(fixture_loader, variant):
    """Test multiple scenarios with parametrization."""
    from heipy.heipipe.step_library import [step_name]

    step = [step_name].get_step()
    # Configure step based on variant if needed

    input_tree, expected_tree = fixture_loader.load_step_pair('[step_name]', variant=variant)
    input_string = fixture_loader.tree_to_string(input_tree)
    result_string = step.execute(input_string)

    assert xml_equal(result_string, expected_tree)
```

**Key Points**:
1. **Import xml_equal directly** from `tests.helpers.xml_compare` at module level
2. **fixture_loader** is a pytest fixture - receive as parameter
3. **Load as trees**: Use `loader.load()` or `load_step_pair()` - returns ElementTree
4. **Convert to string**: Use `loader.tree_to_string()` before passing to step
5. **Step returns string**: `execute()` always returns XML string
6. **Compare with xml_equal**: Handles string/tree conversion, preserves whitespace

### Intermediate Fixtures
```python
# tests/integration/test_multi_feature.py
def test_abbrev_manuscript_processing(fixture_loader):
    doc = fixture_loader.load('intermediate/abbrev_manuscript.xml')

    # Test multiple steps on same document
    result = step1.execute(doc)
    result = step2.execute(result)

    # Verify features handled correctly
    assert check_abbreviations_expanded(result)
    assert check_structure_preserved(result)
```
**Focus**: Feature interaction, realistic scenarios

### Integration Fixtures
```python
# tests/integration/test_simple_pipeline.py
def test_simple_pipeline_complete(fixture_loader):
    source = fixture_loader.load('integration/simple_pipeline/source.xml')
    config = fixture_loader.load_json('integration/simple_pipeline/config.json')
    expected = fixture_loader.load('integration/simple_pipeline/expected_output.xml')

    pipeline = Pipeline.from_config(config)
    result = pipeline.execute(source)

    assert xml_equal(result, expected)
```
**Focus**: End-to-end workflows

---

## Benefits of This Strategy

### 1. **Clear Separation of Concerns**
- Unit tests use minimal fixtures
- Step-specific tests use step_library fixtures
- Integration tests use intermediate/advanced fixtures
- Pipeline tests use integration scenarios

### 2. **Scalability**
- Easy to add new step_library fixtures as steps are tested
- Intermediate fixtures can be reused across tests
- Integration scenarios document real workflows

### 3. **Maintainability**
- Each fixture has clear purpose
- READMEs document what's being tested
- Input/expected pairs make test intent obvious

### 4. **Documentation Value**
- Fixtures serve as usage examples
- Integration scenarios show real editorial workflows
- Clear patterns for contributors

### 5. **Performance**
- Small fixtures (minimal, step_library) run fast
- Large fixtures (advanced, integration) used selectively
- Tests can run in parallel

---

## Next Steps

1. **Create fixture directory structure**
   ```bash
   mkdir -p tests/fixtures/{step,intermediate,advanced,integration}
   ```

2. **Add README files** to each category directory explaining purpose

3. **Identify Tier 1 steps** - Pick 5 most critical step_library functions

4. **Start with one step**:
   - Create `step/[step_name]/` directory
   - Create input_basic.xml
   - Run transformation manually
   - Save as expected_basic.xml
   - Write test
   - Document in README

5. **Iterate** through remaining Tier 1 steps

6. **Create intermediate fixtures** based on DATA_ANALYSIS.md patterns

7. **Expand to remaining tiers** as needed

---

## StepFixtureLoader API Reference

### Overview
The `StepFixtureLoader` provides both **structured** and **flexible** APIs for loading test fixtures.

### Hybrid API Design

#### Structured Methods (For Standard Patterns)
Use these when following the standard `input_*.xml` / `expected_*.xml` pattern:

```python
# Load single fixture
input_tree = loader.load_step_fixture('step_name', 'input_basic')

# Load input/expected pair
input_tree, expected_tree = loader.load_step_pair('step_name')
input_tree, expected_tree = loader.load_step_pair('step_name', variant='edge_case')

# Load configuration
config = loader.load_step_config('step_name', 'structure', format='xml')
```

#### Flexible Method (For Ad-hoc Loading)
Use `load()` when you need direct path access:

```python
# Load any fixture by relative path (returns ElementTree)
tree = loader.load('step_name/input_basic.xml')
tree = loader.load('mark_note_as_editorial/input_two_classes.xml')

# Load as string directly
xml_str = loader.load('step_name/input_basic.xml', return_string=True)
```

#### Helper Method
```python
# Convert tree to string for step.execute()
xml_string = loader.tree_to_string(tree)
```

### When to Use Which API

**Use Structured API** when:
- Following standard naming convention (`input_*.xml`, `expected_*.xml`)
- Loading input/expected pairs together
- Want automatic variant handling
- Building reusable test patterns

**Use Flexible API** when:
- Need to load fixtures with non-standard names
- Loading single files ad-hoc
- Prototyping new test patterns
- Direct path is clearer than step_name + fixture_name

### Complete Example

```python
from tests.helpers.xml_compare import xml_equal

def test_mark_note_as_editorial_two_classes(fixture_loader):
    """Test marking notes as editorial with two note classes."""
    from heipy.heipipe.step_library import mark_note_as_editorial

    # Initialize step
    step = mark_note_as_editorial.get_step()
    step.add_parameter('note_classes', 'hc:TextCriticalNote hc:Comment')

    # Option 1: Flexible API
    input_tree = fixture_loader.load('mark_note_as_editorial/input_two_classes.xml')
    expected_tree = fixture_loader.load('mark_note_as_editorial/expected_two_classes.xml')

    # Option 2: Structured API (equivalent)
    # input_tree, expected_tree = fixture_loader.load_step_pair('mark_note_as_editorial', variant='two_classes')

    # Convert and execute
    input_string = fixture_loader.tree_to_string(input_tree)
    result_string = step.execute(input_string)

    # Assert equality
    assert xml_equal(result_string, expected_tree)
```

### Type Conversion Cheat Sheet

```python
from lxml import etree as et
from heipy.parsers import HeiEditionsParser

# Load as tree (default)
tree = fixture_loader.load('step_name/input.xml')
# tree is et._ElementTree

# Tree → String
xml_string = fixture_loader.tree_to_string(tree)
# OR
xml_string = et.tostring(tree.getroot(), encoding='unicode')

# Step execution flow
input_string = fixture_loader.tree_to_string(input_tree)  # Tree → String
result_string = step.execute(input_string)                 # String → String
assert xml_equal(result_string, expected_tree)             # xml_equal handles conversion
```

### What Types Do Tools Accept?

| Tool/Method | Accepts | Returns |
|------------|---------|---------|
| `step.execute()` | `str` (XML string) | `str` (XML string) |
| `fixture_loader.load()` | `str` (path) | `et._ElementTree` |
| `fixture_loader.load_step_pair()` | `str` (step name) | `(et._ElementTree, et._ElementTree)` |
| `fixture_loader.tree_to_string()` | `et._ElementTree` or `et._Element` | `str` |
| `xml_equal()` | `str` or `et._ElementTree` or `et._Element` | `bool` |

---

## Common Pitfalls and Solutions

### Pitfall 1: Wrong Import Pattern
**Wrong**:
```python
# Trying to use xml_equal as a fixture parameter (no longer exists)
def test_something(fixture_loader, xml_equal):  # xml_equal fixture removed!
    assert xml_equal(...)
```

**Right**:
```python
# Import directly from xml_compare module
from tests.helpers.xml_compare import xml_equal

def test_something(fixture_loader):
    assert xml_equal(...)
```

### Pitfall 2: Type Mismatch
**Wrong**:
```python
tree = fixture_loader.load('path/to/file.xml')
result = step.execute(tree)  # step.execute() expects STRING not TREE!
```

**Right**:
```python
tree = fixture_loader.load('path/to/file.xml')
xml_string = fixture_loader.tree_to_string(tree)
result = step.execute(xml_string)  # Now it's a string
```

### Pitfall 3: Wrong Path
**Wrong**:
```python
# step_fixtures_dir already points to step_library/
tree = fixture_loader.load('step_library/step_name/input.xml')  # REDUNDANT!
```

**Right**:
```python
tree = fixture_loader.load('step_name/input.xml')  # Relative to step_library/
```

---

## Appendix: Fixture Statistics

### Current State
- ✅ Minimal: 5 fixtures
- ✅ Step library: 2 fixtures (1 step covered: mark_note_as_editorial, 34 steps remaining)
  - mark_note_as_editorial: input_two_classes.xml, expected_two_classes.xml
- ❌ Intermediate: 0 fixtures (5 planned)
- ❌ Advanced: 0 fixtures (4 planned)
- ❌ Integration: 0 fixtures (4 scenarios planned)

### Target State (Phase 2-4)
- Minimal: 5 fixtures (no change)
- Step library: ~75 fixtures (15 Tier 1 + 60 Tier 2-5)
- Intermediate: 5 fixtures
- Advanced: 4 fixtures
- Integration: 4 scenarios (multiple files each)

**Total**: ~90-100 new fixtures to create

### Realistic Approach
Start with **Tier 1 (15 fixtures)** and **Intermediate (5 fixtures)** = 20 fixtures
This provides solid foundation for most common transformations and integration testing.
