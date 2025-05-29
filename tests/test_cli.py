"""
Tests for the CLI module.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from markit_mistral.cli import create_parser, main


class TestCLIParser:
    """Test cases for CLI argument parser."""

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser.prog == "markit-mistral"

    def test_version_argument(self):
        """Test version argument."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])

    def test_help_argument(self):
        """Test help argument."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])

    def test_basic_arguments(self):
        """Test basic argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["input.pdf"])

        assert args.input == "input.pdf"
        assert args.output is None
        assert args.verbose is False
        assert args.quiet is False

    def test_output_argument(self):
        """Test output argument."""
        parser = create_parser()
        args = parser.parse_args(["input.pdf", "-o", "output.md"])

        assert args.input == "input.pdf"
        assert args.output == "output.md"

    def test_image_arguments(self):
        """Test image-related arguments."""
        parser = create_parser()

        # Test extract images
        args = parser.parse_args(["input.pdf", "--extract-images"])
        assert args.extract_images is True

        # Test no images
        args = parser.parse_args(["input.pdf", "--no-images"])
        assert args.no_images is True

        # Test base64 images
        args = parser.parse_args(["input.pdf", "--base64-images"])
        assert args.base64_images is True

    def test_output_management_arguments(self):
        """Test output management arguments."""
        parser = create_parser()

        # Test metadata arguments
        args = parser.parse_args(["input.pdf", "--no-metadata"])
        assert args.no_metadata is True

        # Test archive creation
        args = parser.parse_args(["input.pdf", "--create-archive"])
        assert args.create_archive is True

        # Test output format
        args = parser.parse_args(["input.pdf", "--output-format", "json"])
        assert args.output_format == "json"

    def test_verbose_quiet_arguments(self):
        """Test verbose and quiet arguments."""
        parser = create_parser()

        # Test verbose
        args = parser.parse_args(["input.pdf", "--verbose"])
        assert args.verbose is True

        # Test quiet
        args = parser.parse_args(["input.pdf", "--quiet"])
        assert args.quiet is True

    def test_api_key_argument(self):
        """Test API key argument."""
        parser = create_parser()
        args = parser.parse_args(["input.pdf", "--api-key", "test-key"])

        assert args.api_key == "test-key"

    def test_progress_argument(self):
        """Test progress argument."""
        parser = create_parser()
        args = parser.parse_args(["input.pdf", "--progress"])

        assert args.progress is True

    def test_batch_argument(self):
        """Test batch argument."""
        parser = create_parser()
        args = parser.parse_args(["input.pdf", "--batch"])

        assert args.batch is True


