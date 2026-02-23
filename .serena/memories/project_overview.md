# markit-mistral - Project Overview

## Purpose
PDF and image to markdown converter using Mistral AI OCR with advanced mathematical equation support.

## Tech Stack
- **Language:** Python 3.10+ (supports 3.10-3.13)
- **Build System:** Hatch (hatchling)
- **Package Manager:** uv
- **AI Backend:** Mistral AI OCR API (mistralai SDK)
- **Key Dependencies:** Pillow, PyPDF2, requests, python-magic, typing-extensions
- **Testing:** pytest, pytest-cov
- **Linting/Formatting:** ruff
- **Type Checking:** mypy (strict)
- **CI/CD:** GitHub Actions (ci.yml, pages.yml, publish.yml)

## Version
0.2.2 (Alpha)

## Repository
https://github.com/neuromechanist/markit-mistral

## Architecture
Modular pipeline design:
1. **FileProcessor** - Input validation and file type detection
2. **OCRProcessor** - Mistral AI API interaction with retry logic
3. **MarkdownFormatter** - Post-processing, math/table formatting, image refs
4. **OutputManager** - File and image output handling
5. **MarkItMistral** - Orchestrator class tying the pipeline together
6. **CLI** - Command-line interface via `create_parser()` and `main()`

## Project Structure
```
src/markit_mistral/
  __init__.py             # Package exports, version (0.2.2)
  __main__.py             # Entry point
  cli.py                  # CLI: create_parser(), main()
  config.py               # Config class (from_env, validate, setup_logging)
  converter.py            # MarkItMistral class (convert_file, convert, convert_url)
  file_processor.py       # FileProcessor, ImageProcessor, PDFProcessor, FileProcessorManager
  markdown_formatter.py   # MarkdownFormatter (format_document, math processing, image refs)
  ocr_processor.py        # OCRProcessor (process_pdf, process_image, process_url)
  output_manager.py       # OutputManager (prepare_output_structure, save_metadata)
  exceptions.py           # Custom exception classes
tests/
  test_cli.py
  test_config.py
  test_markdown_formatter.py
  test_ocr_processor.py
  test_output_manager.py
docs/                     # Web interface and documentation
examples/                 # Usage examples
.github/workflows/        # CI/CD (ci.yml, pages.yml, publish.yml)
```

## Context and Rules
- `CLAUDE.md` - Project-level instructions (tracked in git)
- `.rules/` - Development standards (tracked in git)
- `.context/` - Plan, ideas, research, scratch history (tracked in git)
