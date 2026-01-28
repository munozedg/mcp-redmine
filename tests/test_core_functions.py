"""
Unit tests for core functions in mcp_redmine.server module.
"""
import pytest
import httpx
import yaml
from unittest.mock import Mock, patch, MagicMock
from mcp_redmine.server import request, yd


class TestRequestFunction:
    """Tests for the request() function."""

    @pytest.mark.unit
    def test_request_success_with_json_response(self, mock_env, mocker):
        """Test successful request with JSON response."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b'{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = Mock()

        mock_httpx = mocker.patch('httpx.request', return_value=mock_response)

        # Act
        result = request('/test.json', method='get')

        # Assert
        assert result['status_code'] == 200
        assert result['body'] == {"data": "test"}
        assert result['error'] == ""
        mock_httpx.assert_called_once()

    @pytest.mark.unit
    def test_request_with_parameters(self, mock_env, mocker):
        """Test request with query parameters."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b'{"issues": []}'
        mock_response.json.return_value = {"issues": []}
        mock_response.raise_for_status = Mock()

        mock_httpx = mocker.patch('httpx.request', return_value=mock_response)

        # Act
        result = request('/issues.json', method='get', params={'limit': 10})

        # Assert
        assert result['status_code'] == 200
        call_args = mock_httpx.call_args
        assert call_args.kwargs['params'] == {'limit': 10}

    @pytest.mark.unit
    def test_request_with_post_data(self, mock_env, mocker):
        """Test POST request with data."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.content = b'{"issue": {"id": 1}}'
        mock_response.json.return_value = {"issue": {"id": 1}}
        mock_response.raise_for_status = Mock()

        mock_httpx = mocker.patch('httpx.request', return_value=mock_response)

        test_data = {"issue": {"subject": "Test", "project_id": 1}}

        # Act
        result = request('/issues.json', method='post', data=test_data)

        # Assert
        assert result['status_code'] == 201
        assert result['body']['issue']['id'] == 1
        call_args = mock_httpx.call_args
        assert call_args.kwargs['json'] == test_data
        assert call_args.kwargs['method'] == 'post'

    @pytest.mark.unit
    def test_request_with_custom_content_type(self, mock_env, mocker):
        """Test request with custom content type."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 201
        mock_response.content = b'{"upload": {"token": "abc"}}'
        mock_response.json.return_value = {"upload": {"token": "abc"}}
        mock_response.raise_for_status = Mock()

        mock_httpx = mocker.patch('httpx.request', return_value=mock_response)

        # Act
        result = request('/uploads.json', method='post',
                        content_type='application/octet-stream',
                        content=b'file content')

        # Assert
        assert result['status_code'] == 201
        call_args = mock_httpx.call_args
        assert call_args.kwargs['headers']['Content-Type'] == 'application/octet-stream'
        assert call_args.kwargs['content'] == b'file content'

    @pytest.mark.unit
    def test_request_includes_api_key_header(self, mock_env, mocker):
        """Test that API key is included in request headers."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b'{}'
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()

        mock_httpx = mocker.patch('httpx.request', return_value=mock_response)

        # Act
        request('/test.json')

        # Assert
        call_args = mock_httpx.call_args
        assert call_args.kwargs['headers']['X-Redmine-API-Key'] == 'test_api_key_12345'

    @pytest.mark.unit
    def test_request_constructs_correct_url(self, mock_env, mocker):
        """Test that URL is correctly constructed."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b'{}'
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()

        mock_httpx = mocker.patch('httpx.request', return_value=mock_response)

        # Act
        request('/api/test.json')

        # Assert
        call_args = mock_httpx.call_args
        assert call_args.kwargs['url'] == 'https://test.redmine.example.com/api/test.json'

    @pytest.mark.unit
    def test_request_handles_http_error(self, mock_env, mocker):
        """Test error handling for HTTP errors."""
        # Arrange
        error_response = Mock(spec=httpx.Response)
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Not found"}
        error_response.text = '{"error": "Not found"}'

        http_error = httpx.HTTPStatusError(
            "404 Not Found",
            request=Mock(),
            response=error_response
        )

        mock_httpx = mocker.patch('httpx.request', side_effect=http_error)

        # Act
        result = request('/nonexistent.json')

        # Assert
        assert result['status_code'] == 404
        assert result['body'] == {"error": "Not found"}
        assert 'HTTPStatusError' in result['error']

    @pytest.mark.unit
    def test_request_handles_connection_error(self, mock_env, mocker):
        """Test error handling for connection errors."""
        # Arrange
        mock_httpx = mocker.patch('httpx.request',
                                 side_effect=httpx.ConnectError("Connection failed"))

        # Act
        result = request('/test.json')

        # Assert
        assert result['status_code'] == 0
        assert result['body'] is None
        assert 'ConnectError' in result['error']
        assert 'Connection failed' in result['error']

    @pytest.mark.unit
    def test_request_handles_timeout(self, mock_env, mocker):
        """Test error handling for timeouts."""
        # Arrange
        mock_httpx = mocker.patch('httpx.request',
                                 side_effect=httpx.TimeoutException("Request timed out"))

        # Act
        result = request('/test.json')

        # Assert
        assert result['status_code'] == 0
        assert 'TimeoutException' in result['error']

    @pytest.mark.unit
    def test_request_with_empty_response(self, mock_env, mocker):
        """Test request with empty response body."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 204
        mock_response.content = b''
        mock_response.raise_for_status = Mock()

        mock_httpx = mocker.patch('httpx.request', return_value=mock_response)

        # Act
        result = request('/delete.json', method='delete')

        # Assert
        assert result['status_code'] == 204
        assert result['body'] is None
        assert result['error'] == ""

    @pytest.mark.unit
    def test_request_with_non_json_response(self, mock_env, mocker):
        """Test request with non-JSON response."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b'Plain text response'
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.raise_for_status = Mock()

        mock_httpx = mocker.patch('httpx.request', return_value=mock_response)

        # Act
        result = request('/text.txt')

        # Assert
        assert result['status_code'] == 200
        assert result['body'] == b'Plain text response'
        assert result['error'] == ""

    @pytest.mark.unit
    def test_request_uses_correct_timeout(self, mock_env, mocker):
        """Test that request uses correct timeout value."""
        # Arrange
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.content = b'{}'
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()

        mock_httpx = mocker.patch('httpx.request', return_value=mock_response)

        # Act
        request('/test.json')

        # Assert
        call_args = mock_httpx.call_args
        assert call_args.kwargs['timeout'] == 60.0