class TestCLIMain:
    """Test cases for CLI main function."""

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    def test_main_with_file_input(self, mock_config_class, mock_converter_class):
        """Test main function with file input."""
        # Setup mocks
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        mock_converter.file_processor.is_supported.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "test.pdf"
            input_file.touch()  # Create empty file
            
            # Create actual output file that CLI can read
            output_file = temp_path / "output.md"
            output_file.write_text("# Test Output\n\nThis is test content.")
            mock_converter.convert_file.return_value = output_file

            with patch("sys.argv", ["markit-mistral", str(input_file)]):
                result = main()

                assert result == 0
                mock_converter.convert_file.assert_called_once()

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    def test_main_file_not_found(self, mock_config_class, _mock_converter_class):
        """Test main function with non-existent file."""
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        with patch("sys.argv", ["markit-mistral", "nonexistent.pdf"]):
            result = main()

            assert result == 1

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    def test_main_unsupported_file(self, mock_config_class, mock_converter_class):
        """Test main function with unsupported file type."""
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        mock_converter.file_processor.is_supported.return_value = False
        mock_converter.file_processor.get_supported_extensions.return_value = [
            ".pdf",
            ".png",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "test.txt"
            input_file.touch()

            with patch("sys.argv", ["markit-mistral", str(input_file)]):
                result = main()

                assert result == 1

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    @patch("sys.stdin")
    def test_main_stdin_tty(self, mock_stdin, mock_config_class, _mock_converter_class):
        """Test main function with stdin from TTY."""
        mock_stdin.isatty.return_value = True
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        with patch("sys.argv", ["markit-mistral"]):
            result = main()

            assert result == 1

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    @patch("sys.stdin")
    def test_main_stdin_empty(
        self, mock_stdin, mock_config_class, _mock_converter_class
    ):
        """Test main function with empty stdin."""
        mock_stdin.isatty.return_value = False
        mock_stdin.buffer.read.return_value = b""
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        with patch("sys.argv", ["markit-mistral"]):
            result = main()

            assert result == 1

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    def test_main_with_verbose(self, mock_config_class, mock_converter_class):
        """Test main function with verbose flag."""
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        mock_converter.file_processor.is_supported.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "test.pdf"
            input_file.touch()
            
            # Create actual output file that CLI can read
            output_file = temp_path / "output.md"
            output_file.write_text("# Test Output\n\nThis is test content.")
            mock_converter.convert_file.return_value = output_file

            with (
                patch("sys.argv", ["markit-mistral", str(input_file), "--verbose"]),
                patch("traceback.print_exc"),
            ):
                result = main()

                assert result == 0
                assert mock_config.log_level == "DEBUG"

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    def test_main_with_quiet(self, mock_config_class, mock_converter_class):
        """Test main function with quiet flag."""
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        mock_converter.file_processor.is_supported.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "test.pdf"
            input_file.touch()
            
            # Create actual output file that CLI can read
            output_file = temp_path / "output.md"
            output_file.write_text("# Test Output\n\nThis is test content.")
            mock_converter.convert_file.return_value = output_file

            with patch("sys.argv", ["markit-mistral", str(input_file), "--quiet"]):
                result = main()

                assert result == 0
                assert mock_config.log_level == "ERROR"

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    def test_main_with_no_images(self, mock_config_class, mock_converter_class):
        """Test main function with no-images flag."""
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        mock_converter.file_processor.is_supported.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "test.pdf"
            input_file.touch()
            
            # Create actual output file that CLI can read
            output_file = temp_path / "output.md"
            output_file.write_text("# Test Output\n\nThis is test content.")
            mock_converter.convert_file.return_value = output_file

            with patch("sys.argv", ["markit-mistral", str(input_file), "--no-images"]):
                result = main()

                assert result == 0
                assert mock_config.include_images is False

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    def test_main_with_output_management(self, mock_config_class, mock_converter_class):
        """Test main function with output management flags."""
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        mock_converter = Mock()
        mock_converter.output_manager = Mock()
        mock_converter_class.return_value = mock_converter
        mock_converter.file_processor.is_supported.return_value = True

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "test.pdf"
            input_file.touch()
            
            # Create actual output file that CLI can read
            output_file = temp_path / "output.md"
            output_file.write_text("# Test Output\n\nThis is test content.")
            mock_converter.convert_file.return_value = output_file

            with patch(
                "sys.argv",
                [
                    "markit-mistral",
                    str(input_file),
                    "--no-metadata",
                    "--create-archive",
                ],
            ):
                result = main()

                assert result == 0
                assert mock_converter.output_manager.preserve_metadata is False
                assert mock_converter.output_manager.create_zip_archive is True

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    def test_main_exception_handling(self, mock_config_class, mock_converter_class):
        """Test main function exception handling."""
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        mock_converter.file_processor.is_supported.return_value = True
        mock_converter.convert_file.side_effect = Exception("Test error")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "test.pdf"
            input_file.touch()

            with patch("sys.argv", ["markit-mistral", str(input_file)]):
                result = main()

                assert result == 1

    @patch("markit_mistral.cli.MarkItMistral")
    @patch("markit_mistral.cli.Config")
    def test_main_exception_handling_verbose(
        self, mock_config_class, mock_converter_class
    ):
        """Test main function exception handling with verbose output."""
        mock_config = Mock()
        mock_config_class.from_env.return_value = mock_config

        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        mock_converter.file_processor.is_supported.return_value = True
        mock_converter.convert_file.side_effect = Exception("Test error")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_file = temp_path / "test.pdf"
            input_file.touch()

            with (
                patch("sys.argv", ["markit-mistral", str(input_file), "--verbose"]),
                patch("traceback.print_exc"),
            ):
                result = main()

                assert result == 1
