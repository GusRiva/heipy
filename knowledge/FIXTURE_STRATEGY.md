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
├── README.md              # What this step does, what fixtures test
├── input_basic.xml        # Simplest working case
├── expected_basic.xml     # Expected output
├── input_edge_*.xml       # Edge cases
├── expected_edge_*.xml    # Expected edge case outputs
└── config_*.xml           # If step needs configuration
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
- Used by tests in `tests/step_library/`

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
- `expected_` - Expected output
- `config_` - Configuration file
- `structure_` - Structure definition file (for inject_structure)

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

3. **Generate expected output**
   - Run the step manually: `step.execute(input_xml)`
   - Save output
   - **Verify correctness** (this is critical!)

4. **Create edge cases**
   - Identify boundary conditions
   - Create additional input/expected pairs

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
# tests/step_library/test_filter_visual_information.py
def test_basic_filtering(fixture_loader):
    from heipy.heipipe.step_library import filter_visual_information

    step = filter_visual_information.get_step()
    input_xml = fixture_loader.load('step_library/filter_visual_information/input_basic.xml')
    expected = fixture_loader.load('step_library/filter_visual_information/expected_basic.xml')

    result = step.execute(input_xml)
    assert xml_equal(result, expected)
```
**Focus**: Specific transformation behavior

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
   mkdir -p tests/fixtures/{step_library,intermediate,advanced,integration}
   ```

2. **Add README files** to each category directory explaining purpose

3. **Identify Tier 1 steps** - Pick 5 most critical step_library functions

4. **Start with one step**:
   - Create `step_library/[step_name]/` directory
   - Create input_basic.xml
   - Run transformation manually
   - Save as expected_basic.xml
   - Write test
   - Document in README

5. **Iterate** through remaining Tier 1 steps

6. **Create intermediate fixtures** based on DATA_ANALYSIS.md patterns

7. **Expand to remaining tiers** as needed

---

## Appendix: Fixture Statistics

### Current State
- ✅ Minimal: 5 fixtures
- ❌ Step library: 0 fixtures (35 steps to cover)
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
