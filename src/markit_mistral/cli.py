"""
Command-line interface for markit-mistral.

Provides a CLI similar to markitdown but using Mistral AI for OCR processing.
"""

import argparse
import sys
from pathlib import Path

from . import __description__, __version__
from .config import Config
from .converter import MarkItMistral


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description=__description__,
        prog="markit-mistral",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  markit-mistral document.pdf
  markit-mistral image.png -o output.md
  
  # Image handling
  markit-mistral document.pdf --extract-images      # Extract images to folder
  markit-mistral document.pdf --base64-images       # Embed images as base64
  markit-mistral document.pdf --no-images           # Skip image processing
  
  # Progress and output control
  markit-mistral large_document.pdf --progress      # Show progress bar
  markit-mistral document.pdf --quiet               # Silent mode
  markit-mistral document.pdf --verbose             # Detailed output
  
  # Reading from stdin
  cat document.pdf | markit-mistral                 # Process from stdin
        """.strip(),
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="show version and exit"
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="input file (PDF or image). If not provided, reads from stdin"
    )

    parser.add_argument(
        "-o", "--output",
        help="output file path. If not provided, outputs to stdout"
    )

    parser.add_argument(
        "--api-key",
        help="Mistral API key (can also be set via MISTRAL_API_KEY environment variable)"
    )

    parser.add_argument(
        "--extract-images",
        action="store_true",
        help="extract images to separate files alongside markdown output (default: extract if images exist)"
    )

    parser.add_argument(
        "--no-images",
        action="store_true",
        help="suppress image extraction (overrides --extract-images)"
    )

    parser.add_argument(
        "--base64-images",
        action="store_true",
        help="embed images as base64 in markdown instead of separate files"
    )

    parser.add_argument(
        "--preserve-math",
        action="store_true",
        default=True,
        help="preserve mathematical equations in LaTeX format (default: True)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="enable verbose output"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress all output except errors"
    )

    parser.add_argument(
        "--progress",
        action="store_true",
        help="show progress bars for long operations (default: auto-detect TTY)"
    )

    parser.add_argument(
        "--batch",
        action="store_true",
        help="enable batch processing mode for multiple files"
    )

    parser.add_argument(
        "--save-metadata",
        action="store_true",
        default=True,
        help="save conversion metadata to JSON file (default: True)"
    )

    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="skip saving conversion metadata"
    )

    parser.add_argument(
        "--create-archive",
        action="store_true",
        help="create a zip archive with all output files"
    )

    parser.add_argument(
        "--output-format",
        choices=["markdown", "json", "both"],
        default="markdown",
        help="output format (default: markdown)"
    )

    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        # Create configuration
        config = Config.from_env()

        # Override config with command line arguments
        if args.api_key:
            config.mistral_api_key = args.api_key
        
        # Handle image extraction options (--no-images overrides --extract-images)
        if args.no_images:
            config.include_images = False
        elif args.extract_images:
            config.include_images = True
        # Default: include_images is True unless explicitly disabled
        
        if args.base64_images:
            config.base64_images = True
        if hasattr(args, 'preserve_math') and args.preserve_math is not None:
            config.preserve_math = args.preserve_math
        if args.verbose:
            config.log_level = "DEBUG"
        if args.quiet:
            config.log_level = "ERROR"

        # Configure progress bars (default to auto-detect TTY unless specified)
        show_progress = args.progress if hasattr(args, 'progress') else sys.stdout.isatty()
        if args.quiet:
            show_progress = False

        # Setup logging
        config.setup_logging()

        # Validate configuration
        config.validate()

        # Create converter
        converter = MarkItMistral(config=config)

        # Configure output manager
        if hasattr(args, 'no_metadata') and args.no_metadata:
            converter.output_manager.preserve_metadata = False
        if hasattr(args, 'create_archive') and args.create_archive:
            converter.output_manager.create_zip_archive = True

        # Determine input source
        if args.input:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Error: Input file not found: {input_path}", file=sys.stderr)
                return 1

            # Validate file type
            if not converter.file_processor.is_supported(input_path):
                supported = ", ".join(converter.file_processor.get_supported_extensions())
                print(f"Error: Unsupported file type: {input_path.suffix}", file=sys.stderr)
                print(f"Supported formats: {supported}", file=sys.stderr)
                return 1

            # Convert file
            if args.output:
                output_path = Path(args.output)
                result_path = converter.convert_file(input_path, output_path)
                if not args.quiet:
                    print(f"Successfully converted to: {result_path}")
            else:
                # Output to stdout
                result_path = converter.convert_file(input_path)
                with open(result_path, encoding='utf-8') as f:
                    print(f.read(), end='')

                # Clean up temporary file if we created one
                if result_path.parent == config.get_temp_dir():
                    result_path.unlink()

        else:
            # Process from stdin
            if sys.stdin.isatty():
                print("Error: No input file provided and stdin is a TTY", file=sys.stderr)
                print("Use: markit-mistral <file> or pipe content to stdin", file=sys.stderr)
                return 1
            
            # Read binary data from stdin
            import tempfile
            input_data = sys.stdin.buffer.read()
            
            if not input_data:
                print("Error: No data received from stdin", file=sys.stderr)
                return 1
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(input_data)
                temp_input_path = Path(temp_file.name)
            
            try:
                # Validate file type
                if not converter.file_processor.is_supported(temp_input_path):
                    print("Error: Unsupported file type from stdin", file=sys.stderr)
                    supported = ", ".join(converter.file_processor.get_supported_extensions())
                    print(f"Supported formats: {supported}", file=sys.stderr)
                    return 1
                
                # Convert file
                if args.output:
                    output_path = Path(args.output)
                    result_path = converter.convert_file(temp_input_path, output_path)
                    if not args.quiet:
                        print(f"Successfully converted to: {result_path}", file=sys.stderr)
                else:
                    # Output to stdout
                    result_path = converter.convert_file(temp_input_path)
                    with open(result_path, encoding='utf-8') as f:
                        print(f.read(), end='')
                    
                    # Clean up temporary result file
                    if result_path.parent == config.get_temp_dir():
                        result_path.unlink()
            
            finally:
                # Clean up temporary input file
                temp_input_path.unlink(missing_ok=True)

        return 0

    except Exception as e:
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
