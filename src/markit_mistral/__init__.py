"""
markit-mistral: PDF and image to markdown converter using Mistral AI OCR.

A powerful tool for converting PDF documents and images to markdown format
with advanced math equation support and image extraction capabilities.
"""

__version__ = "0.2.2"
__author__ = "Seyed Yahya Shirazi"
__email__ = "shirazi@ieee.org"
__description__ = "PDF and image to markdown converter using Mistral AI OCR"

from .config import Config
from .converter import MarkItMistral
from .file_processor import FileProcessorManager, create_file_processor
from .markdown_formatter import MarkdownFormatter
from .ocr_processor import OCRProcessor

__all__ = [
    "MarkItMistral",
    "OCRProcessor",
    "Config",
    "FileProcessorManager",
    "create_file_processor",
    "MarkdownFormatter",
]
