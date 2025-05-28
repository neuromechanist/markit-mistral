"""
MarkIt Mistral Web Interface - PyScript Backend
Handles file processing using Mistral AI OCR in the browser
"""

import json
import logging
from typing import Any

import js
from pyodide.http import pyfetch

# Immediate console logging to verify PyScript is working
js.console.log("🚀 MarkIt Mistral PyScript starting...")

# Configure logging for browser console
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Enable debug mode for detailed logging
DEBUG_MODE = True


def debug_log(message: str, data: Any = None):
    """Enhanced debug logging for browser console."""
    try:
        if data is not None:
            js.console.log(f"[DEBUG] {message}", js.JSON.stringify(data))
        else:
            js.console.log(f"[DEBUG] {message}")
    except Exception as e:
        js.console.error(f"Debug log error: {e}")


# Test debug logging immediately
debug_log("PyScript debug logging initialized")


class WebOCRProcessor:
    """
    OCR processor for web interface using Mistral AI API.
    Adapted for browser environment with PyScript.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "mistral-ocr-latest"
        self.max_file_size_mb = 50

    async def process_file_data(
        self,
        file_data: str,
        file_name: str,
        file_type: str,
        include_images: bool = True,
    ) -> dict[str, Any]:
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
            debug_log(
                "Starting file processing",
                {
                    "file_name": file_name,
                    "file_type": file_type,
                    "include_images": include_images,
                    "file_data_length": len(file_data) if file_data else 0,
                },
            )

            logger.info(f"Processing file: {file_name} ({file_type})")

            # Validate file data
            if not file_data:
                raise ValueError("No file data provided")

            debug_log("File data validation passed")

            # Prepare document configuration based on file type
            if file_type == "application/pdf":
                document_config = {"type": "document_url", "document_url": file_data}
                debug_log("Configured for PDF processing")
            elif file_type.startswith("image/"):
                document_config = {"type": "image_url", "image_url": file_data}
                debug_log("Configured for image processing")
            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            debug_log("Document configuration prepared", document_config)

            # Make API request to Mistral
            js.updateProgress("Calling Mistral API...", 40)
            debug_log("About to make API request to Mistral")

            response = await self._make_api_request(document_config, include_images)
            debug_log(
                "API request completed successfully",
                {"response_keys": list(response.keys()) if response else None},
            )

            js.updateProgress("Processing API response...", 70)

            # Extract text and images
            debug_log("Starting text extraction")
            markdown_text = self._extract_text(response)
            debug_log("Text extraction completed", {"text_length": len(markdown_text)})

            extracted_images = []

            if include_images:
                js.updateProgress("Extracting images...", 80)
                debug_log("Starting image extraction")
                extracted_images = self._extract_images(response)
                debug_log(
                    "Image extraction completed", {"image_count": len(extracted_images)}
                )

            result = {
                "success": True,
                "markdown": markdown_text,
                "images": extracted_images,
                "page_count": len(response.get("pages", [])),
            }

            debug_log(
                "Processing completed successfully",
                {
                    "markdown_length": len(markdown_text),
                    "image_count": len(extracted_images),
                    "page_count": result["page_count"],
                },
            )

            return result

        except Exception as e:
            error_msg = str(e)
            debug_log(
                "Error during processing",
                {"error": error_msg, "error_type": type(e).__name__},
            )
            logger.error(f"Error processing file: {e}")

            # Show error in browser console for debugging
            js.console.error(f"Processing error: {error_msg}")

            return {"success": False, "error": error_msg, "markdown": "", "images": []}

    async def _make_api_request(
        self, document_config: dict, include_images: bool
    ) -> dict:
        """Make API request to Mistral OCR service."""

        url = "https://api.mistral.ai/v1/ocr"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "document": document_config,
            "include_image_base64": include_images,
        }

        debug_log(
            "Preparing API request",
            {
                "url": url,
                "model": self.model,
                "document_type": document_config.get("type"),
                "include_images": include_images,
                "api_key_length": len(self.api_key) if self.api_key else 0,
            },
        )

        try:
            debug_log("Making API request with pyfetch")

            # Use pyodide's fetch for API calls
            response = await pyfetch(
                url, method="POST", headers=headers, body=json.dumps(payload)
            )

            debug_log(
                "API response received",
                {
                    "status": response.status,
                    "ok": response.ok,
                    "status_text": response.status
                    if hasattr(response, "status_text")
                    else "N/A",
                },
            )

            if not response.ok:
                error_text = await response.text()
                debug_log(
                    "API Error response",
                    {"status": response.status, "error_text": error_text},
                )
                logger.error(f"API Error: {response.status} - {error_text}")

                if response.status == 401:
                    raise ValueError(
                        "Invalid API key. Please check your Mistral API key."
                    )
                elif response.status == 429:
                    raise ValueError("Rate limit exceeded. Please try again later.")
                elif response.status == 413:
                    raise ValueError("File too large for processing.")
                else:
                    raise ValueError(f"API Error: {response.status} - {error_text}")

            debug_log("Parsing API response JSON")
            result = await response.json()
            debug_log(
                "API response parsed successfully",
                {"result_keys": list(result.keys()) if result else None},
            )

            return result

        except Exception as e:
            error_msg = str(e)
            debug_log(
                "Exception in API request",
                {"error": error_msg, "error_type": type(e).__name__},
            )

            if "Invalid API key" in error_msg or "Rate limit" in error_msg:
                raise
            else:
                raise ValueError(f"Network error: {error_msg}") from e

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

                    extracted_images.append(
                        {"name": filename, "data": image_data, "page": page_idx + 1}
                    )

        return extracted_images


# Global processor instance
processor = None


async def process_file_handler(event):
    """Handle file processing requests from JavaScript."""
    global processor

    try:
        debug_log("File processing request received")

        # Get data from JavaScript
        data = event.detail
        debug_log(
            "Event data received",
            {
                "file_name": data.get("file_name"),
                "file_type": data.get("file_type"),
                "api_key_length": len(data.get("api_key", ""))
                if data.get("api_key")
                else 0,
                "include_images": data.get("include_images"),
                "file_data_length": len(data.get("file_data", ""))
                if data.get("file_data")
                else 0,
            },
        )

        # Validate required data
        required_fields = ["file_data", "file_name", "file_type", "api_key"]
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Missing required field: {field}")

        debug_log("Data validation passed")

        # Create processor with API key
        debug_log("Creating OCR processor")
        processor = WebOCRProcessor(data["api_key"])

        # Process the file
        debug_log("Starting file processing")
        result = await processor.process_file_data(
            file_data=data["file_data"],
            file_name=data["file_name"],
            file_type=data["file_type"],
            include_images=data.get("include_images", True),
        )

        debug_log("File processing completed", {"success": result.get("success")})

        # Return result to JavaScript
        if hasattr(js, "pyScriptProcessFile"):
            debug_log("Calling JavaScript callback with result")
            js.pyScriptProcessFile(result)
        else:
            debug_log("ERROR: pyScriptProcessFile callback not found")
            js.console.error("pyScriptProcessFile callback not found in JavaScript")

    except Exception as e:
        error_msg = str(e)
        debug_log(
            "Error in process_file_handler",
            {"error": error_msg, "error_type": type(e).__name__},
        )
        logger.error(f"Error in process_file_handler: {e}")

        error_result = {
            "success": False,
            "error": error_msg,
            "markdown": "",
            "images": [],
        }

        # Try multiple ways to report the error
        if hasattr(js, "pyScriptProcessFile"):
            debug_log("Calling JavaScript callback with error result")
            js.pyScriptProcessFile(error_result)
        elif hasattr(js, "showError"):
            debug_log("Calling JavaScript showError function")
            js.showError(error_msg)
        else:
            debug_log("No JavaScript error handling found, logging to console")
            js.console.error(f"PyScript Error: {error_msg}")


# Set up event listener for file processing
js.document.addEventListener("processFile", process_file_handler)


# Add debug mode control function for JavaScript
def set_debug_mode(enabled: bool):
    """Control debug mode from JavaScript."""
    global DEBUG_MODE
    DEBUG_MODE = enabled
    debug_log(f"Debug mode {'enabled' if enabled else 'disabled'} from JavaScript")


# Expose debug mode control to JavaScript
js.pyScriptSetDebugMode = set_debug_mode

# Log that PyScript is ready
debug_log("PyScript backend initialization complete")

# Update UI to show PyScript is ready
js.console.log("✅ MarkIt Mistral PyScript backend ready")
js.console.log(
    "📝 To enable debug mode, check the 'Debug mode' checkbox in the interface"
)
js.console.log("🔧 Open browser console (F12) to see debug messages")

# Test that JavaScript communication works
try:
    js.console.log("🔗 Testing JavaScript communication...")
    if hasattr(js, "document"):
        debug_log("JavaScript document object available")
    if hasattr(js, "window"):
        debug_log("JavaScript window object available")
except Exception as e:
    js.console.error(f"JavaScript communication test failed: {e}")
