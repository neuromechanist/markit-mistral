# Testing Standards - NO MOCKS Policy

## Core Philosophy: Test Reality, Not Fiction
**Why NO MOCKS?** Mocks test your assumptions, not your code.
**Real bugs** hide in integration points, not unit logic.
**Better approach:** No test is better than a false-confidence mock test.

## [STRICT] NO MOCKS, NO FAKE DATA
Never use mocks, stubs, or fake datasets. If real testing isn't possible, don't write tests.
- **No mock objects** - Use real implementations
- **No mock datasets** - Use actual sample data
- **No stub services** - Connect to real test instances
- **Alternative:** Ask user for sample data or test environment setup

## When to Write Tests
- **DO:** Test with real data and actual dependencies
- **DO:** Test against actual file systems
- **DO:** Use real PDF/image samples for conversion testing
- **DON'T:** Write tests if only mocks would work
- **DON'T:** Create artificial test scenarios

## Test Structure
```
tests/
  conftest.py              # Real test fixtures
  test_cli.py              # CLI interface tests
  test_config.py           # Configuration tests
  test_markdown_formatter.py  # Formatter tests with real markdown
  test_ocr_processor.py    # OCR tests (requires API key)
  test_output_manager.py   # Output management tests
```

## Framework
- **Runner:** `pytest` with `pytest-cov`
- **Coverage:** `--cov=markit_mistral --cov-report=term-missing`
- **Markers:** `slow`, `integration`, `unit`

## The Testing Mindset
- **You're not checking boxes** - you're building confidence
- **Every test should** catch at least one real bug category
- **Think:** "Will this test save someone from a 3am wake-up call?"

---
*NO MOCKS. Real tests build real confidence. When in doubt, ask for real data.*
