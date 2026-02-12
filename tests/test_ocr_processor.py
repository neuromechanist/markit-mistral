"""Tests for OCR processor helper functions."""

from markit_mistral.ocr_processor import _ext_from_data_uri_header


class TestExtFromDataUriHeader:
    """Test image extension detection from data URI headers."""

    def test_png(self):
        assert _ext_from_data_uri_header("data:image/png;base64") == ".png"

    def test_jpeg(self):
        assert _ext_from_data_uri_header("data:image/jpeg;base64") == ".jpg"

    def test_gif(self):
        assert _ext_from_data_uri_header("data:image/gif;base64") == ".gif"

    def test_webp(self):
        assert _ext_from_data_uri_header("data:image/webp;base64") == ".webp"

    def test_bmp(self):
        assert _ext_from_data_uri_header("data:image/bmp;base64") == ".bmp"

    def test_tiff(self):
        assert _ext_from_data_uri_header("data:image/tiff;base64") == ".tiff"

    def test_unknown_subtype_uses_subtype_as_ext(self):
        assert _ext_from_data_uri_header("data:image/avif;base64") == ".avif"

    def test_malformed_header_returns_jpg(self):
        assert _ext_from_data_uri_header("garbage") == ".jpg"

    def test_empty_header_returns_jpg(self):
        assert _ext_from_data_uri_header("") == ".jpg"
