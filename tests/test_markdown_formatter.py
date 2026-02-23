"""Tests for the markdown formatter module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

from markit_mistral.markdown_formatter import (
    MarkdownFormatter,
    extract_title_from_markdown,
    title_to_slug,
)


class TestMarkdownFormatter:
    """Test the MarkdownFormatter class."""

    def test_init_default(self):
        """Test default initialization."""
        formatter = MarkdownFormatter()

        assert formatter.preserve_math is True
        assert formatter.base64_images is False

    def test_init_custom(self):
        """Test custom initialization."""
        formatter = MarkdownFormatter(preserve_math=False, base64_images=True)

        assert formatter.preserve_math is False
        assert formatter.base64_images is True

    def test_normalize_math_delimiters(self):
        """Test math delimiter normalization."""
        formatter = MarkdownFormatter()

        # Test \(...\) to $...$
        content = r"This is \(E = mc^2\) inline math."
        result = formatter._normalize_math_delimiters(content)
        assert "$E = mc^2$" in result

        # Test \[...\] to $$...$$
        content = r"Display math: \[E = mc^2\]"
        result = formatter._normalize_math_delimiters(content)
        # The formatter adds proper spacing around display math
        assert "$$" in result and "E = mc^2" in result

    def test_enhance_math_formatting(self):
        """Test math formatting enhancement."""
        formatter = MarkdownFormatter()

        content = "The equation $E=mc^2$ is famous."
        result = formatter._enhance_math_formatting(content)
        assert "$E = mc^2$" in result or "$E=mc^2$" in result  # Should add spaces

    def test_fix_common_math_errors(self):
        """Test common math error fixing."""
        formatter = MarkdownFormatter()

        # Test superscript fixing
        content = "The formula x ^ 2 should be formatted."
        result = formatter._fix_common_math_errors(content)
        assert "x^{2}" in result

        # Test subscript fixing
        content = "The variable x _ 1 should be formatted."
        result = formatter._fix_common_math_errors(content)
        assert "x_{1}" in result

    def test_clean_markdown_content(self):
        """Test markdown content cleaning."""
        formatter = MarkdownFormatter()

        # Test excessive whitespace removal
        content = "Line 1\n\n\n\nLine 2"
        result = formatter._clean_markdown_content(content)
        assert result == "Line 1\n\nLine 2"

        # Test heading formatting
        content = "#Heading without space"
        result = formatter._clean_markdown_content(content)
        assert result == "# Heading without space"

    def test_fix_table_formatting(self):
        """Test table formatting fixes."""
        formatter = MarkdownFormatter()

        content = "|Column 1|Column 2|Column 3|\n|Value 1|Value 2|Value 3|"
        result = formatter._fix_table_formatting(content)

        assert "| Column 1 | Column 2 | Column 3 |" in result
        assert "| Value 1 | Value 2 | Value 3 |" in result

    def test_update_image_references(self):
        """Test image reference updating."""
        formatter = MarkdownFormatter()

        image_map = {"image1.png": "images/image1.png", "chart.jpg": "images/chart.jpg"}

        content = "Here is ![Image 1](image1.png) and ![Chart](chart.jpg)"
        result = formatter._update_image_references(content, image_map)

        assert "![Image 1](images/image1.png)" in result
        assert "![Chart](images/chart.jpg)" in result

    def test_extract_metadata(self):
        """Test metadata extraction."""
        formatter = MarkdownFormatter()

        content = """# Title

This is a paragraph with $E = mc^2$ inline math.

$$F = ma$$

## Section

- List item 1
- List item 2

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

![Image](image.png)

