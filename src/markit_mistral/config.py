"""Configuration management for markit-mistral."""

import logging
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Configuration settings for markit-mistral."""

    # API Configuration
    mistral_api_key: str | None = None

    # Processing Configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    max_file_size_mb: int = 50

    # Output Configuration
    include_images: bool = True
    preserve_math: bool = True
    base64_images: bool = False

    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Directories
    temp_dir: Path | None = None

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            mistral_api_key=os.getenv("MISTRAL_API_KEY"),
            max_retries=int(os.getenv("MARKIT_MISTRAL_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("MARKIT_MISTRAL_RETRY_DELAY", "1.0")),
            max_file_size_mb=int(os.getenv("MARKIT_MISTRAL_MAX_FILE_SIZE_MB", "50")),
            include_images=os.getenv("MARKIT_MISTRAL_INCLUDE_IMAGES", "true").lower() == "true",
            preserve_math=os.getenv("MARKIT_MISTRAL_PRESERVE_MATH", "true").lower() == "true",
            base64_images=os.getenv("MARKIT_MISTRAL_BASE64_IMAGES", "false").lower() == "true",
            log_level=os.getenv("MARKIT_MISTRAL_LOG_LEVEL", "INFO").upper(),
            temp_dir=Path(os.getenv("MARKIT_MISTRAL_TEMP_DIR", "/tmp/markit-mistral")) if os.getenv("MARKIT_MISTRAL_TEMP_DIR") else None,
        )

    def setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format=self.log_format,
            handlers=[
                logging.StreamHandler(),
            ]
        )

        # Set library loggers to WARNING to reduce noise
        logging.getLogger("mistralai").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)

    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.mistral_api_key:
            raise ValueError(
                "Mistral API key is required. Set MISTRAL_API_KEY environment variable."
            )

        if self.max_retries < 1:
            raise ValueError("max_retries must be at least 1")

        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")

        if self.max_file_size_mb < 1:
            raise ValueError("max_file_size_mb must be at least 1")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {self.log_level}")

    def get_temp_dir(self) -> Path:
        """Get temporary directory, creating it if necessary."""
        if self.temp_dir is None:
            self.temp_dir = Path("/tmp") / "markit-mistral"

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        return self.temp_dir
