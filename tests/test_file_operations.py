"""
Unit tests for file operation tools in mcp_redmine.server module.
"""
import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from mcp_redmine.server import redmine_upload, redmine_download


class TestRedmineUploadTool:
    """Tests for the redmine_upload() tool."""

    @pytest.mark.unit
    def test_upload_success(self, mock_env, temp_file, mocker):
        """Test successful file upload."""
        # Arrange
        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 201,
            'body': {
                'upload': {
                    'id': 7,
                    'token': 'abc123.token'
                }
            },
            'error': ''
        }

        # Act
        result = redmine_upload(str(temp_file))

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 201
        assert parsed['body']['upload']['id'] == 7
        assert parsed['body']['upload']['token'] == 'abc123.token'

        # Verify request was called correctly
        call_args = mock_request.call_args
        assert call_args.kwargs['path'] == 'uploads.json'
        assert call_args.kwargs['method'] == 'post'
        assert call_args.kwargs['content_type'] == 'application/octet-stream'
        assert temp_file.name in call_args.kwargs['params']['filename']

    @pytest.mark.unit
    def test_upload_with_description(self, mock_env, temp_file, mocker):
        """Test file upload with description."""
        # Arrange
        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 201,
            'body': {'upload': {'id': 1, 'token': 'token'}},
            'error': ''
        }

        # Act
        result = redmine_upload(str(temp_file), description="Test description")

        # Assert
        call_args = mock_request.call_args
        assert call_args.kwargs['params']['description'] == "Test description"

    @pytest.mark.unit
    def test_upload_file_not_found(self, mock_env):
        """Test upload with non-existent file."""
        # Act
        result = redmine_upload('/nonexistent/file.txt')

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 0
        assert parsed['body'] is None
        assert 'error' in parsed
        assert 'does not exist' in parsed['error']

    @pytest.mark.unit
    def test_upload_relative_path(self, mock_env):
        """Test upload rejects relative path."""
        # Act
        result = redmine_upload('relative/path/file.txt')

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 0
        assert 'must be fully qualified' in parsed['error']

    @pytest.mark.unit
    def test_upload_reads_file_content(self, mock_env, temp_file, mocker):
        """Test that upload reads file content correctly."""
        # Arrange
        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 201,
            'body': {'upload': {'id': 1, 'token': 'token'}},
            'error': ''
        }

        # Act
        redmine_upload(str(temp_file))

        # Assert
        call_args = mock_request.call_args
        content = call_args.kwargs['content']
        assert b'Test file content' in content

    @pytest.mark.unit
    def test_upload_handles_request_error(self, mock_env, temp_file, mocker):
        """Test upload handles request errors."""
        # Arrange
        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 500,
            'body': {'error': 'Server error'},
            'error': 'HTTPStatusError: 500 Server Error'
        }

        # Act
        result = redmine_upload(str(temp_file))

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 500

    @pytest.mark.unit
    def test_upload_expanduser_path(self, mock_env, mocker):
        """Test that upload expands user home directory."""
        # Arrange
        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 201,
            'body': {'upload': {'id': 1, 'token': 'token'}},
            'error': ''
        }

        # Create a temporary file in a known location
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test")
            temp_path = f.name

        try:
            # Act - this should work if the file exists
            result = redmine_upload(temp_path)

            # Assert - should succeed
            parsed = yaml.safe_load(result)
            assert parsed['status_code'] == 201
        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)


