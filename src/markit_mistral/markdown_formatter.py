"""Markdown formatting and processing for markit-mistral."""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class MarkdownFormatter:
    """Handles markdown formatting, math equation processing, and image management."""

    def __init__(self, preserve_math: bool = True, base64_images: bool = False):
        """Initialize the markdown formatter.

        Args:
            preserve_math: Whether to preserve and enhance mathematical equations.
            base64_images: Whether to embed images as base64 instead of file links.
        """
        self.preserve_math = preserve_math
        self.base64_images = base64_images

    def format_document(
        self,
        pages: list[dict],
        image_paths: list[Path],
        output_dir: Path,
        document_title: str | None = None,
    ) -> str:
        """Format a complete document from OCR pages.

        Args:
            pages: List of OCR page results from Mistral API.
            image_paths: List of extracted image file paths.
            output_dir: Output directory for relative path calculation.
            document_title: Optional document title to include.

        Returns:
            Formatted markdown content.
        """
        markdown_parts = []

        # Add document title if provided
        if document_title:
            markdown_parts.append(f"# {document_title}\n")

        # Create image mapping for reference replacement
        image_map = self._create_image_map(image_paths, output_dir)

        # Process each page
        for page_idx, page in enumerate(pages):
            if hasattr(page, "markdown") and page.markdown:
                page_content = page.markdown

                # Process math equations if enabled
                if self.preserve_math:
                    page_content = self._process_math_equations(page_content)

                # Update image references
                page_content = self._update_image_references(page_content, image_map)

                # Add page separator for multi-page documents
                if page_idx > 0 and len(pages) > 1:
                    markdown_parts.append("\n---\n")

                # Clean and format the content
                page_content = self._clean_markdown_content(page_content)

                markdown_parts.append(page_content)

        # Join all parts and apply final formatting
        content = "\n\n".join(markdown_parts)
        content = self._apply_final_formatting(content)

        return content

    def _create_image_map(
        self, image_paths: list[Path], output_dir: Path
    ) -> dict[str, str]:
        """Create a mapping of image filenames to their appropriate references.

        Args:
            image_paths: List of image file paths.
            output_dir: Output directory for relative path calculation.

        Returns:
            Dictionary mapping image filenames to markdown references.
        """
        image_map = {}

        for img_path in image_paths:
            if self.base64_images:
                # Convert to base64 data URI
                try:
                    import base64

                    with open(img_path, "rb") as f:
                        img_data = f.read()

                    # Determine MIME type
                    import mimetypes

                    mime_type, _ = mimetypes.guess_type(str(img_path))
                    if not mime_type:
                        mime_type = "image/jpeg"  # default

                    base64_str = base64.b64encode(img_data).decode("utf-8")
                    data_uri = f"data:{mime_type};base64,{base64_str}"
                    image_map[img_path.name] = data_uri

                except Exception as e:
                    logger.warning(f"Failed to encode image {img_path} as base64: {e}")
                    # Fallback to file path
                    rel_path = img_path.relative_to(output_dir)
                    image_map[img_path.name] = str(rel_path)
            else:
                # Use relative file path
                rel_path = img_path.relative_to(output_dir)
                image_map[img_path.name] = str(rel_path)

        return image_map

    def _update_image_references(self, content: str, image_map: dict[str, str]) -> str:
        """Update image references in markdown content.

        Args:
            content: Markdown content with image references.
            image_map: Mapping of image filenames to their references.

        Returns:
            Updated markdown content with correct image references.
        """
        # Pattern to match markdown image syntax: ![alt](filename)
        pattern = r"!\[([^\]]*)\]\(([^)]+)\)"

        def replace_image_ref(match: re.Match[str]) -> str:
            alt_text = match.group(1)
            filename = match.group(2)

            # Try to find the image in our map
            for img_name, img_ref in image_map.items():
                if filename in img_name or img_name in filename:
                    return f"![{alt_text}]({img_ref})"

            # If no exact match, try partial matches
            for img_name, img_ref in image_map.items():
                if any(
                    part in img_name.lower() for part in filename.lower().split("_")
                ):
                    return f"![{alt_text}]({img_ref})"

            # Keep original reference if no match found
            return match.group(0)

        return re.sub(pattern, replace_image_ref, content)

    def _process_math_equations(self, content: str) -> str:
        """Process and enhance mathematical equations in the content.

        Args:
            content: Markdown content that may contain math equations.

        Returns:
            Content with processed math equations.
        """
        # Apply various math processing steps
        content = self._normalize_math_delimiters(content)
        content = self._enhance_math_formatting(content)
        content = self._fix_common_math_errors(content)

        return content

    def _normalize_math_delimiters(self, content: str) -> str:
        """Normalize mathematical equation delimiters to standard LaTeX format.

        Args:
            content: Content with potential math equations.

        Returns:
            Content with normalized math delimiters.
        """
        # Convert \(...\) to $...$
        content = re.sub(r"\\?\\\(([^)]+)\\?\\\)", r"$\1$", content)

        # Convert \[...\] to $$...$$
        content = re.sub(r"\\?\\\[([^\]]+)\\?\\\]", r"$$\1$$", content)

        # Fix malformed delimiters
        content = re.sub(r"\$\s*\$([^$]+)\$\s*\$", r"$$\1$$", content)

        # Ensure display math has proper spacing
        content = re.sub(r"([^\n])\$\$", r"\1\n$$", content)
        content = re.sub(r"\$\$([^\n])", r"$$\n\1", content)

        return content

    def _enhance_math_formatting(self, content: str) -> str:
        """Enhance mathematical formatting for better readability.

        Args:
            content: Content with math equations.

        Returns:
            Content with enhanced math formatting.
        """

        # Add proper spacing around operators in inline math
        def enhance_inline_math(match: re.Match[str]) -> str:
            math_content = match.group(1)
            # Add spaces around key operators
            math_content = re.sub(
                r"([a-zA-Z0-9])([\+\-\=])([a-zA-Z0-9])", r"\1 \2 \3", math_content
            )
            return f"${math_content}$"

        content = re.sub(r"\$([^$]+)\$", enhance_inline_math, content)

        return content

    def _fix_common_math_errors(self, content: str) -> str:
        """Fix common OCR errors in mathematical expressions.

        Args:
            content: Content with potential math errors.

        Returns:
            Content with corrected math expressions.
        """
        # Common OCR corrections for math
        corrections = {
            r"([a-zA-Z])\s*\^\s*([0-9]+)": r"\1^{\2}",  # Fix superscripts
            r"([a-zA-Z])\s*_\s*([0-9]+)": r"\1_{\2}",  # Fix subscripts
            r"\\frac\s*\{\s*([^}]+)\s*\}\s*\{\s*([^}]+)\s*\}": r"\\frac{\1}{\2}",  # Fix fractions
            r"\\sqrt\s*\{\s*([^}]+)\s*\}": r"\\sqrt{\1}",  # Fix square roots
            r"\\sum\s*_\s*\{\s*([^}]+)\s*\}\s*\^\s*\{\s*([^}]+)\s*\}": r"\\sum_{{\1}}^{{\2}}",  # Fix summations
        }

        for pattern, replacement in corrections.items():
            content = re.sub(pattern, replacement, content)

        return content

    def _clean_markdown_content(self, content: str) -> str:
        """Clean and improve markdown content formatting.

        Args:
            content: Raw markdown content.

        Returns:
            Cleaned markdown content.
        """
        # Remove excessive whitespace
        content = re.sub(r"\n\s*\n\s*\n+", "\n\n", content)

        # Fix heading formatting
        content = re.sub(r"^(#{1,6})\s*(.+)", r"\1 \2", content, flags=re.MULTILINE)

        # Ensure proper list formatting
        content = re.sub(r"^(\s*[-*+])\s+", r"\1 ", content, flags=re.MULTILINE)
        content = re.sub(r"^(\s*\d+\.)\s+", r"\1 ", content, flags=re.MULTILINE)

        # Fix table formatting
        content = self._fix_table_formatting(content)

        # Remove trailing whitespace
        content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)

        return content.strip()

    def _fix_table_formatting(self, content: str) -> str:
        """Fix markdown table formatting.

        Args:
            content: Content that may contain tables.

        Returns:
            Content with improved table formatting.
        """
        # Find potential table patterns
        lines = content.split("\n")
        in_table = False
        result_lines = []

        for line in lines:
            # Detect table rows (lines with multiple | characters)
            if "|" in line and line.count("|") >= 2:
                # Clean up the table row
                parts = [part.strip() for part in line.split("|")]
                # Remove empty parts at beginning and end
                if parts and not parts[0]:
                    parts = parts[1:]
                if parts and not parts[-1]:
                    parts = parts[:-1]

                if parts:  # If we have content
                    cleaned_line = "| " + " | ".join(parts) + " |"
                    result_lines.append(cleaned_line)
                    in_table = True
                else:
                    result_lines.append(line)
                    in_table = False
            else:
                if in_table and line.strip() == "":
                    # End of table, add spacing
                    result_lines.append("")
                result_lines.append(line)
                in_table = False

        return "\n".join(result_lines)

    def _apply_final_formatting(self, content: str) -> str:
        """Apply final formatting touches to the markdown content.

        Args:
            content: Nearly complete markdown content.

        Returns:
            Final formatted markdown content.
        """
        # Ensure proper spacing around headers
        content = re.sub(r"(^|\n)(#{1,6}\s+[^\n]+)\n(?!\n)", r"\1\2\n\n", content)

        # Ensure proper spacing around code blocks
        content = re.sub(r"(^|\n)(```[^`]*```)\n(?!\n)", r"\1\2\n\n", content)

        # Ensure proper spacing around block quotes
        content = re.sub(r"(^|\n)(>[^\n]+)\n(?!\n)", r"\1\2\n\n", content)

        # Final cleanup
        content = re.sub(r"\n{3,}", "\n\n", content)

        return content.strip() + "\n"

    def extract_metadata(self, content: str) -> dict[str, object]:
        """Extract metadata from markdown content.

        Args:
            content: Markdown content to analyze.

        Returns:
            Dictionary with extracted metadata.
        """
        metadata = {
            "word_count": len(content.split()),
            "char_count": len(content),
            "line_count": len(content.split("\n")),
            "headers": [],
            "math_equations": [],
            "images": [],
            "tables": 0,
            "links": [],
        }

        # Extract headers
        headers = re.findall(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE)
        metadata["headers"] = [(len(h[0]), h[1].strip()) for h in headers]

        # Count math equations
        inline_math = re.findall(r"\$[^$]+\$", content)
        display_math = re.findall(r"\$\$[^$]+\$\$", content)
        metadata["math_equations"] = len(inline_math) + len(display_math)

        # Extract image references
        images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content)
        metadata["images"] = images

        # Count tables
        table_lines = [
            line for line in content.split("\n") if "|" in line and line.count("|") >= 2
        ]
        metadata["tables"] = len(set(table_lines)) // 2 if table_lines else 0

        # Extract links
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        metadata["links"] = links

        return metadata
