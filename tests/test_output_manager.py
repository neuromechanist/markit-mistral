"""Tests for the OutputManager class."""

import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch

from markit_mistral.output_manager import OutputManager


class TestOutputManager:
    """Test cases for OutputManager."""

    def test_init_default(self):
        """Test OutputManager initialization with defaults."""
        manager = OutputManager()

        assert manager.base_output_dir is None
        assert manager.preserve_metadata is True
        assert manager.create_zip_archive is False
        assert manager.custom_naming is None

    def test_init_custom(self):
        """Test OutputManager initialization with custom values."""
        base_dir = Path("/tmp/test")
        manager = OutputManager(
            base_output_dir=base_dir,
            preserve_metadata=False,
            create_zip_archive=True,
            custom_naming="{original}_{timestamp}",
        )

        assert manager.base_output_dir == base_dir
        assert manager.preserve_metadata is False
        assert manager.create_zip_archive is True
        assert manager.custom_naming == "{original}_{timestamp}"

    def test_prepare_output_structure_with_output_path(self):
        """Test preparing output structure with specified output path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "test.pdf"
            output_path = temp_path / "output.md"

            manager = OutputManager()
            structure = manager.prepare_output_structure(
                input_path=input_path,
                output_path=output_path,
                include_images=True,
            )

            assert structure["output_dir"] == output_path.parent
            assert structure["markdown_path"] == output_path
            assert structure["metadata_path"] == temp_path / "output_metadata.json"
            assert structure["images_dir"] == temp_path / "output_images"

    def test_prepare_output_structure_without_output_path(self):
        """Test preparing output structure without specified output path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "test.pdf"

            manager = OutputManager(base_output_dir=temp_path)
            structure = manager.prepare_output_structure(
                input_path=input_path,
                include_images=False,
            )

            assert structure["output_dir"] == temp_path
            assert structure["markdown_path"] == temp_path / "test.md"
            assert structure["metadata_path"] == temp_path / "test_metadata.json"
            assert "images_dir" not in structure

    def test_generate_output_filename_default(self):
        """Test default filename generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "document.pdf"

            manager = OutputManager()
            filename = manager._generate_output_filename(input_path, temp_path)

            assert filename == temp_path / "document.md"

    def test_generate_output_filename_custom(self):
        """Test custom filename generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "document.pdf"

            manager = OutputManager(custom_naming="{original}_converted")
            filename = manager._generate_output_filename(input_path, temp_path)

            assert filename == temp_path / "document_converted.md"

    @patch("markit_mistral.output_manager.datetime")
    def test_generate_output_filename_with_timestamp(self, mock_datetime):
        """Test filename generation with timestamp."""
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "document.pdf"

            manager = OutputManager(custom_naming="{original}_{timestamp}")
            filename = manager._generate_output_filename(input_path, temp_path)

            assert filename == temp_path / "document_20240101_120000.md"

    def test_save_metadata(self):
        """Test metadata saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            metadata_path = temp_path / "metadata.json"

            manager = OutputManager(preserve_metadata=True)

            conversion_metadata = {"word_count": 100, "images": 2}
            input_info = {"name": "test.pdf", "size_mb": 1.5}
            processing_stats = {"processing_time": 5.2}

            manager.save_metadata(
                metadata_path=metadata_path,
                conversion_metadata=conversion_metadata,
                input_info=input_info,
                processing_stats=processing_stats,
            )

            assert metadata_path.exists()

            with open(metadata_path, encoding="utf-8") as f:
                saved_metadata = json.load(f)

            assert "conversion_info" in saved_metadata
            assert saved_metadata["input_file"] == input_info
            assert saved_metadata["content_metadata"] == conversion_metadata
            assert saved_metadata["processing_stats"] == processing_stats

    def test_save_metadata_disabled(self):
        """Test that metadata is not saved when disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            metadata_path = temp_path / "metadata.json"

            manager = OutputManager(preserve_metadata=False)

            manager.save_metadata(
                metadata_path=metadata_path,
                conversion_metadata={},
                input_info={},
            )

            assert not metadata_path.exists()

    def test_create_archive(self):
        """Test zip archive creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            markdown_path = temp_path / "test.md"
            metadata_path = temp_path / "test_metadata.json"
            images_dir = temp_path / "test_images"
            image_path = images_dir / "image1.jpg"

            markdown_path.write_text("# Test Document")
            metadata_path.write_text('{"test": true}')
            images_dir.mkdir()
            image_path.write_bytes(b"fake image data")

            output_structure = {
                "markdown_path": markdown_path,
                "metadata_path": metadata_path,
                "images_dir": images_dir,
            }

            manager = OutputManager(create_zip_archive=True)
            archive_path = manager.create_archive(output_structure)

            assert archive_path is not None
            assert archive_path.exists()
            assert archive_path.suffix == ".zip"

            # Verify archive contents
            with zipfile.ZipFile(archive_path, "r") as zipf:
                names = zipf.namelist()
                assert "test.md" in names
                assert "test_metadata.json" in names
                assert "test_images/image1.jpg" in names

    def test_create_archive_disabled(self):
        """Test that archive is not created when disabled."""
        manager = OutputManager(create_zip_archive=False)
        result = manager.create_archive({})

        assert result is None

    def test_validate_output_permissions(self):
        """Test output permissions validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            manager = OutputManager()

            # Should have permissions in temp directory
            assert manager.validate_output_permissions(temp_path) is True

            # Should not have permissions in non-existent directory
            non_existent = temp_path / "non_existent"
            assert manager.validate_output_permissions(non_existent) is False

    def test_cleanup_temporary_files(self):
        """Test temporary file cleanup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files and directories
            temp_file = temp_path / "temp_file.txt"
            temp_dir_path = temp_path / "temp_dir"
            temp_subfile = temp_dir_path / "subfile.txt"

            temp_file.write_text("temporary content")
            temp_dir_path.mkdir()
            temp_subfile.write_text("sub content")

            manager = OutputManager()
            manager.cleanup_temporary_files([temp_file, temp_dir_path])

            assert not temp_file.exists()
            assert not temp_dir_path.exists()

    def test_get_output_summary(self):
        """Test output summary generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            markdown_path = temp_path / "test.md"
            images_dir = temp_path / "test_images"
            image_path = images_dir / "image1.jpg"

            markdown_path.write_text("# Test Document")
            images_dir.mkdir()
            image_path.write_bytes(b"fake image data")

            output_structure = {
                "markdown_path": markdown_path,
                "images_dir": images_dir,
            }

            manager = OutputManager()
            summary = manager.get_output_summary(output_structure)

            assert summary["images_count"] == 1
            assert summary["total_size_bytes"] > 0
            assert len(summary["files_created"]) == 2  # markdown + image

            # Check file types
            file_types = [f["type"] for f in summary["files_created"]]
            assert "markdown_path" in file_types
            assert "image" in file_types
