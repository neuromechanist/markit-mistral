# Suggested Commands for markit-mistral

## Environment Setup
```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Testing
```bash
# Run all tests with coverage
pytest tests/ --cov=markit_mistral --cov-report=term-missing

# Run specific test file
pytest tests/test_markdown_formatter.py

# Run only unit tests
pytest tests/ -m unit

# Run only integration tests (requires API key)
pytest tests/ -m integration
```

## Linting and Formatting
```bash
# Check and auto-fix lint issues
ruff check --fix --unsafe-fixes .

# Format code
ruff format .

# Type checking
mypy src/
```

## Running the CLI
```bash
# Convert PDF to markdown
markit-mistral document.pdf -o output.md

# Convert image to markdown
markit-mistral image.png -o result.md

# Extract images alongside markdown
markit-mistral document.pdf --extract-images -o output.md

# Verbose mode
markit-mistral document.pdf --verbose -o output.md
```

## Git
```bash
# Feature branch workflow
git checkout -b feature/short-description
git add <specific-files>
git commit -m "feat: concise description"
git push -u origin feature/short-description
gh pr create --title "Concise title" --body "Description"
```

## System Utilities (macOS/Darwin)
```bash
git status
git log --oneline -10
ls -la
```
