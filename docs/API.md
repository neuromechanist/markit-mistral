# API Documentation

This document provides detailed information about the markit-mistral API.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Classes](#core-classes)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Installation

```bash
pip install markit-mistral
```

## Quick Start

```python
from markit_mistral import MarkItMistral

# Initialize with API key
converter = MarkItMistral(api_key="your-mistral-api-key")

# Convert a PDF to markdown
result = converter.convert_file("document.pdf", "output.md")
print(f"Converted to: {result}")
```

## Core Classes

### MarkItMistral

The main converter class that orchestrates the conversion process.

#### Constructor

```python
MarkItMistral(
    config: Config | None = None,
    api_key: str | None = None,
    max_retries: int | None = None,
    retry_delay: float | None = None,
    include_images: bool | None = None,
    preserve_math: bool | None = None,
)
```

**Parameters:**
- `config`: Configuration object (optional, will use defaults if not provided)
- `api_key`: Mistral API key (optional, can be set via environment variable)
- `max_retries`: Maximum number of retry attempts for API calls (default: 3)
- `retry_delay`: Delay between retries in seconds (default: 1.0)
- `include_images`: Whether to extract and include images (default: True)
- `preserve_math`: Whether to preserve mathematical equations (default: True)

#### Methods

##### convert_file()

Convert a PDF or image file to markdown.

```python
def convert_file(
    self,
    input_path: str | Path,
    output_path: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> Path
```

**Parameters:**
- `input_path`: Path to the input file (PDF or image)
- `output_path`: Path for the output markdown file (optional)
- `output_dir`: Directory for output files (optional)

**Returns:** Path to the generated markdown file

**Example:**
```python
# Basic usage
result = converter.convert_file("document.pdf")

# With custom output path
result = converter.convert_file("document.pdf", "custom_output.md")

# With custom output directory
result = converter.convert_file("document.pdf", output_dir="./outputs/")
```

##### convert_url()

Convert a document from URL to markdown.

```python
def convert_url(
    self,
    url: str,
    output_path: str | Path,
    output_dir: str | Path | None = None,
) -> Path
```

**Parameters:**
- `url`: URL to the document (PDF or image)
- `output_path`: Path for the output markdown file
- `output_dir`: Directory for output files (optional)

**Returns:** Path to the generated markdown file

**Example:**
```python
result = converter.convert_url(
    "https://example.com/document.pdf",
    "downloaded_doc.md"
)
```

##### get_supported_formats()

Get list of supported input file formats.

```python
def get_supported_formats(self) -> list[str]
```

**Returns:** List of supported file extensions

**Example:**
```python
formats = converter.get_supported_formats()
print(formats)  # ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
```

##### validate_input()

Validate if the input file is supported.

```python
def validate_input(self, input_path: str | Path) -> bool
```

**Parameters:**
- `input_path`: Path to the input file

**Returns:** True if the file is supported, False otherwise

**Example:**
```python
if converter.validate_input("document.pdf"):
    result = converter.convert_file("document.pdf")
else:
    print("Unsupported file type")
```

### Config

Configuration class for markit-mistral settings.

#### Constructor

```python
Config(
    mistral_api_key: str | None = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    max_file_size_mb: float = 50.0,
    include_images: bool = True,
    base64_images: bool = False,
    preserve_math: bool = True,
    log_level: str = "INFO",
)
```

#### Class Methods

##### from_env()

Create configuration from environment variables.

```python
@classmethod
def from_env(cls) -> "Config"
```

**Environment Variables:**
- `MISTRAL_API_KEY`: Mistral API key
- `MARKIT_MISTRAL_MAX_RETRIES`: Maximum retry attempts
- `MARKIT_MISTRAL_RETRY_DELAY`: Retry delay in seconds
- `MARKIT_MISTRAL_MAX_FILE_SIZE_MB`: Maximum file size in MB
- `MARKIT_MISTRAL_LOG_LEVEL`: Logging level

**Example:**
```python
# Set environment variable
import os
os.environ["MISTRAL_API_KEY"] = "your-api-key"

# Create config from environment
config = Config.from_env()
converter = MarkItMistral(config=config)
```

### OutputManager

Manages output files, directories, and metadata.

#### Constructor

```python
OutputManager(
    base_output_dir: str | Path | None = None,
    preserve_metadata: bool = True,
    create_zip_archive: bool = False,
    custom_naming: str | None = None,
)
```

**Parameters:**
- `base_output_dir`: Base directory for all outputs
- `preserve_metadata`: Whether to save conversion metadata
- `create_zip_archive`: Whether to create zip archives
- `custom_naming`: Custom naming pattern for output files

#### Methods

##### prepare_output_structure()

Prepare the output directory structure for a conversion.

```python
def prepare_output_structure(
    self,
    input_path: Path,
    output_path: Path | None = None,
    include_images: bool = True,
) -> dict[str, Path]
```

**Returns:** Dictionary with paths for different output components

##### save_metadata()

Save conversion metadata to a JSON file.

```python
def save_metadata(
    self,
    metadata_path: Path,
    conversion_metadata: dict[str, Any],
    input_info: dict[str, Any],
    processing_stats: dict[str, Any] | None = None,
) -> None
```

##### create_archive()

Create a zip archive containing all conversion outputs.

```python
def create_archive(
    self,
    output_structure: dict[str, Path],
    archive_path: Path | None = None,
) -> Path | None
```

## Configuration

### Environment Variables

markit-mistral can be configured using environment variables:

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

You can also use a configuration object:

```python
from markit_mistral import Config, MarkItMistral

config = Config(
    mistral_api_key="your-api-key",
    max_retries=5,
    retry_delay=2.0,
    max_file_size_mb=100.0,
    include_images=True,
    preserve_math=True,
    log_level="DEBUG"
)

converter = MarkItMistral(config=config)
```

## Error Handling

markit-mistral provides comprehensive error handling with custom exception classes:

### Exception Hierarchy

```
MarkItMistralError (base)
├── ConfigurationError
├── APIError
│   ├── APIKeyError
│   ├── APIQuotaError
│   └── APIRateLimitError
├── FileProcessingError
│   ├── UnsupportedFileTypeError
│   ├── FileNotFoundError
│   ├── FileCorruptedError
│   └── FileTooLargeError
├── OCRProcessingError
│   └── OCRTimeoutError
├── MarkdownGenerationError
├── ImageExtractionError
├── OutputError
│   ├── PermissionError
│   └── DiskSpaceError
├── ValidationError
└── NetworkError
```

### Error Handling Example

```python
from markit_mistral import MarkItMistral
from markit_mistral.exceptions import (
    APIKeyError,
    FileTooLargeError,
    UnsupportedFileTypeError,
    MarkItMistralError
)

try:
    converter = MarkItMistral()
    result = converter.convert_file("document.pdf")
    
except APIKeyError as e:
    print(f"API key issue: {e}")
    print("Please set MISTRAL_API_KEY environment variable")
    
except FileTooLargeError as e:
    print(f"File too large: {e}")
    print("Try processing a smaller file")
    
except UnsupportedFileTypeError as e:
    print(f"Unsupported file: {e}")
    supported = converter.get_supported_formats()
    print(f"Supported formats: {supported}")
    
except MarkItMistralError as e:
    print(f"markit-mistral error: {e}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Examples

### Basic PDF Conversion

```python
from markit_mistral import MarkItMistral

# Initialize converter
converter = MarkItMistral(api_key="your-api-key")

# Convert PDF to markdown
result = converter.convert_file("research_paper.pdf")
print(f"Converted to: {result}")

# The output will include:
# - research_paper.md (markdown file)
# - research_paper_images/ (directory with extracted images)
# - research_paper_metadata.json (conversion metadata)
```

### Image Conversion with Custom Settings

```python
from markit_mistral import MarkItMistral, Config

# Create custom configuration
config = Config(
    mistral_api_key="your-api-key",
    include_images=False,  # Don't extract images
    preserve_math=True,    # Preserve mathematical equations
    max_retries=5,         # More retries for reliability
)

converter = MarkItMistral(config=config)

# Convert image to markdown
result = converter.convert_file("screenshot.png", "extracted_text.md")
```

### Batch Processing

```python
from pathlib import Path
from markit_mistral import MarkItMistral

converter = MarkItMistral(api_key="your-api-key")

# Process multiple files
input_dir = Path("./documents")
output_dir = Path("./converted")

for pdf_file in input_dir.glob("*.pdf"):
    try:
        output_path = output_dir / f"{pdf_file.stem}.md"
        result = converter.convert_file(pdf_file, output_path)
        print(f"Converted {pdf_file} -> {result}")
    except Exception as e:
        print(f"Failed to convert {pdf_file}: {e}")
```

### URL Processing

```python
from markit_mistral import MarkItMistral

converter = MarkItMistral(api_key="your-api-key")

# Convert document from URL
url = "https://example.com/research_paper.pdf"
result = converter.convert_url(url, "downloaded_paper.md")
print(f"Downloaded and converted to: {result}")
```

### Advanced Output Management

```python
from markit_mistral import MarkItMistral
from markit_mistral.output_manager import OutputManager

# Create output manager with custom settings
output_manager = OutputManager(
    base_output_dir="./outputs",
    preserve_metadata=True,
    create_zip_archive=True,
    custom_naming="{original}_{timestamp}"
)

converter = MarkItMistral(api_key="your-api-key")
converter.output_manager = output_manager

# Convert with custom output management
result = converter.convert_file("document.pdf")

# This will create:
# - ./outputs/document_20240101_120000.md
# - ./outputs/document_20240101_120000_images/
# - ./outputs/document_20240101_120000_metadata.json
# - ./outputs/document_20240101_120000_complete.zip
```

### Mathematical Content Processing

```python
from markit_mistral import MarkItMistral

converter = MarkItMistral(
    api_key="your-api-key",
    preserve_math=True  # Enable math preservation
)

# Convert document with mathematical equations
result = converter.convert_file("math_textbook.pdf")

# The output markdown will contain LaTeX-formatted equations:
# $$E = mc^2$$
# $\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$
```

### Error Recovery and Logging

```python
import logging
from markit_mistral import MarkItMistral, Config

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

config = Config(
    mistral_api_key="your-api-key",
    max_retries=5,      # More retries
    retry_delay=2.0,    # Longer delay between retries
    log_level="DEBUG"   # Detailed logging
)

converter = MarkItMistral(config=config)

try:
    result = converter.convert_file("large_document.pdf")
except Exception as e:
    print(f"Conversion failed: {e}")
    # Check logs for detailed error information
```

## Performance Tips

1. **File Size**: Keep files under 50MB for optimal performance
2. **Retries**: Increase `max_retries` for unreliable network connections
3. **Images**: Set `include_images=False` if you don't need image extraction
4. **Batch Processing**: Process files sequentially to avoid rate limits
5. **Error Handling**: Always wrap API calls in try-catch blocks

## Rate Limits

Mistral API has rate limits. markit-mistral handles this automatically with:
- Exponential backoff retry strategy
- Automatic rate limit detection
- Graceful degradation on quota exceeded

## Support

For issues and questions:
- GitHub Issues: [markit-mistral issues](https://github.com/your-username/markit-mistral/issues)
- Documentation: [Full documentation](https://github.com/your-username/markit-mistral/docs) 