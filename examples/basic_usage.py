#!/usr/bin/env python3
"""
Basic usage example for markit-mistral.

This script demonstrates how to use the markit-mistral library
to convert PDF and image files to markdown.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from markit_mistral import Config, MarkItMistral


def main():
    """Demonstrate basic usage of markit-mistral."""

    # Check if API key is set
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("Error: Please set the MISTRAL_API_KEY environment variable")
        print("Example: export MISTRAL_API_KEY='your-api-key-here'")
        return 1

    print("markit-mistral Basic Usage Example")
    print("=" * 40)

    # Create configuration
    config = Config.from_env()
    config.log_level = "INFO"

    # Initialize converter
    converter = MarkItMistral(config=config)

    print(f"Supported file formats: {converter.get_supported_formats()}")

    # Example 1: Check if a file is supported
    example_files = ["document.pdf", "image.png", "unsupported.txt"]

    print("\nFile Support Check:")
    for filename in example_files:
        file_path = Path(filename)
        is_supported = converter.file_processor.is_supported(file_path)
        print(f"  {filename}: {'✓ Supported' if is_supported else '✗ Not supported'}")

    # Example 2: Process a sample file (if available)
    sample_files = [
        "sample.pdf",
        "sample_math.pdf",
        "test.png",
        "document.jpg",
    ]

    print("\nLooking for sample files to process...")

    sample_file = None
    for filename in sample_files:
        file_path = Path(filename)
        if file_path.exists():
            sample_file = file_path
            break

    if sample_file:
        print(f"Found sample file: {sample_file}")

        try:
            # Get file information
            file_info = converter.file_processor.get_file_info(sample_file)
            print(f"File info: {file_info}")

            # Convert the file
            print(f"Converting {sample_file}...")
            output_path = converter.convert_file(
                input_path=sample_file,
                output_dir=Path("output")
            )

            print(f"✓ Successfully converted to: {output_path}")

            # Read and display first few lines of output
            with open(output_path, encoding='utf-8') as f:
                lines = f.readlines()[:10]  # First 10 lines

            print("\nFirst 10 lines of generated markdown:")
            print("-" * 40)
            for line in lines:
                print(line.rstrip())

            if len(lines) == 10:
                print("... (truncated)")

        except Exception as e:
            print(f"✗ Error processing file: {e}")
            return 1

    else:
        print("No sample files found. To test the converter:")
        print("1. Place a PDF or image file in this directory")
        print("2. Run this script again")
        print("\nExample usage in code:")
        print("""
from markit_mistral import MarkItMistral

# Initialize converter
converter = MarkItMistral()

# Convert a file
output_path = converter.convert_file('document.pdf')
print(f"Converted to: {output_path}")
""")

    print("\nExample CLI usage:")
    print("  markit-mistral document.pdf")
    print("  markit-mistral image.png -o output.md")
    print("  markit-mistral document.pdf --extract-images")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
