# Code Style and Conventions

## Python Style
- **Line length:** 88 characters (Black standard)
- **Quote style:** Double quotes
- **Import sorting:** isort via ruff
- **Formatter:** ruff format
- **Linter:** ruff check with rules: E, W, F, I, B, C4, UP, ARG, SIM, TCH

## Type Hints
- Required for all public functions and methods
- mypy in strict mode with specific overrides for mistralai, PIL, PyPDF2
- Use `typing-extensions` for backcompat

## Naming Conventions
- Classes: PascalCase (MarkItMistral, OCRProcessor, MarkdownFormatter)
- Functions/methods: snake_case (convert_file, process_pdf, format_document)
- Constants: UPPER_SNAKE_CASE (_MAX_SLUG_LENGTH, _MIME_TO_EXT)
- Private methods: leading underscore (_process_with_retry, _encode_image_to_data_uri)
- Logger: module-level `logger` variable

## Docstrings
- Google or NumPy style
- Module-level docstrings at file top

## Patterns
- Context managers for resource management
- Dataclasses for data structures
- Pathlib for file operations (not os.path)
- F-strings for string formatting
- Structured logging throughout

## Commit Messages
- Format: `<type>: <description>` (feat, fix, docs, refactor, test, chore)
- Concise, no emojis
- No co-author attribution lines
- Atomic commits, one logical change each

## Testing
- NO MOCKS policy: real data or skip tests entirely
- pytest with coverage reporting
- Markers: slow, integration, unit
