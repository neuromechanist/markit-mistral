# CLI Documentation

This document provides detailed information about the markit-mistral command-line interface.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Command Options](#command-options)
- [Examples](#examples)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Tips and Best Practices](#tips-and-best-practices)

## Installation

```bash
pip install markit-mistral
```

After installation, the `markit-mistral` command will be available in your terminal.

## Basic Usage

### Convert a PDF file

```bash
markit-mistral document.pdf
```

This will create `document.md` in the same directory as the input file.

### Convert with custom output

```bash
markit-mistral document.pdf -o output.md
```

### Convert from stdin

```bash
cat document.pdf | markit-mistral > output.md
```

## Command Options

### Input/Output Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `input` | - | Input file path (PDF or image) | `markit-mistral file.pdf` |
| `--output` | `-o` | Output markdown file path | `-o output.md` |

### API Configuration

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--api-key` | - | Mistral API key | `--api-key your-key` |

### Image Handling

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--extract-images` | - | Extract images to separate files | Auto (if images exist) |
| `--no-images` | - | Suppress image extraction | False |
| `--base64-images` | - | Embed images as base64 in markdown | False |

### Output Control

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--verbose` | `-v` | Enable verbose output | False |
| `--quiet` | `-q` | Suppress all output except errors | False |
| `--progress` | - | Show progress bars for long operations | Auto-detect TTY |

### Output Management

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--save-metadata` | - | Save conversion metadata to JSON file | True |
| `--no-metadata` | - | Skip saving conversion metadata | False |
| `--create-archive` | - | Create a zip archive with all output files | False |
| `--output-format` | - | Output format (markdown, json, both) | markdown |

### Processing Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--batch` | - | Enable batch processing mode | False |

### Help and Version

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--version` | - | Show version information |

## Examples

### Basic Conversion

```bash
# Convert a PDF to markdown
markit-mistral research_paper.pdf

# Convert with custom output name
markit-mistral research_paper.pdf -o paper.md

# Convert an image
markit-mistral screenshot.png -o extracted_text.md
```

### Image Handling

```bash
# Extract images to separate files (default behavior)
markit-mistral document.pdf --extract-images

# Suppress image extraction
markit-mistral document.pdf --no-images

# Embed images as base64 in markdown
markit-mistral document.pdf --base64-images

# Extract images but don't save them separately
markit-mistral document.pdf --no-images --base64-images
```

### Output Control

```bash
# Verbose output with detailed logging
markit-mistral document.pdf --verbose

# Quiet mode (only errors)
markit-mistral document.pdf --quiet

# Show progress bar
markit-mistral large_document.pdf --progress
```

### Output Management

```bash
# Save metadata (default)
markit-mistral document.pdf --save-metadata

# Skip metadata
markit-mistral document.pdf --no-metadata

# Create zip archive with all outputs
markit-mistral document.pdf --create-archive

# Different output formats
markit-mistral document.pdf --output-format json
markit-mistral document.pdf --output-format both
```

### API Configuration

```bash
# Specify API key directly
markit-mistral document.pdf --api-key your-mistral-api-key

# Use environment variable (recommended)
export MISTRAL_API_KEY="your-mistral-api-key"
markit-mistral document.pdf
```

### Stdin Processing

```bash
# Process from stdin
cat document.pdf | markit-mistral > output.md

# Process URL content
curl -s https://example.com/document.pdf | markit-mistral > output.md

# Process with options
cat document.pdf | markit-mistral --no-images --quiet > output.md
```

### Batch Processing

```bash
# Process multiple files
for file in *.pdf; do
    markit-mistral "$file" --quiet
done

# With custom output directory
mkdir converted
for file in *.pdf; do
    markit-mistral "$file" -o "converted/${file%.pdf}.md"
done
```

### Advanced Examples

```bash
# High-quality conversion with all features
markit-mistral document.pdf \
    --extract-images \
    --save-metadata \
    --create-archive \
    --progress \
    --verbose

# Minimal conversion for text extraction only
markit-mistral document.pdf \
    --no-images \
    --no-metadata \
    --quiet \
    -o text_only.md

# Convert with custom settings and error handling
markit-mistral document.pdf \
    --verbose \
    --progress \
    --output-format both \
    || echo "Conversion failed"
```

## Configuration

### Environment Variables

Set these environment variables to configure default behavior:

```bash
# Required
export MISTRAL_API_KEY="your-mistral-api-key"

# Optional
export MARKIT_MISTRAL_MAX_RETRIES=3
export MARKIT_MISTRAL_RETRY_DELAY=1.0
export MARKIT_MISTRAL_MAX_FILE_SIZE_MB=50.0
export MARKIT_MISTRAL_LOG_LEVEL=INFO
```

### Configuration File

You can also create a configuration file (not yet implemented):

```bash
# ~/.markit-mistral/config.toml
[api]
key = "your-mistral-api-key"
max_retries = 3
retry_delay = 1.0

[processing]
max_file_size_mb = 50.0
include_images = true
preserve_math = true

[output]
save_metadata = true
create_archive = false
```

## Error Handling

### Common Errors and Solutions

#### API Key Issues

```bash
$ markit-mistral document.pdf
Error: Invalid or missing API key
Details: Please set the MISTRAL_API_KEY environment variable or pass --api-key
```

**Solution:**
```bash
export MISTRAL_API_KEY="your-api-key"
# or
markit-mistral document.pdf --api-key your-api-key
```

#### File Not Found

```bash
$ markit-mistral nonexistent.pdf
Error: File not found: nonexistent.pdf
```

**Solution:** Check the file path and ensure the file exists.

#### Unsupported File Type

```bash
$ markit-mistral document.txt
Error: Unsupported file type: document.txt
Details: Supported formats: .pdf, .png, .jpg, .jpeg, .tiff, .bmp, .gif
```

**Solution:** Convert your file to a supported format or use a different tool.

#### File Too Large

```bash
$ markit-mistral huge_document.pdf
Error: File too large: huge_document.pdf (150.5 MB)
Details: Maximum allowed size: 50 MB
```

**Solution:** Split the file into smaller parts or compress it.

#### Network Issues

```bash
$ markit-mistral document.pdf
Error: Network error occurred
Details: Check your internet connection and try again
```

**Solution:** Check your internet connection and retry.

#### Rate Limit Exceeded

```bash
$ markit-mistral document.pdf
Error: API rate limit exceeded
Details: Please wait before making more requests
```

**Solution:** Wait a few minutes before retrying.

### Verbose Error Information

Use `--verbose` to get detailed error information:

```bash
markit-mistral problematic_file.pdf --verbose
```

This will show:
- Detailed error messages
- Stack traces for debugging
- API request/response information
- Processing steps and timing

## Tips and Best Practices

### Performance Optimization

1. **File Size**: Keep files under 50MB for best performance
   ```bash
   # Check file size before processing
   ls -lh document.pdf
   ```

2. **Batch Processing**: Process files sequentially to avoid rate limits
   ```bash
   for file in *.pdf; do
       markit-mistral "$file" --quiet
       sleep 1  # Brief pause between files
   done
   ```

3. **Image Handling**: Skip images if not needed
   ```bash
   markit-mistral document.pdf --no-images  # Faster processing
   ```

### Quality Optimization

1. **High-Quality Conversion**: Use all features for best results
   ```bash
   markit-mistral document.pdf \
       --extract-images \
       --save-metadata \
       --verbose
   ```

2. **Mathematical Content**: Ensure math preservation is enabled (default)
   ```bash
   markit-mistral math_paper.pdf  # Math equations preserved automatically
   ```

### Automation and Scripting

1. **Error Handling in Scripts**:
   ```bash
   #!/bin/bash
   for file in *.pdf; do
       if markit-mistral "$file" --quiet; then
           echo "✓ Converted: $file"
       else
           echo "✗ Failed: $file"
       fi
   done
   ```

2. **Progress Monitoring**:
   ```bash
   # Monitor conversion progress
   markit-mistral large_file.pdf --progress --verbose
   ```

3. **Output Organization**:
   ```bash
   # Organize outputs by date
   DATE=$(date +%Y%m%d)
   mkdir -p "converted/$DATE"
   markit-mistral document.pdf -o "converted/$DATE/document.md"
   ```

### Troubleshooting

1. **Debug Mode**: Use verbose output for troubleshooting
   ```bash
   markit-mistral document.pdf --verbose 2>&1 | tee debug.log
   ```

2. **Test with Small Files**: Start with small files to verify setup
   ```bash
   # Create a test PDF or use a small image
   markit-mistral small_test.pdf --verbose
   ```

3. **Check Dependencies**: Ensure all dependencies are installed
   ```bash
   pip show markit-mistral
   ```

4. **Validate API Key**: Test API connectivity
   ```bash
   markit-mistral --version  # Should work without API key
   echo "test" | markit-mistral  # Will test API key
   ```

### Integration Examples

#### With Git Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit
# Convert PDFs to markdown before committing

for pdf in $(git diff --cached --name-only --diff-filter=A | grep '\.pdf$'); do
    markit-mistral "$pdf" --no-images --quiet
    git add "${pdf%.pdf}.md"
done
```

#### With CI/CD

```yaml
# .github/workflows/convert-docs.yml
name: Convert Documents
on:
  push:
    paths: ['docs/*.pdf']

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install markit-mistral
        run: pip install markit-mistral
      - name: Convert PDFs
        env:
          MISTRAL_API_KEY: ${{ secrets.MISTRAL_API_KEY }}
        run: |
          for pdf in docs/*.pdf; do
            markit-mistral "$pdf" --quiet
          done
      - name: Commit results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/*.md
          git commit -m "Auto-convert PDFs to markdown" || exit 0
          git push
```

#### With Make

```makefile
# Makefile
PDFS := $(wildcard docs/*.pdf)
MARKDOWNS := $(PDFS:.pdf=.md)

.PHONY: convert clean

convert: $(MARKDOWNS)

%.md: %.pdf
	markit-mistral $< -o $@ --quiet

clean:
	rm -f docs/*.md docs/*_images/ docs/*_metadata.json

watch:
	find docs -name "*.pdf" | entr make convert
```

## Support

For additional help:

1. **Built-in Help**: `markit-mistral --help`
2. **Version Info**: `markit-mistral --version`
3. **GitHub Issues**: Report bugs and request features
4. **Documentation**: Full API documentation available
5. **Examples**: Check the examples directory for more use cases