[Link](http://example.com)
"""

        metadata = formatter.extract_metadata(content)

        assert metadata["word_count"] > 0
        assert metadata["char_count"] > 0
        assert metadata["line_count"] > 0
        assert len(metadata["headers"]) >= 2  # Title and Section
        assert metadata["math_equations"] >= 2  # Inline and display math
        assert len(metadata["images"]) >= 1
        assert metadata["tables"] >= 1
        assert len(metadata["links"]) >= 1

    def test_create_image_map_file_paths(self):
        """Test creating image map with file paths."""
        formatter = MarkdownFormatter(base64_images=False)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "output"
            images_dir = output_dir / "images"
            images_dir.mkdir(parents=True)

            # Create dummy image files
            img1 = images_dir / "image1.png"
            img2 = images_dir / "chart.jpg"
            img1.write_bytes(b"dummy")
            img2.write_bytes(b"dummy")

            image_paths = [img1, img2]
            image_map = formatter._create_image_map(image_paths, output_dir)

            assert image_map["image1.png"] == "images/image1.png"
            assert image_map["chart.jpg"] == "images/chart.jpg"

    def test_format_document_simple(self):
        """Test simple document formatting."""
        formatter = MarkdownFormatter()

        # Mock page objects
        page1 = Mock()
        page1.markdown = "# Page 1\n\nThis is page 1 content."

        page2 = Mock()
        page2.markdown = "# Page 2\n\nThis is page 2 content."

        pages = [page1, page2]
        image_paths = []

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            result = formatter.format_document(
                pages=pages,
                image_paths=image_paths,
                output_dir=output_dir,
                document_title="Test Document",
            )

            assert "# Test Document" in result
            assert "# Page 1" in result
            assert "# Page 2" in result
            assert "---" in result  # Page separator

    def test_apply_final_formatting(self):
        """Test final formatting application."""
        formatter = MarkdownFormatter()

        content = "# Header\nContent without spacing\n```\ncode\n```\nMore content"
        result = formatter._apply_final_formatting(content)

        # Should have proper spacing after headers and code blocks
        assert "\n\n" in result
        assert result.endswith("\n")  # Should end with newline

    def test_enhance_math_preserves_subscripts(self):
        """Test that math enhancement does not corrupt subscripts."""
        formatter = MarkdownFormatter()

        # E_{-1} should NOT become E_{ - 1}
        content = "$E_{-1}$"
        result = formatter._enhance_math_formatting(content)
        assert result == "$E_{-1}$"

        # x^{2+3} should NOT add spaces inside braces
        content = "$x^{2+3}$"
        result = formatter._enhance_math_formatting(content)
        assert result == "$x^{2+3}$"

    def test_enhance_math_adds_spaces_at_top_level(self):
        """Test that math enhancement adds spaces at top level."""
        formatter = MarkdownFormatter()

        content = "$a+b=c$"
        result = formatter._enhance_math_formatting(content)
        assert result == "$a + b = c$"


class TestTitleExtraction:
    """Test title extraction from markdown pages."""

    def test_extract_title_from_first_heading(self):
        page = Mock()
        page.markdown = "# Treatment of Alzheimer's Disease\n\nSome content."
        assert extract_title_from_markdown([page]) == "Treatment of Alzheimer's Disease"

    def test_extract_title_no_heading(self):
        page = Mock()
        page.markdown = "No heading here, just text."
        assert extract_title_from_markdown([page]) is None

    def test_extract_title_empty_pages(self):
        assert extract_title_from_markdown([]) is None

    def test_extract_title_skips_h2(self):
        page = Mock()
        page.markdown = "## This is H2\n\nContent."
        assert extract_title_from_markdown([page]) is None

    def test_extract_title_from_second_page(self):
        page1 = Mock()
        page1.markdown = "Just a paragraph."
        page2 = Mock()
        page2.markdown = "# Title on Page Two\n\nContent."
        assert extract_title_from_markdown([page1, page2]) == "Title on Page Two"


class TestTitleToSlug:
    """Test slug generation from titles."""

    def test_basic_slug(self):
        assert (
            title_to_slug("Treatment of Alzheimer's Disease")
            == "treatment-of-alzheimers-disease"
        )

    def test_special_characters(self):
        assert (
            title_to_slug("E = mc^2: A Famous Equation!") == "e-mc2-a-famous-equation"
        )

    def test_unicode(self):
        slug = title_to_slug("Uber die Quantenmechanik")
        assert slug == "uber-die-quantenmechanik"

    def test_truncation(self):
        long_title = "A" * 100
        slug = title_to_slug(long_title)
        assert len(slug) <= 50

    def test_empty_title(self):
        assert title_to_slug("") == "document"

    def test_only_special_chars(self):
        assert title_to_slug("!!!@@@###") == "document"

    def test_collapses_hyphens(self):
        assert title_to_slug("word   --  another") == "word-another"
