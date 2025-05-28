"""
OCR processor using Mistral AI API.

This module handles the interaction with Mistral AI OCR services
to extract text from images and PDF pages.
"""

import base64
import logging
import mimetypes
import os
import time
from pathlib import Path

from mistralai import Mistral
from mistralai import SDKError

from .exceptions import (
    APIError,
    APIKeyError,
    APIQuotaError,
    APIRateLimitError,
    FileCorruptedError,
    FileNotFoundError,
    FileTooLargeError,
    NetworkError,
    OCRProcessingError,
    OCRTimeoutError,
    handle_api_error,
)

logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    OCR processor using Mistral AI API.

    Handles image preprocessing, API communication, and result processing
    for optimal text extraction with math equation preservation.
    """

    def __init__(
        self,
        api_key: str | None = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        max_file_size_mb: int = 50,
    ):
        """
        Initialize the OCR processor.

        Args:
            api_key: Mistral API key. If None, will try to get from environment.
            max_retries: Maximum number of retries for API calls.
            retry_delay: Delay between retries in seconds.
            max_file_size_mb: Maximum file size in MB.
        """
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise APIKeyError()

        try:
            self.client = Mistral(api_key=self.api_key)
        except Exception as e:
            raise APIError(f"Failed to initialize Mistral client: {e}")
            
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_file_size_mb = max_file_size_mb
        self.model = "mistral-ocr-latest"

    def _encode_image_to_data_uri(self, image_path: str | Path) -> str:
        """Encode an image file to a data URI.

        Args:
            image_path: Path to the image file.

        Returns:
            Data URI string for the image.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        mime_type, _ = mimetypes.guess_type(str(image_path))
        if not mime_type or not mime_type.startswith("image/"):
            raise FileCorruptedError(str(image_path), "File is not a valid image")

        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
        except PermissionError as e:
            raise FileCorruptedError(str(image_path), f"Permission denied: {e}")
        except Exception as e:
            raise FileCorruptedError(str(image_path), f"Failed to read image file: {e}")

        try:
            base64_encoded = base64.b64encode(image_data).decode("utf-8")
            return f"data:{mime_type};base64,{base64_encoded}"
        except Exception as e:
            raise OCRProcessingError(f"Failed to encode image as base64: {e}")

    def _encode_pdf_to_data_uri(self, pdf_path: str | Path) -> str:
        """Encode a PDF file to a data URI.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Data URI string for the PDF.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if pdf_path.suffix.lower() != ".pdf":
            raise FileCorruptedError(str(pdf_path), "File is not a PDF")

        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()
        except PermissionError as e:
            raise FileCorruptedError(str(pdf_path), f"Permission denied: {e}")
        except Exception as e:
            raise FileCorruptedError(str(pdf_path), f"Failed to read PDF file: {e}")

        try:
            base64_encoded = base64.b64encode(pdf_data).decode("utf-8")
            return f"data:application/pdf;base64,{base64_encoded}"
        except Exception as e:
            raise OCRProcessingError(f"Failed to encode PDF as base64: {e}")

    def _process_with_retry(self, document_config: dict, include_images: bool = True) -> dict:
        """Process document with retry logic.

        Args:
            document_config: Document configuration for the API.
            include_images: Whether to include images in the response.

        Returns:
            OCR response from Mistral API.
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"OCR attempt {attempt + 1}/{self.max_retries}")

                response = self.client.ocr.process(
                    model=self.model,
                    document=document_config,
                    include_image_base64=include_images
                )

                logger.info(f"OCR successful on attempt {attempt + 1}")
                return response

            except SDKError as e:
                last_exception = handle_api_error(e)
                logger.warning(f"OCR attempt {attempt + 1} failed: {e}")

                # Don't retry on certain errors
                if isinstance(last_exception, (APIKeyError, APIQuotaError)):
                    break

                if attempt < self.max_retries - 1:
                    sleep_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"All {self.max_retries} OCR attempts failed")

            except Exception as e:
                last_exception = handle_api_error(e)
                logger.error(f"Unexpected error during OCR: {e}")
                break

        raise last_exception or OCRProcessingError("OCR processing failed after all retries")

    def process_pdf(self, pdf_path: str | Path, include_images: bool = True) -> dict:
        """Process a PDF file using Mistral OCR.

        Args:
            pdf_path: Path to the PDF file.
            include_images: Whether to include extracted images in the response.

        Returns:
            OCR response containing pages with markdown text and images.
        """
        logger.info(f"Processing PDF: {pdf_path}")

        pdf_path = Path(pdf_path)
        
        try:
            file_size = pdf_path.stat().st_size
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        except Exception as e:
            raise FileCorruptedError(str(pdf_path), f"Cannot access file: {e}")
            
        file_size_mb = file_size / (1024 * 1024)
        logger.debug(f"PDF file size: {file_size_mb:.2f} MB")

        # Check file size limit
        if file_size_mb > self.max_file_size_mb:
            raise FileTooLargeError(str(pdf_path), file_size_mb, self.max_file_size_mb)

        try:
            data_uri = self._encode_pdf_to_data_uri(pdf_path)

            document_config = {
                "type": "document_url",
                "document_url": data_uri
            }

            response = self._process_with_retry(document_config, include_images)

            logger.info(f"Successfully processed PDF with {len(response.pages)} pages")
            return response

        except (FileNotFoundError, FileCorruptedError, FileTooLargeError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to process PDF {pdf_path}: {e}")
            raise OCRProcessingError(f"PDF processing failed: {e}")

    def process_image(self, image_path: str | Path, include_images: bool = True) -> dict:
        """Process an image file using Mistral OCR.

        Args:
            image_path: Path to the image file.
            include_images: Whether to include the processed image in the response.

        Returns:
            OCR response containing the extracted text and image data.
        """
        logger.info(f"Processing image: {image_path}")

        image_path = Path(image_path)
        file_size = image_path.stat().st_size
        logger.debug(f"Image file size: {file_size / (1024 * 1024):.2f} MB")

        # Check file size limit
        max_size_bytes = self.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise ValueError(
                f"Image file too large: {file_size / (1024 * 1024):.2f} MB "
                f"(max {self.max_file_size_mb} MB)"
            )

        try:
            data_uri = self._encode_image_to_data_uri(image_path)

            document_config = {
                "type": "image_url",
                "image_url": data_uri
            }

            response = self._process_with_retry(document_config, include_images)

            logger.info(f"Successfully processed image with {len(response.pages)} pages")
            return response

        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}")
            raise

    def process_url(self, url: str, include_images: bool = True) -> dict:
        """Process a document from a URL using Mistral OCR.

        Args:
            url: URL to the document (PDF or image).
            include_images: Whether to include extracted images in the response.

        Returns:
            OCR response containing pages with markdown text and images.
        """
        logger.info(f"Processing URL: {url}")

        try:
            # Determine document type based on URL
            if url.lower().endswith(('.pdf',)) or 'pdf' in url.lower():
                document_config = {
                    "type": "document_url",
                    "document_url": url
                }
            else:
                document_config = {
                    "type": "image_url",
                    "image_url": url
                }

            response = self._process_with_retry(document_config, include_images)

            logger.info(f"Successfully processed URL with {len(response.pages)} pages")
            return response

        except Exception as e:
            logger.error(f"Failed to process URL {url}: {e}")
            raise

    def extract_text(self, response: dict) -> str:
        """Extract plain text from OCR response.

        Args:
            response: OCR response from Mistral API.

        Returns:
            Concatenated text from all pages.
        """
        text_parts = []

        for page in response.pages:
            if hasattr(page, 'markdown') and page.markdown:
                text_parts.append(page.markdown)

        return "\n\n".join(text_parts)

    def extract_images(self, response: dict, output_dir: str | Path) -> list[Path]:
        """Extract and save images from OCR response.

        Args:
            response: OCR response from Mistral API.
            output_dir: Directory to save extracted images.

        Returns:
            List of paths to saved image files.
        """
        output_dir = Path(output_dir)
        saved_images = []

        # First, check if there are any images to extract
        has_images = False
        for page in response.pages:
            if hasattr(page, 'images') and page.images:
                for image in page.images:
                    if hasattr(image, 'image_base64') and image.image_base64:
                        has_images = True
                        break
            if has_images:
                break
        
        # Only create directory if we have images to save
        if not has_images:
            logger.debug("No images found in OCR response")
            return saved_images
        
        # Create output directory only when needed
        output_dir.mkdir(parents=True, exist_ok=True)

        for page_idx, page in enumerate(response.pages):
            if hasattr(page, 'images') and page.images:
                for image in page.images:
                    if hasattr(image, 'image_base64') and image.image_base64:
                        try:
                            # Parse the base64 data URI
                            if image.image_base64.startswith('data:'):
                                header, data = image.image_base64.split(',', 1)
                                image_data = base64.b64decode(data)
                            else:
                                image_data = base64.b64decode(image.image_base64)

                            # Use the image ID as filename, or generate one
                            if hasattr(image, 'id') and image.id:
                                filename = image.id
                            else:
                                filename = f"page_{page_idx + 1}_image_{len(saved_images) + 1}.jpg"

                            image_path = output_dir / filename

                            with open(image_path, 'wb') as f:
                                f.write(image_data)

                            saved_images.append(image_path)
                            logger.debug(f"Saved image: {image_path}")

                        except Exception as e:
                            logger.warning(f"Failed to save image from page {page_idx + 1}: {e}")

        logger.info(f"Extracted {len(saved_images)} images to {output_dir}")
        return saved_images

    def get_page_count(self, response: dict) -> int:
        """Get the number of pages in the OCR response.

        Args:
            response: OCR response from Mistral API.

        Returns:
            Number of pages processed.
        """
        return len(response.pages) if hasattr(response, 'pages') else 0

    def get_page_text(self, response: dict, page_index: int) -> str:
        """Get text from a specific page.

        Args:
            response: OCR response from Mistral API.
            page_index: Zero-based page index.

        Returns:
            Markdown text from the specified page.
        """
        if not hasattr(response, 'pages') or page_index >= len(response.pages):
            raise IndexError(f"Page index {page_index} out of range")

        page = response.pages[page_index]
        return page.markdown if hasattr(page, 'markdown') else ""
