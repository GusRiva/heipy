# XML Comparison Utilities

## Overview

The `tests/helpers/xml_compare.py` module provides utilities for comparing XML documents in tests. All utilities **PRESERVE WHITESPACE by default** because whitespace is semantically significant in TEI documents.

## Two Comparison Approaches

### 1. Element-based Comparison (Structural)
Compares parsed XML trees - checks structure, tags, attributes, text content.

**Functions:**
- `xml_equal(left, right, ignore_attribute_order=True) -> bool`
- `assert_xml_equal(left, right, message="", ignore_attribute_order=True)`
- `xml_diff(left, right, context_lines=3) -> str`

**Use when:** Comparing XML structure and content after transformations.

**Example:**
```python
from tests.helpers.xml_compare import assert_xml_equal

result_tree = transform(input_tree)
assert_xml_equal(result_tree, expected_tree)
```

### 2. Text-based Comparison (Byte-for-byte)
Compares serialized XML text - useful for testing file I/O, entity preservation, exact formatting.

**Functions:**
- `text_equal(left, right, normalize_prologues=True, strip_trailing_whitespace=True) -> bool`
- `assert_text_equal(left, right, message="", normalize_prologues=True, strip_trailing_whitespace=True)`
- `normalize_prologue(xml_text: str) -> Tuple[str, str]`
- `xml_to_comparable_text(xml_input, strip_trailing_whitespace=True) -> str`

**Use when:**
- Testing roundtrip file I/O
- Verifying entity preservation (e.g., `&bar;` not expanded)
- Ensuring exact formatting preservation

**Accepts:** Path objects, string file paths, XML strings, XML elements/trees

**Example:**
```python
from pathlib import Path
from tests.helpers.xml_compare import assert_text_equal

# Test that file I/O preserves entities and formatting
tree.write(output_path)
assert_text_equal(input_path, output_path)  # Path objects!
```

## Key Design Decisions

### Whitespace Handling
- **Element-based (`xml_equal`)**: Compares text/tail **exactly** - whitespace matters
- **Text-based (`text_equal`)**: Compares text **exactly** with optional prologue normalization

Both approaches preserve whitespace, which is critical for TEI documents.

### Input Flexibility
All functions accept multiple input types:
- `Path` objects (preferred for files)
- String file paths
- XML strings
- lxml Element or ElementTree objects

## Usage in Tests

### conftest.py Fixtures
```python
@pytest.fixture
def xml_equal():
    """Fixture providing xml_equal function."""
    from tests.helpers.xml_compare import xml_equal as _xml_equal
    return _xml_equal
```

### Test Pattern (tests/steps)
```python
def test_transformation(fixture_loader, xml_equal):
    input_tree, expected_tree = fixture_loader.load_step_pair('my_step', variant='basic')
    input_string = fixture_loader.tree_to_string(input_tree)

    result_string = step.execute(input_string)

    # xml_equal handles string vs tree comparison
    assert xml_equal(result_string, expected_tree)
```

### Test Pattern (tests/parsers)
```python
def test_roundtrip_with_entities(minimal_fixtures_dir, tmp_path):
    tree = et.parse(input_path, parser=parser)
    tree.write(output_path)

    # Text-based comparison for exact preservation
    assert_text_equal(input_path, output_path, message="Roundtrip failed")
```

## Removed Redundancies (2025-12-12)

**Before:**
- Duplicate `normalize_prologue()` in `test_parser_io.py`
- Unused `compare_elements()` in `test_parser_io.py`
- Manual text comparison with multiple normalize/strip operations

**After:**
- Single source of truth in `xml_compare.py`
- Clean imports: `from tests.helpers.xml_compare import normalize_prologue, assert_text_equal`
- Simplified test code using standard utilities

## Additional Utilities

- `assert_xml_structure_equal(left, right)` - Compare structure only (ignore text)
- `assert_xml_contains(container, contained)` - Check fragment containment
- `normalize_for_comparison(xml_input, ...)` - Optional normalization (use sparingly)
- `get_xpath_to_element(elem, root)` - Generate XPath for debugging

## Location
- Module: `/home/gusriva/Dokumente/Editionen/EditionVieGregoire/heipy/tests/helpers/xml_compare.py`
- Tests: Used throughout `tests/parsers/` and `tests/steps/`
