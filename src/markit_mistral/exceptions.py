"""
Custom exceptions for markit-mistral.

This module defines custom exception classes for better error handling
and user-friendly error messages.
"""


class MarkItMistralError(Exception):
    """Base exception class for markit-mistral."""

    def __init__(self, message: str, details: str | None = None):
        """
        Initialize the exception.
        
        Args:
            message: Main error message.
            details: Additional details about the error.
        """
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        """Return a formatted error message."""
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class ConfigurationError(MarkItMistralError):
    """Raised when there's a configuration issue."""
    pass


class APIError(MarkItMistralError):
    """Raised when there's an API-related error."""

    def __init__(self, message: str, status_code: int | None = None, details: str | None = None):
        """
        Initialize the API error.
        
        Args:
            message: Main error message.
            status_code: HTTP status code if applicable.
            details: Additional details about the error.
        """
        super().__init__(message, details)
        self.status_code = status_code


class APIKeyError(APIError):
    """Raised when there's an API key issue."""

    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(
            message,
            details="Please set the MISTRAL_API_KEY environment variable or pass --api-key"
        )


class APIQuotaError(APIError):
    """Raised when API quota is exceeded."""

    def __init__(self, message: str = "API quota exceeded"):
        super().__init__(
            message,
            details="Please check your Mistral API usage limits and try again later"
        )


class APIRateLimitError(APIError):
    """Raised when API rate limit is hit."""

    def __init__(self, message: str = "API rate limit exceeded", retry_after: int | None = None):
        details = "Please wait before making more requests"
        if retry_after:
            details += f" (retry after {retry_after} seconds)"
        super().__init__(message, details=details)
        self.retry_after = retry_after


class FileProcessingError(MarkItMistralError):
    """Raised when there's a file processing issue."""
    pass


class UnsupportedFileTypeError(FileProcessingError):
    """Raised when trying to process an unsupported file type."""

    def __init__(self, file_path: str, supported_formats: list[str] | None = None):
        message = f"Unsupported file type: {file_path}"
        details = None
        if supported_formats:
            details = f"Supported formats: {', '.join(supported_formats)}"
        super().__init__(message, details)


class FileNotFoundError(FileProcessingError):
    """Raised when a required file is not found."""
    pass


class FileCorruptedError(FileProcessingError):
    """Raised when a file appears to be corrupted."""

    def __init__(self, file_path: str, reason: str | None = None):
        message = f"File appears to be corrupted: {file_path}"
        details = reason if reason else "Unable to read or parse the file"
        super().__init__(message, details)


class FileTooLargeError(FileProcessingError):
    """Raised when a file exceeds size limits."""

    def __init__(self, file_path: str, size_mb: float, max_size_mb: float):
        message = f"File too large: {file_path} ({size_mb:.1f} MB)"
        details = f"Maximum allowed size: {max_size_mb} MB"
        super().__init__(message, details)


class OCRProcessingError(MarkItMistralError):
    """Raised when OCR processing fails."""
    pass


class OCRTimeoutError(OCRProcessingError):
    """Raised when OCR processing times out."""

    def __init__(self, timeout_seconds: int):
        message = f"OCR processing timed out after {timeout_seconds} seconds"
        details = "Try processing a smaller file or increase the timeout limit"
        super().__init__(message, details)


class MarkdownGenerationError(MarkItMistralError):
    """Raised when markdown generation fails."""
    pass


class ImageExtractionError(MarkItMistralError):
    """Raised when image extraction fails."""
    pass


class OutputError(MarkItMistralError):
    """Raised when there's an output-related error."""
    pass


class PermissionError(OutputError):
    """Raised when there are insufficient permissions."""

    def __init__(self, path: str, operation: str = "write"):
        message = f"Permission denied: cannot {operation} to {path}"
        details = "Check file/directory permissions and try again"
        super().__init__(message, details)


class DiskSpaceError(OutputError):
    """Raised when there's insufficient disk space."""

    def __init__(self, path: str, required_mb: float | None = None):
        message = f"Insufficient disk space: {path}"
        details = None
        if required_mb:
            details = f"Required space: {required_mb:.1f} MB"
        super().__init__(message, details)


class ValidationError(MarkItMistralError):
    """Raised when input validation fails."""
    pass


class NetworkError(MarkItMistralError):
    """Raised when there's a network-related error."""

    def __init__(self, message: str = "Network error occurred"):
        details = "Check your internet connection and try again"
        super().__init__(message, details)


def handle_api_error(error: Exception) -> APIError:
    """
    Convert various API errors to appropriate custom exceptions.
    
    Args:
        error: The original exception from the API.
        
    Returns:
        Appropriate APIError subclass.
    """
    error_message = str(error).lower()

    if "api key" in error_message or "unauthorized" in error_message:
        return APIKeyError()
    elif "quota" in error_message or "limit exceeded" in error_message:
        if "rate" in error_message:
            return APIRateLimitError()
        else:
            return APIQuotaError()
    elif "timeout" in error_message:
        return NetworkError("Request timed out")
    elif "connection" in error_message or "network" in error_message:
        return NetworkError()
    else:
        return APIError(f"API request failed: {error}")


def handle_file_error(error: Exception, file_path: str) -> FileProcessingError:
    """
    Convert various file errors to appropriate custom exceptions.
    
    Args:
        error: The original exception.
        file_path: Path to the file that caused the error.
        
    Returns:
        Appropriate FileProcessingError subclass.
    """
    error_message = str(error).lower()

    if "not found" in error_message or "no such file" in error_message:
        return FileNotFoundError(f"File not found: {file_path}")
    elif "permission" in error_message or "access" in error_message:
        return PermissionError(file_path, "read")
    elif "corrupted" in error_message or "invalid" in error_message:
        return FileCorruptedError(file_path, str(error))
    elif "too large" in error_message or "size" in error_message:
        # Try to extract size information if available
        return FileTooLargeError(file_path, 0, 0)  # Will be updated by caller
    else:
        return FileProcessingError(f"File processing failed: {file_path}", str(error))


def get_user_friendly_message(error: Exception) -> str:
    """
    Get a user-friendly error message for any exception.
    
    Args:
        error: The exception to format.
        
    Returns:
        User-friendly error message.
    """
    if isinstance(error, MarkItMistralError):
        return str(error)

    # Handle common Python exceptions
    error_type = type(error).__name__
    error_message = str(error)

    if error_type == "FileNotFoundError":
        return f"File not found: {error_message}"
    elif error_type == "PermissionError":
        return f"Permission denied: {error_message}"
    elif error_type == "ConnectionError":
        return "Network connection error. Please check your internet connection."
    elif error_type == "TimeoutError":
        return "Operation timed out. Please try again."
    elif error_type == "MemoryError":
        return "Insufficient memory. Try processing a smaller file."
    else:
        return f"An unexpected error occurred: {error_message}"
