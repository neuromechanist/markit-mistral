"""
MarkIt Mistral Web Interface - PyScript Backend
Handles file processing using Mistral AI OCR in the browser
"""

import json
import logging
from typing import Any

import js
from pyodide.http import pyfetch

# Configure logging for browser console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebOCRProcessor:
    """
    OCR processor for web interface using Mistral AI API.
    Adapted for browser environment with PyScript.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "mistral-ocr-latest"
        self.max_file_size_mb = 50

    async def process_file_data(self, file_data: str, file_name: str, file_type: str,
                              include_images: bool = True) -> dict[str, Any]:
        """
        Process a file from base64 data using Mistral OCR.

        Args:
            file_data: Base64 encoded file data with data URI prefix
            file_name: Original filename
            file_type: MIME type of the file
            include_images: Whether to extract images

        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Processing file: {file_name} ({file_type})")

            # Prepare document configuration based on file type
            if file_type == "application/pdf":
                document_config = {
                    "type": "document_url",
                    "document_url": file_data
                }
            elif file_type.startswith("image/"):
                document_config = {
                    "type": "image_url",
                    "image_url": file_data
                }
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            # Make API request to Mistral
            js.updateProgress("Calling Mistral API...", 40)
            response = await self._make_api_request(document_config, include_images)

            js.updateProgress("Processing API response...", 70)

            # Extract text and images
            markdown_text = self._extract_text(response)
            extracted_images = []

            if include_images:
                js.updateProgress("Extracting images...", 80)
                extracted_images = self._extract_images(response)

            return {
                "success": True,
                "markdown": markdown_text,
                "images": extracted_images,
                "page_count": len(response.get("pages", []))
            }

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return {
                "success": False,
                "error": str(e),
                "markdown": "",
                "images": []
            }

    async def _make_api_request(self, document_config: dict, include_images: bool) -> dict:
        """Make API request to Mistral OCR service."""

        url = "https://api.mistral.ai/v1/ocr"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "document": document_config,
            "include_image_base64": include_images
        }

        try:
            # Use pyodide's fetch for API calls
            response = await pyfetch(
                url,
                method="POST",
                headers=headers,
                body=json.dumps(payload)
            )

            if not response.ok:
                error_text = await response.text()
                logger.error(f"API Error: {response.status} - {error_text}")

                if response.status == 401:
                    raise ValueError("Invalid API key. Please check your Mistral API key.")
                elif response.status == 429:
                    raise ValueError("Rate limit exceeded. Please try again later.")
                elif response.status == 413:
                    raise ValueError("File too large for processing.")
                else:
                    raise ValueError(f"API Error: {response.status} - {error_text}")

            result = await response.json()
            return result

        except Exception as e:
            if "Invalid API key" in str(e) or "Rate limit" in str(e):
                raise
            else:
                raise ValueError(f"Network error: {str(e)}") from e

    def _extract_text(self, response: dict) -> str:
        """Extract plain text from OCR response."""
        text_parts = []

        pages = response.get("pages", [])
        for page in pages:
            if "markdown" in page and page["markdown"]:
                text_parts.append(page["markdown"])

        return "\n\n".join(text_parts)

    def _extract_images(self, response: dict) -> list[dict[str, str]]:
        """Extract images from OCR response."""
        extracted_images = []

        pages = response.get("pages", [])
        for page_idx, page in enumerate(pages):
            images = page.get("images", [])
            for img_idx, image in enumerate(images):
                if "image_base64" in image and image["image_base64"]:

                    # Get image data
                    image_data = image["image_base64"]
                    if not image_data.startswith("data:"):
                        # Add data URI prefix if missing
                        image_data = f"data:image/png;base64,{image_data}"

                    # Generate filename
                    if "id" in image and image["id"]:
                        filename = image["id"]
                    else:
                        filename = f"page_{page_idx + 1}_image_{img_idx + 1}.png"

                    extracted_images.append({
                        "name": filename,
                        "data": image_data,
                        "page": page_idx + 1
                    })

        return extracted_images


# Global processor instance
processor = None


async def process_file_handler(event):
    """Handle file processing requests from JavaScript."""
    global processor

    try:
        # Get data from JavaScript
        data = event.detail

        # Create processor with API key
        processor = WebOCRProcessor(data["api_key"])

        # Process the file
        result = await processor.process_file_data(
            file_data=data["file_data"],
            file_name=data["file_name"],
            file_type=data["file_type"],
            include_images=data.get("include_images", True)
        )

        # Return result to JavaScript
        if hasattr(js, "pyScriptProcessFile"):
            js.pyScriptProcessFile(result)

    except Exception as e:
        logger.error(f"Error in process_file_handler: {e}")
        error_result = {
            "success": False,
            "error": str(e),
            "markdown": "",
            "images": []
        }

        if hasattr(js, "pyScriptProcessFile"):
            js.pyScriptProcessFile(error_result)
        else:
            js.showError(str(e))


# Set up event listener for file processing
js.document.addEventListener("processFile", process_file_handler)

# Log that PyScript is ready
logger.info("MarkIt Mistral PyScript backend initialized")

# Update UI to show PyScript is ready
if hasattr(js, "console"):
    js.console.log("MarkIt Mistral PyScript backend ready")
