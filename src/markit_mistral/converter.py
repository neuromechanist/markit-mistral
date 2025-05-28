"""
Main converter class for markit-mistral.

This module provides the MarkItMistral class which orchestrates the conversion
of PDF and image files to markdown using Mistral AI OCR.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from .config import Config
from .file_processor import create_file_processor
from .ocr_processor import OCRProcessor

logger = logging.getLogger(__name__)


class MarkItMistral:
    """
    Main converter class for PDF and image to markdown conversion.
    
    Uses Mistral AI OCR to extract text and preserves mathematical equations
    and images in the output markdown.
    """
    
    def __init__(
        self,
        config: Optional[Config] = None,
        api_key: Optional[str] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        include_images: Optional[bool] = None,
        preserve_math: Optional[bool] = None,
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
        self.ocr_processor = OCRProcessor(
            api_key=self.config.mistral_api_key,
            max_retries=self.config.max_retries,
            retry_delay=self.config.retry_delay,
            max_file_size_mb=self.config.max_file_size_mb,
        )
        self.file_processor = create_file_processor()

    def convert_file(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        output_dir: Optional[Union[str, Path]] = None,
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
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Determine output paths
        if output_path is None:
            if output_dir is None:
                output_dir = input_path.parent
            else:
                output_dir = Path(output_dir)
            
            output_path = output_dir / f"{input_path.stem}.md"
        else:
            output_path = Path(output_path)
            output_dir = output_path.parent
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Converting {input_path} to {output_path}")
        
        # Process the file based on its type
        if input_path.suffix.lower() == '.pdf':
            response = self.ocr_processor.process_pdf(input_path, self.config.include_images)
        elif input_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']:
            response = self.ocr_processor.process_image(input_path, self.config.include_images)
        else:
            raise ValueError(f"Unsupported file type: {input_path.suffix}")
        
        # Extract and save images if requested
        image_paths = []
        if self.config.include_images:
            image_paths = self.ocr_processor.extract_images(response, output_dir)
        
        # Generate markdown content
        markdown_content = self._generate_markdown(response, image_paths, output_dir)
        
        # Apply math equation processing if enabled
        if self.config.preserve_math:
            markdown_content = self._process_math_equations(markdown_content)
        
        # Write markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully converted to {output_path}")
        return output_path

    def convert_url(
        self,
        url: str,
        output_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
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
        
        if output_dir is None:
            output_dir = output_path.parent
        else:
            output_dir = Path(output_dir)
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Converting URL {url} to {output_path}")
        
        # Process the URL
        response = self.ocr_processor.process_url(url, self.config.include_images)
        
        # Extract and save images if requested
        image_paths = []
        if self.config.include_images:
            image_paths = self.ocr_processor.extract_images(response, output_dir)
        
        # Generate markdown content
        markdown_content = self._generate_markdown(response, image_paths, output_dir)
        
        # Apply math equation processing if enabled
        if self.config.preserve_math:
            markdown_content = self._process_math_equations(markdown_content)
        
        # Write markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Successfully converted URL to {output_path}")
        return output_path

    def _generate_markdown(
        self,
        response: Dict,
        image_paths: List[Path],
        output_dir: Path,
    ) -> str:
        """
        Generate markdown content from OCR response.
        
        Args:
            response: OCR response from Mistral API.
            image_paths: List of extracted image file paths.
            output_dir: Output directory for relative path calculation.
            
        Returns:
            Generated markdown content.
        """
        markdown_parts = []
        
        # Create a mapping of image IDs to relative paths
        image_map = {}
        for img_path in image_paths:
            # Use relative path from output directory
            rel_path = img_path.relative_to(output_dir)
            image_map[img_path.name] = str(rel_path)
        
        # Process each page
        for page_idx, page in enumerate(response.pages):
            if hasattr(page, 'markdown') and page.markdown:
                page_content = page.markdown
                
                # Update image references to use relative paths
                page_content = self._update_image_references(page_content, image_map)
                
                # Add page separator for multi-page documents
                if page_idx > 0:
                    markdown_parts.append("\n---\n")
                
                markdown_parts.append(page_content)
        
        return "\n\n".join(markdown_parts)

    def _update_image_references(self, content: str, image_map: Dict[str, str]) -> str:
        """
        Update image references in markdown content.
        
        Args:
            content: Markdown content with image references.
            image_map: Mapping of image filenames to relative paths.
            
        Returns:
            Updated markdown content with correct image paths.
        """
        # Pattern to match markdown image syntax: ![alt](filename)
        pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        def replace_image_ref(match):
            alt_text = match.group(1)
            filename = match.group(2)
            
            # If we have a mapping for this filename, use the relative path
            if filename in image_map:
                return f"![{alt_text}]({image_map[filename]})"
            else:
                # Keep original reference
                return match.group(0)
        
        return re.sub(pattern, replace_image_ref, content)

    def _process_math_equations(self, content: str) -> str:
        """
        Process and enhance mathematical equations in the content.
        
        Args:
            content: Markdown content that may contain math equations.
            
        Returns:
            Content with processed math equations.
        """
        # Mistral OCR should already preserve LaTeX math syntax
        # This method can be extended to:
        # 1. Validate math syntax
        # 2. Convert between different math formats
        # 3. Add math rendering hints
        
        # For now, we'll ensure proper LaTeX delimiters
        content = self._normalize_math_delimiters(content)
        
        return content

    def _normalize_math_delimiters(self, content: str) -> str:
        """
        Normalize mathematical equation delimiters.
        
        Args:
            content: Content with potential math equations.
            
        Returns:
            Content with normalized math delimiters.
        """
        # Convert various math delimiters to standard LaTeX format
        
        # Inline math: $...$ (keep as is, this is standard)
        # Display math: $$...$$ (keep as is, this is standard)
        
        # Convert \(...\) to $...$
        content = re.sub(r'\\\\?\(([^)]+)\\\\?\)', r'$\1$', content)
        
        # Convert \[...\] to $$...$$
        content = re.sub(r'\\\\?\[([^\]]+)\\\\?\]', r'$$\1$$', content)
        
        return content

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported input file formats.
        
        Returns:
            List of supported file extensions.
        """
        return ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']

    def validate_input(self, input_path: Union[str, Path]) -> bool:
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

    def get_file_info(self, input_path: Union[str, Path]) -> Dict[str, Union[str, int, float]]:
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