"""
Main converter class for markit-mistral.

This module provides the MarkItMistral class which orchestrates the conversion
of PDF and image files to markdown using Mistral AI OCR.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from .config import Config
from .file_processor import create_file_processor
from .markdown_formatter import (
    MarkdownFormatter,
    extract_title_from_markdown,
    title_to_slug,
)
from .ocr_processor import OCRProcessor
from .output_manager import OutputManager

logger = logging.getLogger(__name__)


def _content_hash(path: Path, length: int = 6) -> str:
    """Return a short hex digest of a file's contents for uniqueness."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:length]


def generate_image_prefix(
    pages: list,
    input_path: Path,
    output_path: Path,
) -> str:
    """Build a robust, collision-resistant image filename prefix.

    Fallback order:
    1. First non-trivial heading from OCR (H1, then H2)
    2. Input filename stem (if not too generic)
    3. Output filename stem

    A short content hash is always appended to prevent collisions
    between documents that happen to share the same title or filename.
    """
    slug = None

    # Layer 1: meaningful heading from OCR content
    ocr_title = extract_title_from_markdown(pages)
    if ocr_title:
        slug = title_to_slug(ocr_title)

    # Layer 2: input filename (if it looks meaningful)
    if slug is None or slug == "document":
        stem = input_path.stem
        # Reject very generic stems
        generic_stems = {"input", "document", "file", "temp", "tmp", "output", "scan"}
        if stem.lower() not in generic_stems:
            slug = title_to_slug(stem)

    # Layer 3: output filename
    if slug is None or slug == "document":
        slug = title_to_slug(output_path.stem)

    # Guarantee uniqueness with a content hash suffix
    short_hash = _content_hash(input_path)
    return f"{slug}-{short_hash}"


