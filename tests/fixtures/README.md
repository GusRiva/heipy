# Test Fixtures for heipy

This directory contains test fixtures for the heipy test suite.

## Directory Structure

```
fixtures/
├── minimal/              # Minimal reusable TEI documents
│   ├── basic_tei.xml
│   ├── tei_with_entities.xml
└── step_fixtures/        # Step-specific input/expected pairs
    └── {step_name}/
        ├── input_*.xml
        ├── expected_*.xml
        ├── config_*.xml
```

## Minimal TEI Fixtures

### basic_tei.xml
Bare minimum valid TEI document with:
- Complete teiHeader (fileDesc with required elements)
- Simple text/body structure
- Two paragraphs with xml:id attributes

Use for: Basic transformation tests that don't need special markup.
## Step-Specific Fixtures

Each transformation step should have its own subdirectory in `step_fixtures/`
containing input/expected XML pairs.

### Naming Convention

- `input.xml` - Default input
- `expected.xml` - Default expected output
- `input_{variant}.xml` - Named variant (e.g., input_edge_case.xml)
- `expected_{variant}.xml` - Corresponding expected output
- `config.xml` or `structure.xml` - Configuration files for steps that need them

### Creating New Fixtures

Use the `StepFixtureLoader` and `FixtureGenerator` classes from `tests/helpers/fixture_loader.py`:

```python
from tests.helpers.fixture_loader import StepFixtureLoader, FixtureGenerator

loader = StepFixtureLoader(step_fixtures_dir)
generator = FixtureGenerator(loader)

# Create directory for new step
loader.create_step_fixture_dir("new_step")

# Save input fixture
generator.save_xml_as_fixture(input_tree, "new_step", "input")

# Generate expected output (after verifying step works correctly!)
generator.generate_expected_from_step(step, "new_step")
```

## Important Notes

### Whitespace Preservation

**All fixtures preserve whitespace exactly as written.** The test comparison utilities
do NOT normalize whitespace by default, as whitespace can be semantically significant
in TEI documents (especially in verse, mixed content, etc.).

When creating fixtures:
- Be intentional about whitespace
- Match the exact whitespace of transformation outputs
- Use consistent indentation (2 spaces recommended)

### XML Formatting

- Use UTF-8 encoding
- Include XML declaration: `<?xml version="1.0" encoding="UTF-8"?>`
- Use 2-space indentation
- Include namespace declarations on root element
- Use xml:id for elements that might be referenced

### Fixture Validation

Before committing new fixtures:
1. Validate against TEI schema (if applicable)
2. Verify whitespace is intentional
3. Test with actual transformation steps
4. Document any special characteristics in comments or README
