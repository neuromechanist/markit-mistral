"""Tests for the converter module's image prefix generation."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

from markit_mistral.converter import _content_hash, generate_image_prefix


class TestContentHash:
    """Test file content hashing."""

    def test_returns_hex_string(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"some pdf content")
            f.flush()
            h = _content_hash(Path(f.name))
        assert len(h) == 6
        assert all(c in "0123456789abcdef" for c in h)

    def test_different_content_different_hash(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f1:
            f1.write(b"content A")
            f1.flush()
            h1 = _content_hash(Path(f1.name))
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f2:
            f2.write(b"content B")
            f2.flush()
            h2 = _content_hash(Path(f2.name))
        assert h1 != h2

    def test_same_content_same_hash(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f1:
            f1.write(b"identical")
            f1.flush()
            h1 = _content_hash(Path(f1.name))
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f2:
            f2.write(b"identical")
            f2.flush()
            h2 = _content_hash(Path(f2.name))
        assert h1 == h2

    def test_custom_length(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"data")
            f.flush()
            h = _content_hash(Path(f.name), length=10)
        assert len(h) == 10


class TestGenerateImagePrefix:
    """Test robust image prefix generation with fallback chain."""

    def _make_page(self, markdown: str) -> Mock:
        page = Mock()
        page.markdown = markdown
        return page

    def _make_file(self, content: bytes = b"pdf data", name: str = "paper.pdf") -> Path:
        d = tempfile.mkdtemp()
        p = Path(d) / name
        p.write_bytes(content)
        return p

    def test_uses_meaningful_h1_title(self):
        pages = [self._make_page("# Treatment of Alzheimer's Disease\n\nContent.")]
        inp = self._make_file()
        out = Path("/tmp/output.md")
        prefix = generate_image_prefix(pages, inp, out)
        assert prefix.startswith("treatment-of-alzheimers-disease-")
        # Has hash suffix
        assert len(prefix.split("-")[-1]) == 6

    def test_skips_introduction_uses_h2(self):
        pages = [
            self._make_page(
                "# Introduction\n\n## Neural Network Architecture\n\nContent."
            )
        ]
        inp = self._make_file()
        out = Path("/tmp/output.md")
        prefix = generate_image_prefix(pages, inp, out)
        assert "neural-network-architecture" in prefix

    def test_skips_trivial_uses_filename(self):
        pages = [self._make_page("# Abstract\n\nSome text.")]
        inp = self._make_file(name="alzheimers-treatment-2024.pdf")
        out = Path("/tmp/output.md")
        prefix = generate_image_prefix(pages, inp, out)
        assert "alzheimers-treatment-2024" in prefix

    def test_generic_filename_uses_output_stem(self):
        pages = [self._make_page("# Introduction\n\nSome text.")]
        inp = self._make_file(name="document.pdf")
        out = Path("/tmp/my-paper.md")
        prefix = generate_image_prefix(pages, inp, out)
        assert "my-paper" in prefix

    def test_no_heading_uses_filename(self):
        pages = [self._make_page("Just plain text, no headings.")]
        inp = self._make_file(name="research-paper.pdf")
        out = Path("/tmp/output.md")
        prefix = generate_image_prefix(pages, inp, out)
        assert "research-paper" in prefix

    def test_different_files_different_prefixes(self):
        pages = [self._make_page("# Same Title\n\nContent.")]
        inp_a = self._make_file(content=b"file A content")
        inp_b = self._make_file(content=b"file B content")
        out = Path("/tmp/output.md")
        prefix_a = generate_image_prefix(pages, inp_a, out)
        prefix_b = generate_image_prefix(pages, inp_b, out)
        # Both start with the same slug but have different hashes
        assert prefix_a != prefix_b
        assert prefix_a.rsplit("-", 1)[0] == prefix_b.rsplit("-", 1)[0]

    def test_empty_pages(self):
        pages = []
        inp = self._make_file(name="my-thesis.pdf")
        out = Path("/tmp/output.md")
        prefix = generate_image_prefix(pages, inp, out)
        assert "my-thesis" in prefix

    def test_hash_suffix_always_present(self):
        pages = [self._make_page("# Good Title\n\nContent.")]
        inp = self._make_file()
        out = Path("/tmp/output.md")
        prefix = generate_image_prefix(pages, inp, out)
        parts = prefix.rsplit("-", 1)
        assert len(parts) == 2
        assert len(parts[1]) == 6
