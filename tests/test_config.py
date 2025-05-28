"""Tests for the configuration module."""

import os
import tempfile
from pathlib import Path

import pytest

from markit_mistral.config import Config


class TestConfig:
    """Test the Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.max_file_size_mb == 50
        assert config.include_images is True
        assert config.preserve_math is True
        assert config.base64_images is False
        assert config.log_level == "INFO"
    
    def test_from_env_with_defaults(self):
        """Test creating config from environment with no env vars set."""
        # Clear any existing environment variables
        env_vars = [
            "MISTRAL_API_KEY",
            "MARKIT_MISTRAL_MAX_RETRIES",
            "MARKIT_MISTRAL_RETRY_DELAY",
            "MARKIT_MISTRAL_MAX_FILE_SIZE_MB",
            "MARKIT_MISTRAL_INCLUDE_IMAGES",
            "MARKIT_MISTRAL_PRESERVE_MATH",
            "MARKIT_MISTRAL_BASE64_IMAGES",
            "MARKIT_MISTRAL_LOG_LEVEL",
            "MARKIT_MISTRAL_TEMP_DIR",
        ]
        
        original_values = {}
        for var in env_vars:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        
        try:
            config = Config.from_env()
            
            assert config.mistral_api_key is None
            assert config.max_retries == 3
            assert config.retry_delay == 1.0
            assert config.max_file_size_mb == 50
            assert config.include_images is True
            assert config.preserve_math is True
            assert config.base64_images is False
            assert config.log_level == "INFO"
            assert config.temp_dir is None
        
        finally:
            # Restore original environment
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
    
    def test_from_env_with_values(self):
        """Test creating config from environment with values set."""
        env_values = {
            "MISTRAL_API_KEY": "test-key",
            "MARKIT_MISTRAL_MAX_RETRIES": "5",
            "MARKIT_MISTRAL_RETRY_DELAY": "2.5",
            "MARKIT_MISTRAL_MAX_FILE_SIZE_MB": "100",
            "MARKIT_MISTRAL_INCLUDE_IMAGES": "false",
            "MARKIT_MISTRAL_PRESERVE_MATH": "false",
            "MARKIT_MISTRAL_BASE64_IMAGES": "true",
            "MARKIT_MISTRAL_LOG_LEVEL": "debug",
            "MARKIT_MISTRAL_TEMP_DIR": "/tmp/test",
        }
        
        # Save original values
        original_values = {}
        for var in env_values:
            original_values[var] = os.environ.get(var)
        
        try:
            # Set test values
            for var, value in env_values.items():
                os.environ[var] = value
            
            config = Config.from_env()
            
            assert config.mistral_api_key == "test-key"
            assert config.max_retries == 5
            assert config.retry_delay == 2.5
            assert config.max_file_size_mb == 100
            assert config.include_images is False
            assert config.preserve_math is False
            assert config.base64_images is True
            assert config.log_level == "DEBUG"
            assert config.temp_dir == Path("/tmp/test")
        
        finally:
            # Restore original environment
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
                elif var in os.environ:
                    del os.environ[var]
    
    def test_validate_success(self):
        """Test successful validation."""
        config = Config(mistral_api_key="test-key")
        config.validate()  # Should not raise
    
    def test_validate_missing_api_key(self):
        """Test validation fails with missing API key."""
        config = Config()
        
        with pytest.raises(ValueError, match="Mistral API key is required"):
            config.validate()
    
    def test_validate_invalid_retries(self):
        """Test validation fails with invalid max_retries."""
        config = Config(mistral_api_key="test-key", max_retries=0)
        
        with pytest.raises(ValueError, match="max_retries must be at least 1"):
            config.validate()
    
    def test_validate_invalid_retry_delay(self):
        """Test validation fails with invalid retry_delay."""
        config = Config(mistral_api_key="test-key", retry_delay=-1.0)
        
        with pytest.raises(ValueError, match="retry_delay must be non-negative"):
            config.validate()
    
    def test_validate_invalid_file_size(self):
        """Test validation fails with invalid max_file_size_mb."""
        config = Config(mistral_api_key="test-key", max_file_size_mb=0)
        
        with pytest.raises(ValueError, match="max_file_size_mb must be at least 1"):
            config.validate()
    
    def test_validate_invalid_log_level(self):
        """Test validation fails with invalid log level."""
        config = Config(mistral_api_key="test-key", log_level="INVALID")
        
        with pytest.raises(ValueError, match="Invalid log level: INVALID"):
            config.validate()
    
    def test_get_temp_dir(self):
        """Test getting temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Config(temp_dir=Path(temp_dir) / "test")
            
            result_dir = config.get_temp_dir()
            
            assert result_dir.exists()
            assert result_dir.is_dir()
            assert result_dir == Path(temp_dir) / "test" 