"""
Command-line interface for markit-mistral.

Provides a CLI similar to markitdown but using Mistral AI for OCR processing.
"""

import argparse
import sys

from . import __version__, __description__


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

    # TODO: Implement the actual conversion logic
    print(f"markit-mistral v{__version__}")
    print("This is a placeholder. Implementation coming soon!")
    
    if args.input:
        print(f"Would process: {args.input}")
    else:
        print("Would process from stdin")
    
    if args.output:
        print(f"Would output to: {args.output}")
    else:
        print("Would output to stdout")

    return 0


if __name__ == "__main__":
    sys.exit(main()) 