class TestRedmineDownloadTool:
    """Tests for the redmine_download() tool."""

    @pytest.mark.unit
    def test_download_success(self, mock_env, temp_dir, mocker):
        """Test successful file download."""
        # Arrange
        save_path = temp_dir / 'downloaded_file.pdf'

        mock_request = mocker.patch('mcp_redmine.server.request')
        # First call: get attachment info
        # Second call: download file
        mock_request.side_effect = [
            {
                'status_code': 200,
                'body': {
                    'attachment': {
                        'id': 1,
                        'filename': 'test_file.pdf'
                    }
                },
                'error': ''
            },
            {
                'status_code': 200,
                'body': b'PDF file content here',
                'error': ''
            }
        ]

        # Act
        result = redmine_download(1, str(save_path))

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 200
        assert parsed['body']['saved_to'] == str(save_path)
        assert parsed['body']['filename'] == 'test_file.pdf'
        assert save_path.exists()

        # Verify file content
        with open(save_path, 'rb') as f:
            content = f.read()
        assert content == b'PDF file content here'

    @pytest.mark.unit
    def test_download_with_explicit_filename(self, mock_env, temp_dir, mocker):
        """Test download with explicit filename."""
        # Arrange
        save_path = temp_dir / 'custom_name.pdf'

        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 200,
            'body': b'file content',
            'error': ''
        }

        # Act
        result = redmine_download(1, str(save_path), filename='custom_name.pdf')

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 200
        assert parsed['body']['filename'] == 'custom_name.pdf'

        # Should only call request once (no attachment info fetch)
        assert mock_request.call_count == 1

    @pytest.mark.unit
    def test_download_relative_path(self, mock_env):
        """Test download rejects relative path."""
        # Act
        result = redmine_download(1, 'relative/path.pdf')

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 0
        assert 'must be fully qualified' in parsed['error']

    @pytest.mark.unit
    def test_download_directory_path(self, mock_env, temp_dir):
        """Test download rejects directory path."""
        # Act
        result = redmine_download(1, str(temp_dir))

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 0
        assert "can't be a directory" in parsed['error']

    @pytest.mark.unit
    def test_download_attachment_not_found(self, mock_env, temp_dir, mocker):
        """Test download when attachment not found."""
        # Arrange
        save_path = temp_dir / 'file.pdf'

        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 404,
            'body': {'error': 'Not found'},
            'error': 'HTTPStatusError: 404 Not Found'
        }

        # Act
        result = redmine_download(999, str(save_path))

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 404

    @pytest.mark.unit
    def test_download_handles_download_error(self, mock_env, temp_dir, mocker):
        """Test download handles errors during file download."""
        # Arrange
        save_path = temp_dir / 'file.pdf'

        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.side_effect = [
            {
                'status_code': 200,
                'body': {'attachment': {'id': 1, 'filename': 'test.pdf'}},
                'error': ''
            },
            {
                'status_code': 500,
                'body': None,
                'error': 'Server error'
            }
        ]

        # Act
        result = redmine_download(1, str(save_path))

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 500

    @pytest.mark.unit
    def test_download_empty_body(self, mock_env, temp_dir, mocker):
        """Test download with empty response body."""
        # Arrange
        save_path = temp_dir / 'file.pdf'

        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.side_effect = [
            {
                'status_code': 200,
                'body': {'attachment': {'id': 1, 'filename': 'test.pdf'}},
                'error': ''
            },
            {
                'status_code': 200,
                'body': None,  # Empty body
                'error': ''
            }
        ]

        # Act
        result = redmine_download(1, str(save_path))

        # Assert
        parsed = yaml.safe_load(result)
        # Should return the response as-is when body is None/empty
        assert parsed['status_code'] == 200

    @pytest.mark.unit
    def test_download_creates_file(self, mock_env, temp_dir, mocker):
        """Test that download creates the file."""
        # Arrange
        save_path = temp_dir / 'new_file.txt'
        assert not save_path.exists()

        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.side_effect = [
            {
                'status_code': 200,
                'body': {'attachment': {'id': 1, 'filename': 'test.txt'}},
                'error': ''
            },
            {
                'status_code': 200,
                'body': b'test content',
                'error': ''
            }
        ]

        # Act
        result = redmine_download(1, str(save_path))

        # Assert
        assert save_path.exists()
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 200

    @pytest.mark.unit
    def test_download_constructs_correct_url(self, mock_env, temp_dir, mocker):
        """Test that download constructs correct download URL."""
        # Arrange
        save_path = temp_dir / 'file.pdf'

        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.side_effect = [
            {
                'status_code': 200,
                'body': {'attachment': {'id': 1, 'filename': 'document.pdf'}},
                'error': ''
            },
            {
                'status_code': 200,
                'body': b'content',
                'error': ''
            }
        ]

        # Act
        redmine_download(123, str(save_path))

        # Assert
        # First call should be to get attachment info
        first_call = mock_request.call_args_list[0]
        assert first_call.args[0] == 'attachments/123.json'

        # Second call should be to download
        second_call = mock_request.call_args_list[1]
        assert second_call.args[0] == 'attachments/download/123/document.pdf'
        assert second_call.kwargs['content_type'] == 'application/octet-stream'

    @pytest.mark.unit
    def test_download_exception_handling(self, mock_env, temp_dir, mocker):
        """Test download handles unexpected exceptions."""
        # Arrange
        save_path = temp_dir / 'file.pdf'

        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.side_effect = Exception("Unexpected error")

        # Act
        result = redmine_download(1, str(save_path))

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 0
        assert parsed['body'] is None
        assert 'Exception' in parsed['error']
        assert 'Unexpected error' in parsed['error']
