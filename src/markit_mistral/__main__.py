"""
Command-line interface for markit-mistral.

This module provides the main CLI entry point for the markit-mistral tool.
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main()) 