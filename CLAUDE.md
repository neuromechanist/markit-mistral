# markit-mistral Instructions

## Project Context
**Purpose:** PDF and image to markdown converter using Mistral AI OCR with advanced math equation support
**Tech Stack:** Python 3.10+, Mistral AI API, Hatch build system, pytest
**Architecture:** Modular pipeline: file processing -> OCR (Mistral API) -> markdown formatting -> output management
**Version:** 0.2.2 (Alpha)

## Environment Setup
```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest tests/  # Real tests only, NO MOCKS
```

## Development Workflow
1. **Check context:** Review .context/plan.md for current tasks
2. **Understand deeply:** Check .context/ideas.md for design decisions
3. **Research if needed:** Update .context/research.md with findings
4. **Branch:** `git checkout -b feature/short-description`
5. **Code:** Follow patterns (see .rules/python.md for standards)
6. **Test:** Real data only (see .rules/testing.md for details)
7. **Document failures:** Log in .context/scratch_history.md immediately
8. **Commit:** Atomic, concise, no emojis
9. **PR:** Reference context and issue
10. **Code review:** Run pr-review-toolkit after creating PR (see .rules/code_review.md)

## [CRITICAL] Core Principles

### [FUNDAMENTAL] NO MOCKS - Test Reality Only
- Use real data or skip tests entirely
- Ask user for sample data if needed
**Details:** .rules/testing.md

### Commits & Git
- Atomic commits, focused changes
- Concise messages, no emojis, no co-author lines
- Feature branches for multi-step work
**Details:** .rules/git.md

### Documentation
- Examples > explanations
- README gets someone running in <5 minutes
**Details:** .rules/documentation.md

## Project Structure
```
src/markit_mistral/
  __init__.py             # Package exports, version
  __main__.py             # Entry point
  cli.py                  # CLI argument parsing and execution
  config.py               # Configuration management
  converter.py            # Main converter orchestration (MarkItMistral)
  file_processor.py       # File type detection and validation
  markdown_formatter.py   # Markdown generation, math/table formatting
  ocr_processor.py        # Mistral API integration, OCR pipeline
  output_manager.py       # Output file and image management
tests/
  test_cli.py             # CLI tests
  test_config.py          # Config tests
  test_markdown_formatter.py  # Formatter tests
  test_ocr_processor.py   # OCR tests
  test_output_manager.py  # Output manager tests
```

## Key APIs
- `MarkItMistral` - Main converter class (`converter.py`)
- `OCRProcessor` - Mistral API client (`ocr_processor.py`)
- `MarkdownFormatter` - Markdown post-processing (`markdown_formatter.py`)
- `Config` - Configuration management (`config.py`)

## [REFERENCE] Rules Directory
- `.rules/python.md` - Style, linting (ruff), type hints (mypy)
- `.rules/testing.md` - NO MOCK policy, real data testing
- `.rules/git.md` - Commit standards, branch strategy
- `.rules/ci_cd.md` - GitHub Actions setup
- `.rules/code_review.md` - PR review toolkit and checklist
- `.rules/documentation.md` - MkDocs setup
- `.rules/self_improve.md` - Learning from projects
- `.rules/serena_mcp.md` - Code intelligence with Serena MCP

## Context Files
- `.context/plan.md` - Current tasks and phases
- `.context/research.md` - Technical explorations
- `.context/ideas.md` - Design concepts
- `.context/scratch_history.md` - Failed attempts and lessons

## Quick Commands
```bash
# Run tests (real data only)
pytest tests/ --cov

# Format and lint
ruff check --fix . && ruff format .

# Type check
mypy src/

# Build docs
mkdocs serve

# Run CLI
markit-mistral document.pdf -o output.md
```

---
Remember: You're building maintainable systems, not just writing code.
Check .rules/ for detailed guidance on any topic.
