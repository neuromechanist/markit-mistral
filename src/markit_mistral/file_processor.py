"""File processing engine for markit-mistral."""

import logging
import mimetypes
from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)


class FileProcessor(ABC):
    """Abstract base class for file processors."""

    @abstractmethod
    def can_process(self, file_path: Path) -> bool:
        """Check if this processor can handle the given file."""
        pass

    @abstractmethod
    def validate_file(self, file_path: Path) -> None:
        """Validate that the file can be processed."""
        pass

    @abstractmethod
    def get_file_info(self, file_path: Path) -> dict[str, str | int | float]:
        """Get information about the file."""
        pass


class ImageProcessor(FileProcessor):
    """Processor for image files (PNG, JPEG, TIFF, etc.)."""

    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif', '.webp'}

    def can_process(self, file_path: Path) -> bool:
        """Check if this is a supported image file."""
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS

    def validate_file(self, file_path: Path) -> None:
        """Validate that the image file can be processed."""
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        if not self.can_process(file_path):
            raise ValueError(f"Unsupported image format: {file_path.suffix}")

        # Try to open with PIL to validate it's a valid image
        try:
            with Image.open(file_path) as img:
                img.verify()
        except Exception as e:
            raise ValueError(f"Invalid image file: {file_path}") from e

    def get_file_info(self, file_path: Path) -> dict[str, str | int | float]:
        """Get information about the image file."""
        self.validate_file(file_path)

        file_size = file_path.stat().st_size

        with Image.open(file_path) as img:
            width, height = img.size
            mode = img.mode
            format_name = img.format

        return {
            "name": file_path.name,
            "path": str(file_path),
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "extension": file_path.suffix.lower(),
            "width": width,
            "height": height,
            "mode": mode,
            "format": format_name,
            "mime_type": mimetypes.guess_type(str(file_path))[0],
        }


class PDFProcessor(FileProcessor):
    """Processor for PDF files."""

    def can_process(self, file_path: Path) -> bool:
        """Check if this is a PDF file."""
        return file_path.suffix.lower() == '.pdf'

    def validate_file(self, file_path: Path) -> None:
        """Validate that the PDF file can be processed."""
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if not self.can_process(file_path):
            raise ValueError(f"Not a PDF file: {file_path}")

        # Basic PDF validation - check file header
        try:
            with open(file_path, 'rb') as f:
                header = f.read(5)
                if not header.startswith(b'%PDF-'):
                    raise ValueError(f"Invalid PDF file: {file_path}")
        except Exception as e:
            raise ValueError(f"Cannot read PDF file: {file_path}") from e

    def get_file_info(self, file_path: Path) -> dict[str, str | int | float]:
        """Get information about the PDF file."""
        self.validate_file(file_path)

        file_size = file_path.stat().st_size

        # Try to get page count using PyPDF2
        page_count = None
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                page_count = len(reader.pages)
        except Exception:
            logger.warning(f"Could not determine page count for {file_path}")

        return {
            "name": file_path.name,
            "path": str(file_path),
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "extension": file_path.suffix.lower(),
            "page_count": page_count,
            "mime_type": "application/pdf",
        }


class FileProcessorManager:
    """Manager for handling different file types."""

    def __init__(self):
        """Initialize the file processor manager."""
        self.processors: list[FileProcessor] = [
            PDFProcessor(),
            ImageProcessor(),
        ]

    def get_processor(self, file_path: Path) -> FileProcessor:
        """Get the appropriate processor for a file."""
        for processor in self.processors:
            if processor.can_process(file_path):
                return processor

        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def validate_file(self, file_path: Path) -> None:
        """Validate that a file can be processed."""
        processor = self.get_processor(file_path)
        processor.validate_file(file_path)

    def get_file_info(self, file_path: Path) -> dict[str, str | int | float]:
        """Get information about a file."""
        processor = self.get_processor(file_path)
        return processor.get_file_info(file_path)

    def is_supported(self, file_path: Path) -> bool:
        """Check if a file type is supported."""
        try:
            self.get_processor(file_path)
            return True
        except ValueError:
            return False

    def get_supported_extensions(self) -> list[str]:
        """Get list of supported file extensions."""
        extensions = set()

        # Add PDF extension
        extensions.add('.pdf')

        # Add image extensions
        extensions.update(ImageProcessor.SUPPORTED_FORMATS)

        return sorted(extensions)

    def detect_file_type(self, file_path: Path) -> str:
        """Detect the type of file."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            processor = self.get_processor(file_path)
            if isinstance(processor, PDFProcessor):
                return "pdf"
            elif isinstance(processor, ImageProcessor):
                return "image"
            else:
                return "unknown"
        except ValueError:
            return "unsupported"


def create_file_processor() -> FileProcessorManager:
    """Create and return a file processor manager."""
    return FileProcessorManager()