class TestYdFunction:
    """Tests for the yd() YAML dump function."""

    @pytest.mark.unit
    def test_yd_converts_dict_to_yaml(self):
        """Test that yd() converts dictionary to YAML string."""
        # Arrange
        data = {"key": "value", "number": 42}

        # Act
        result = yd(data)

        # Assert
        assert isinstance(result, str)
        parsed = yaml.safe_load(result)
        assert parsed == data

    @pytest.mark.unit
    def test_yd_preserves_unicode(self):
        """Test that yd() preserves Unicode characters."""
        # Arrange
        data = {"message": "Hello 世界 🌍"}

        # Act
        result = yd(data)

        # Assert
        assert "世界" in result
        assert "🌍" in result
        parsed = yaml.safe_load(result)
        assert parsed == data

    @pytest.mark.unit
    def test_yd_preserves_key_order(self):
        """Test that yd() preserves key order (sort_keys=False)."""
        # Arrange
        data = {"z": 1, "a": 2, "m": 3}

        # Act
        result = yd(data)

        # Assert
        # Keys should appear in the order they were inserted
        lines = result.strip().split('\n')
        assert 'z:' in lines[0]
        assert 'a:' in lines[1]
        assert 'm:' in lines[2]

    @pytest.mark.unit
    def test_yd_handles_nested_structures(self):
        """Test that yd() handles nested data structures."""
        # Arrange
        data = {
            "issue": {
                "id": 1,
                "subject": "Test",
                "custom_fields": [
                    {"id": 1, "value": "test1"},
                    {"id": 2, "value": "test2"}
                ]
            }
        }

        # Act
        result = yd(data)

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed == data

    @pytest.mark.unit
    def test_yd_handles_long_lines(self):
        """Test that yd() doesn't wrap long lines (width=4096)."""
        # Arrange
        long_text = "x" * 1000
        data = {"long_field": long_text}

        # Act
        result = yd(data)

        # Assert
        # Should be on one line (no wrapping)
        assert long_text in result
        parsed = yaml.safe_load(result)
        assert parsed['long_field'] == long_text

    @pytest.mark.unit
    def test_yd_handles_empty_dict(self):
        """Test that yd() handles empty dictionary."""
        # Arrange
        data = {}

        # Act
        result = yd(data)

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed == {}

    @pytest.mark.unit
    def test_yd_handles_list(self):
        """Test that yd() handles lists."""
        # Arrange
        data = [1, 2, 3, "test"]

        # Act
        result = yd(data)

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed == data

    @pytest.mark.unit
    def test_yd_handles_none_values(self):
        """Test that yd() handles None values."""
        # Arrange
        data = {"key": None, "other": "value"}

        # Act
        result = yd(data)

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['key'] is None
        assert parsed['other'] == "value"
