"""
Output management for markit-mistral.

This module handles output directory management, file naming conventions,
metadata preservation, and output format customization.
"""

import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class OutputManager:
    """
    Manages output files, directories, and metadata for markit-mistral conversions.

    Handles file naming conventions, directory structure, metadata preservation,
    and optional packaging of complete conversion results.
    """

    def __init__(
        self,
        base_output_dir: str | Path | None = None,
        preserve_metadata: bool = True,
        create_zip_archive: bool = False,
        custom_naming: str | None = None,
    ):
        """
        Initialize the output manager.

        Args:
            base_output_dir: Base directory for all outputs. If None, uses input file directory.
            preserve_metadata: Whether to save conversion metadata.
            create_zip_archive: Whether to create zip archives of complete conversions.
            custom_naming: Custom naming pattern for output files.
        """
        self.base_output_dir = Path(base_output_dir) if base_output_dir else None
        self.preserve_metadata = preserve_metadata
        self.create_zip_archive = create_zip_archive
        self.custom_naming = custom_naming

    def prepare_output_structure(
        self,
        input_path: Path,
        output_path: Path | None = None,
        include_images: bool = True,
    ) -> dict[str, Path]:
        """
        Prepare the output directory structure for a conversion.

        Args:
            input_path: Path to the input file.
            output_path: Desired output path for the markdown file.
            include_images: Whether images will be extracted.

        Returns:
            Dictionary with paths for different output components.
        """
        # Determine base output directory
        if output_path:
            output_dir = output_path.parent
            markdown_path = output_path
        else:
            output_dir = self.base_output_dir or input_path.parent
            markdown_path = self._generate_output_filename(input_path, output_dir)

        # Create directory structure
        output_dir.mkdir(parents=True, exist_ok=True)

        structure = {
            "output_dir": output_dir,
            "markdown_path": markdown_path,
            "metadata_path": output_dir / f"{markdown_path.stem}_metadata.json",
        }

        # Add images directory if needed
        if include_images:
            images_dir = output_dir / f"{markdown_path.stem}_images"
            structure["images_dir"] = images_dir

        return structure

    def _generate_output_filename(self, input_path: Path, output_dir: Path) -> Path:
        """
        Generate an appropriate output filename based on naming conventions.

        Args:
            input_path: Path to the input file.
            output_dir: Output directory.

        Returns:
            Generated output file path.
        """
        base_name = input_path.stem

        if self.custom_naming:
            # Apply custom naming pattern
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_vars = {
                "original": base_name,
                "timestamp": timestamp,
                "date": datetime.now().strftime("%Y%m%d"),
                "time": datetime.now().strftime("%H%M%S"),
            }

            try:
                filename = self.custom_naming.format(**name_vars)
            except KeyError as e:
                logger.warning(f"Invalid naming pattern variable {e}, using default")
                filename = base_name
        else:
            # Use default naming: original filename
            filename = base_name

        # Ensure .md extension
        if not filename.endswith(".md"):
            filename += ".md"

        return output_dir / filename

    def save_metadata(
        self,
        metadata_path: Path,
        conversion_metadata: dict[str, Any],
        input_info: dict[str, Any],
        processing_stats: dict[str, Any] | None = None,
    ) -> None:
        """
        Save conversion metadata to a JSON file.

        Args:
            metadata_path: Path to save the metadata file.
            conversion_metadata: Metadata extracted from the converted content.
            input_info: Information about the input file.
            processing_stats: Optional processing statistics.
        """
        if not self.preserve_metadata:
            return

        metadata = {
            "conversion_info": {
                "timestamp": datetime.now().isoformat(),
                "tool": "markit-mistral",
                "version": "0.1.0",  # TODO: Get from package
            },
            "input_file": input_info,
            "content_metadata": conversion_metadata,
        }

        if processing_stats:
            metadata["processing_stats"] = processing_stats

        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved metadata to {metadata_path}")
        except Exception as e:
            logger.warning(f"Failed to save metadata: {e}")

    def create_archive(
        self,
        output_structure: dict[str, Path],
        archive_path: Path | None = None,
    ) -> Path | None:
        """
        Create a zip archive containing all conversion outputs.

        Args:
            output_structure: Dictionary with paths to output files.
            archive_path: Path for the archive. If None, generates automatically.

        Returns:
            Path to the created archive, or None if creation failed.
        """
        if not self.create_zip_archive:
            return None

        try:
            if archive_path is None:
                markdown_path = output_structure["markdown_path"]
                archive_path = (
                    markdown_path.parent / f"{markdown_path.stem}_complete.zip"
                )

            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add markdown file
                if output_structure["markdown_path"].exists():
                    zipf.write(
                        output_structure["markdown_path"],
                        output_structure["markdown_path"].name,
                    )

                # Add metadata file
                if (
                    "metadata_path" in output_structure
                    and output_structure["metadata_path"].exists()
                ):
                    zipf.write(
                        output_structure["metadata_path"],
                        output_structure["metadata_path"].name,
                    )

                # Add images directory
                if (
                    "images_dir" in output_structure
                    and output_structure["images_dir"].exists()
                ):
                    images_dir = output_structure["images_dir"]
                    for image_file in images_dir.iterdir():
                        if image_file.is_file():
                            zipf.write(
                                image_file, f"{images_dir.name}/{image_file.name}"
                            )

            logger.info(f"Created archive: {archive_path}")
            return archive_path

        except Exception as e:
            logger.error(f"Failed to create archive: {e}")
            return None

    def cleanup_temporary_files(self, temp_paths: list[Path]) -> None:
        """
        Clean up temporary files created during processing.

        Args:
            temp_paths: List of temporary file paths to remove.
        """
        for temp_path in temp_paths:
            try:
                if temp_path.exists():
                    if temp_path.is_file():
                        temp_path.unlink()
                    elif temp_path.is_dir():
                        # Remove directory and contents
                        import shutil

                        shutil.rmtree(temp_path)
                    logger.debug(f"Cleaned up temporary file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {temp_path}: {e}")

    def validate_output_permissions(self, output_dir: Path) -> bool:
        """
        Validate that we have write permissions to the output directory.

        Args:
            output_dir: Directory to check.

        Returns:
            True if we can write to the directory, False otherwise.
        """
        try:
            # Try to create a temporary file
            test_file = output_dir / ".markit_mistral_test"
            test_file.touch()
            test_file.unlink()
            return True
        except Exception:
            return False

    def get_output_summary(self, output_structure: dict[str, Path]) -> dict[str, Any]:
        """
        Generate a summary of the output files created.

        Args:
            output_structure: Dictionary with paths to output files.

        Returns:
            Summary information about the outputs.
        """
        summary = {
            "files_created": [],
            "total_size_bytes": 0,
            "images_count": 0,
        }

        for key, path in output_structure.items():
            if path.exists():
                if path.is_file():
                    size = path.stat().st_size
                    summary["files_created"].append(
                        {
                            "type": key,
                            "path": str(path),
                            "size_bytes": size,
                        }
                    )
                    summary["total_size_bytes"] += size
                elif path.is_dir() and "images" in key:
                    # Count images in directory
                    image_files = [f for f in path.iterdir() if f.is_file()]
                    summary["images_count"] = len(image_files)

                    for img_file in image_files:
                        size = img_file.stat().st_size
                        summary["files_created"].append(
                            {
                                "type": "image",
                                "path": str(img_file),
                                "size_bytes": size,
                            }
                        )
                        summary["total_size_bytes"] += size

        return summary
