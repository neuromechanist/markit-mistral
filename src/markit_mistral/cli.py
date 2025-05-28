"""
Command-line interface for markit-mistral.

Provides a CLI similar to markitdown but using Mistral AI for OCR processing.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import __version__, __description__
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
  markit-mistral document.pdf
  markit-mistral image.png -o output.md
  cat document.pdf | markit-mistral
  markit-mistral document.pdf --extract-images
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
        help="extract images to separate files alongside markdown output"
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
        if args.extract_images:
            config.include_images = True
        if args.base64_images:
            config.base64_images = True
        if hasattr(args, 'preserve_math') and args.preserve_math is not None:
            config.preserve_math = args.preserve_math
        if args.verbose:
            config.log_level = "DEBUG"
        if args.quiet:
            config.log_level = "ERROR"
        
        # Setup logging
        config.setup_logging()
        
        # Validate configuration
        config.validate()
        
        # Create converter
        converter = MarkItMistral(config=config)
        
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
                with open(result_path, 'r', encoding='utf-8') as f:
                    print(f.read(), end='')
                
                # Clean up temporary file if we created one
                if result_path.parent == config.get_temp_dir():
                    result_path.unlink()
        
        else:
            # TODO: Implement stdin processing
            print("Error: stdin processing not yet implemented", file=sys.stderr)
            return 1
        
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