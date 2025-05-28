"""
Tests for the CLI module.
"""

import pytest
from markit_mistral.cli import create_parser


def test_create_parser():
    """Test that the argument parser is created correctly."""
    parser = create_parser()
    assert parser.prog == "markit-mistral"
    
    # Test version argument
    with pytest.raises(SystemExit):
        parser.parse_args(["--version"])


def test_parser_with_input_file():
    """Test parser with input file argument."""
    parser = create_parser()
    args = parser.parse_args(["test.pdf"])
    
    assert args.input == "test.pdf"
    assert args.output is None
    assert args.verbose is False
    assert args.quiet is False


def test_parser_with_output_file():
    """Test parser with output file argument."""
    parser = create_parser()
    args = parser.parse_args(["test.pdf", "-o", "output.md"])
    
    assert args.input == "test.pdf"
    assert args.output == "output.md"


def test_parser_with_flags():
    """Test parser with various flags."""
    parser = create_parser()
    args = parser.parse_args([
        "test.pdf", 
        "--extract-images", 
        "--verbose",
        "--api-key", "test-key"
    ])
    
    assert args.input == "test.pdf"
    assert args.extract_images is True
    assert args.verbose is True
    assert args.api_key == "test-key" 