class MarkItMistral:
    """
    Main converter class for PDF and image to markdown conversion.

    Uses Mistral AI OCR to extract text and preserves mathematical equations
    and images in the output markdown.
    """

    def __init__(
        self,
        config: Config | None = None,
        api_key: str | None = None,
        max_retries: int | None = None,
        retry_delay: float | None = None,
        include_images: bool | None = None,
        preserve_math: bool | None = None,
    ):
        """
        Initialize the MarkItMistral converter.

        Args:
            config: Configuration object. If None, creates from environment.
            api_key: Mistral API key. Overrides config if provided.
            max_retries: Maximum number of retries for API calls. Overrides config if provided.
            retry_delay: Delay between retries in seconds. Overrides config if provided.
            include_images: Whether to extract and save images from documents. Overrides config if provided.
            preserve_math: Whether to preserve mathematical equations in LaTeX format. Overrides config if provided.
        """
        # Use provided config or create from environment
        self.config = config or Config.from_env()

        # Override config with provided parameters
        if api_key is not None:
            self.config.mistral_api_key = api_key
        if max_retries is not None:
            self.config.max_retries = max_retries
        if retry_delay is not None:
            self.config.retry_delay = retry_delay
        if include_images is not None:
            self.config.include_images = include_images
        if preserve_math is not None:
            self.config.preserve_math = preserve_math

        # Setup logging
        self.config.setup_logging()

        # Validate configuration
        self.config.validate()

        # Initialize components
        self.file_processor = create_file_processor()
        self.ocr_processor = OCRProcessor(
            api_key=self.config.mistral_api_key,
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay,
        )
        self.markdown_formatter = MarkdownFormatter(
            preserve_math=self.config.preserve_math,
            base64_images=self.config.base64_images,
        )
        self.output_manager = OutputManager(
            preserve_metadata=True,
            create_zip_archive=False,  # Can be configured later
        )

    def convert_file(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        output_dir: str | Path | None = None,
    ) -> Path:
        """
        Convert a PDF or image file to markdown.

        Args:
            input_path: Path to the input file (PDF or image).
            output_path: Path for the output markdown file. If None, will be generated.
            output_dir: Directory for output files. If None, uses input file directory.

        Returns:
            Path to the generated markdown file.
        """
        input_path = Path(input_path)

        # Validate input file
        self.file_processor.validate_file(input_path)

        # Get file info for logging
        file_info = self.file_processor.get_file_info(input_path)
        logger.info(f"Processing {file_info['name']} ({file_info['size_mb']} MB)")

        # Determine output paths
        if output_path is None:
            output_dir = input_path.parent if output_dir is None else Path(output_dir)

            output_path = output_dir / f"{input_path.stem}.md"
        else:
            output_path = Path(output_path)
            output_dir = output_path.parent

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Converting {input_path} to {output_path}")

        # Process the file based on its type
        file_type = self.file_processor.detect_file_type(input_path)

        if file_type == "pdf":
            response = self.ocr_processor.process_pdf(
                input_path, self.config.include_images
            )
        elif file_type == "image":
            response = self.ocr_processor.process_image(
                input_path, self.config.include_images
            )
        else:
            raise ValueError(f"Unsupported file type: {input_path.suffix}")

        # Derive image prefix with robust fallback chain + content hash
        image_prefix = generate_image_prefix(response.pages, input_path, output_path)

        # Extract and save images if requested
        image_paths: list[Path] = []
        rename_map: dict[str, str] = {}
        if self.config.include_images:
            # Create images subdirectory if needed
            if not self.config.base64_images:
                images_dir = output_dir / f"{output_path.stem}_images"
            else:
                images_dir = output_dir

            image_paths, rename_map = self.ocr_processor.extract_images(
                response, images_dir, image_prefix=image_prefix
            )
            logger.info(f"Extracted {len(image_paths)} images")

        # Generate markdown content using the formatter
        ocr_title = extract_title_from_markdown(response.pages)
        document_title = (
            ocr_title or input_path.stem.replace("_", " ").replace("-", " ").title()
        )
        markdown_content = self.markdown_formatter.format_document(
            pages=response.pages,
            image_paths=image_paths,
            output_dir=output_dir,
            document_title=document_title,
            rename_map=rename_map,
        )

        # Write markdown file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Extract and log metadata, save to JSON
        metadata = self.markdown_formatter.extract_metadata(markdown_content)
        images_count = (
            len(metadata["images"]) if isinstance(metadata["images"], list) else 0
        )
        logger.info(
            f"Generated markdown: {metadata['word_count']} words, "
            f"{metadata['math_equations']} math equations, "
            f"{images_count} images, "
            f"{metadata['tables']} tables"
        )

        # Save metadata JSON
        metadata_path = output_dir / f"{output_path.stem}_metadata.json"
        self.output_manager.save_metadata(
            metadata_path=metadata_path,
            conversion_metadata=metadata,
            input_info=file_info,
        )

        logger.info(f"Successfully converted to {output_path}")
        return output_path

    def convert(self, input_path: str | Path) -> str:
        """Convert a PDF or image file to markdown and return the text.

        This is a convenience wrapper around convert_file() that returns
        the markdown content as a string instead of writing to a file.

        Args:
            input_path: Path to the input file (PDF or image).

        Returns:
            The markdown text as a string.
        """
        import tempfile

        input_path = Path(input_path)
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / f"{input_path.stem}.md"
            self.convert_file(input_path, output_path=output_path, output_dir=tmp_dir)
            return output_path.read_text(encoding="utf-8")

    def convert_url(
        self,
        url: str,
        output_path: str | Path,
        output_dir: str | Path | None = None,
    ) -> Path:
        """
        Convert a document from URL to markdown.

        Args:
            url: URL to the document (PDF or image).
            output_path: Path for the output markdown file.
            output_dir: Directory for output files. If None, uses output_path directory.

        Returns:
            Path to the generated markdown file.
        """
        output_path = Path(output_path)

        output_dir = output_path.parent if output_dir is None else Path(output_dir)

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Converting URL {url} to {output_path}")

        # Process the URL
        response = self.ocr_processor.process_url(url, self.config.include_images)

        # For URL conversions there is no local file to hash, so fall back
        # to title slug with the output stem as disambiguator.
        ocr_title = extract_title_from_markdown(response.pages)
        image_prefix = title_to_slug(ocr_title) if ocr_title else output_path.stem

        # Extract and save images if requested
        image_paths: list[Path] = []
        rename_map: dict[str, str] = {}
        if self.config.include_images:
            # Create images subdirectory if needed
            if not self.config.base64_images:
                images_dir = output_dir / f"{output_path.stem}_images"
            else:
                images_dir = output_dir

            image_paths, rename_map = self.ocr_processor.extract_images(
                response, images_dir, image_prefix=image_prefix
            )
            logger.info(f"Extracted {len(image_paths)} images")

        # Generate markdown content using the formatter
        document_title = (
            ocr_title or output_path.stem.replace("_", " ").replace("-", " ").title()
        )
        markdown_content = self.markdown_formatter.format_document(
            pages=response.pages,
            image_paths=image_paths,
            output_dir=output_dir,
            document_title=document_title,
            rename_map=rename_map,
        )

        # Write markdown file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Extract and log metadata
        metadata = self.markdown_formatter.extract_metadata(markdown_content)
        images_count = (
            len(metadata["images"]) if isinstance(metadata["images"], list) else 0
        )
        logger.info(
            f"Generated markdown: {metadata['word_count']} words, "
            f"{metadata['math_equations']} math equations, "
            f"{images_count} images, "
            f"{metadata['tables']} tables"
        )

        logger.info(f"Successfully converted URL to {output_path}")
        return output_path

    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported input file formats.

        Returns:
            List of supported file extensions.
        """
        return [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]

    def validate_input(self, input_path: str | Path) -> bool:
        """
        Validate if the input file is supported.

        Args:
            input_path: Path to the input file.

        Returns:
            True if the file is supported, False otherwise.
        """
        input_path = Path(input_path)

        if not input_path.exists():
            return False

        return input_path.suffix.lower() in self.get_supported_formats()

    def get_file_info(self, input_path: str | Path) -> dict[str, str | int | float]:
        """
        Get information about the input file.

        Args:
            input_path: Path to the input file.

        Returns:
            Dictionary with file information.
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        file_size = input_path.stat().st_size

        return {
            "name": input_path.name,
            "path": str(input_path),
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "extension": input_path.suffix.lower(),
            "supported": self.validate_input(input_path),
        }
