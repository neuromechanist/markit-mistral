# markit-mistral

A powerful PDF and image to markdown converter using Mistral AI OCR with advanced mathematical equation support.

## Features

- Convert PDF documents and images to clean markdown
- Advanced OCR using Mistral AI for high accuracy text extraction
- Preserve mathematical equations in LaTeX format
- Extract and manage images alongside markdown output
- Support for complex documents with tables, figures, and formulas
- Command-line interface similar to markitdown
- **Web interface for browser-based processing**
- Batch processing capabilities
- Configurable output formats

## Usage Options

### Web Interface (Browser-based)

For a user-friendly, browser-based experience:

1. Open `docs/index.html` in your browser
2. Enter your Mistral API key
3. Drag and drop files or click to upload
4. Download the generated markdown and images

**Features:**
- No installation required - runs entirely in your browser
- Privacy-focused - files never leave your device
- Real-time progress tracking
- Responsive design for mobile and desktop

See the [Web Interface README](src/markit_mistral/web/README.md) for detailed instructions.

### Command Line Interface

For automated workflows and integration:

## Installation

### Prerequisites

- Python 3.10 or higher
- Mistral AI API key

### Install from PyPI (coming soon)

```bash
pip install markit-mistral
```

### Install from Source

```bash
git clone https://github.com/yahya/markit-mistral.git
cd markit-mistral
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yahya/markit-mistral.git
cd markit-mistral
pip install -e ".[dev]"
```

## Quick Start

### API Key Setup

Set your Mistral AI API key as an environment variable:

```bash
export MISTRAL_API_KEY="your-api-key-here"
```

Or pass it directly via command line:

```bash
markit-mistral document.pdf --api-key your-api-key-here
```

### Basic Usage

Convert a PDF to markdown:

```bash
markit-mistral document.pdf
```

Convert with output file:

```bash
markit-mistral document.pdf -o output.md
```

Convert an image:

```bash
markit-mistral image.png -o result.md
```

Extract images alongside markdown:

```bash
markit-mistral document.pdf --extract-images -o output.md
```

Process from stdin:

```bash
cat document.pdf | markit-mistral > output.md
```

## Command Line Options

```
usage: markit-mistral [-h] [-v] [-o OUTPUT] [--api-key API_KEY]
                      [--extract-images] [--base64-images]
                      [--preserve-math] [--verbose] [--quiet]
                      [input]

PDF and image to markdown converter using Mistral AI OCR

positional arguments:
  input                 input file (PDF or image). If not provided, reads from stdin

options:
  -h, --help            show this help message and exit
  -v, --version         show version and exit
  -o OUTPUT, --output OUTPUT
                        output file path. If not provided, outputs to stdout
  --api-key API_KEY     Mistral API key (can also be set via MISTRAL_API_KEY environment variable)
  --extract-images      extract images to separate files alongside markdown output
  --base64-images       embed images as base64 in markdown instead of separate files
  --preserve-math       preserve mathematical equations in LaTeX format (default: True)
  --verbose             enable verbose output
  --quiet               suppress all output except errors
```

## Mathematical Equation Support

markit-mistral automatically detects and preserves mathematical equations in multiple formats:

- **Inline math**: `$E = mc^2$` or `\(E = mc^2\)`
- **Display math**: `$$\frac{-b \pm \sqrt{b^2-4ac}}{2a}$$` or `\[\frac{-b \pm \sqrt{b^2-4ac}}{2a}\]`
- **Complex equations**: Multi-line equations, matrices, chemical formulas
- **Mixed content**: Documents with both text and mathematical content

## Image Management

When processing documents with images, markit-mistral can:

- Extract images to separate files in the same directory
- Generate relative links in markdown
- Maintain original image quality and format
- Support base64 embedding for standalone markdown files

Example output structure:
```
output.md
output_images/
├── image_001.png
├── image_002.jpg
└── figure_003.png
```

## Python API

```python
from markit_mistral import MarkItMistral

# Initialize converter
converter = MarkItMistral(api_key="your-api-key")

# Convert a file
markdown_content = converter.convert_file("document.pdf")

# Convert with custom options
markdown_content = converter.convert_file(
    "document.pdf",
    extract_images=True,
    preserve_math=True
)
```

## Configuration

You can configure markit-mistral through:

1. Environment variables
2. Command line arguments
3. Configuration file (coming soon)

### Environment Variables

- `MISTRAL_API_KEY`: Your Mistral AI API key
- `MARKIT_MISTRAL_CONFIG`: Path to configuration file

## Supported File Formats

### Input Formats
- PDF documents
- PNG images
- JPEG images
- TIFF images
- BMP images

### Output Formats
- Markdown with LaTeX math
- Markdown with extracted images
- Markdown with base64 embedded images

## Performance

markit-mistral is optimized for:

- Large document processing
- Batch operations
- Memory-efficient streaming
- API rate limit handling

## Contributing

We welcome contributions! Please see our contributing guidelines for details.

### Development Setup

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`
4. Format code: `black src tests`
5. Check types: `mypy src`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with the powerful Mistral AI OCR capabilities
- Inspired by the markitdown project
- Thanks to the open source community for various dependencies

## Support

- Report issues on [GitHub Issues](https://github.com/yahya/markit-mistral/issues)
- Check the documentation for common problems
- Join our community discussions

## Roadmap

- [ ] Plugin system for custom processors
- [ ] Multiple output format support
- [ ] Advanced table recognition
- [ ] Batch processing UI
- [ ] Cloud deployment options
- [ ] Integration with popular document workflows

---

**Note**: This project is in active development. Some features may be experimental.
