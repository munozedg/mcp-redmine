"""
Unit tests for health check server in mcp_redmine.server module.
"""
import pytest
import socket
import time
import json
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from mcp_redmine.server import HealthCheckHandler, start_health_server


class TestHealthCheckHandler:
    """Tests for the HealthCheckHandler class."""

    def _create_handler(self, path='/'):
        """Helper to create a handler instance without calling __init__."""
        # Create instance without calling __init__ to avoid socket issues
        handler = HealthCheckHandler.__new__(HealthCheckHandler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = BytesIO()
        handler.path = path
        return handler

    @pytest.mark.unit
    def test_health_check_get_root(self):
        """Test GET request to root path."""
        # Arrange
        handler = self._create_handler('/')

        # Act
        handler.do_GET()

        # Assert
        handler.send_response.assert_called_once_with(200)
        handler.send_header.assert_called_with('Content-type', 'application/json')
        handler.end_headers.assert_called_once()

        # Check response body
        response_data = handler.wfile.getvalue()
        response_json = json.loads(response_data.decode())
        assert response_json['status'] == 'ok'
        assert response_json['service'] == 'mcp-redmine'

    @pytest.mark.unit
    def test_health_check_get_health_path(self):
        """Test GET request to /health path."""
        # Arrange
        handler = self._create_handler('/health')

        # Act
        handler.do_GET()

        # Assert
        handler.send_response.assert_called_once_with(200)
        response_data = handler.wfile.getvalue()
        response_json = json.loads(response_data.decode())
        assert response_json['status'] == 'ok'

    @pytest.mark.unit
    def test_health_check_get_404(self):
        """Test GET request to unknown path returns 404."""
        # Arrange
        handler = self._create_handler('/unknown')

        # Act
        handler.do_GET()

        # Assert
        handler.send_response.assert_called_once_with(404)
        handler.end_headers.assert_called_once()

    @pytest.mark.unit
    def test_health_check_head_root(self):
        """Test HEAD request to root path."""
        # Arrange
        handler = self._create_handler('/')

        # Act
        handler.do_HEAD()

        # Assert
        handler.send_response.assert_called_once_with(200)
        handler.send_header.assert_called_with('Content-type', 'application/json')

    @pytest.mark.unit
    def test_health_check_head_health_path(self):
        """Test HEAD request to /health path."""
        # Arrange
        handler = self._create_handler('/health')

        # Act
        handler.do_HEAD()

        # Assert
        handler.send_response.assert_called_once_with(200)

    @pytest.mark.unit
    def test_health_check_head_404(self):
        """Test HEAD request to unknown path returns 404."""
        # Arrange
        handler = self._create_handler('/unknown')

        # Act
        handler.do_HEAD()

        # Assert
        handler.send_response.assert_called_once_with(404)

    @pytest.mark.unit
    def test_log_message_suppressed(self):
        """Test that log messages are suppressed."""
        # Arrange
        handler = self._create_handler('/')

        # Act & Assert - should not raise any exceptions
        handler.log_message("Test %s", "message")
        # If no exception, test passes (logs are suppressed)


class TestStartHealthServer:
    """Tests for the start_health_server() function."""

    @pytest.mark.unit
    def test_start_health_server_success(self, mocker):
        """Test successful health server startup."""
        # Arrange
        mock_server = Mock()
        mock_server.serve_forever = Mock()
        mock_httpserver = mocker.patch('mcp_redmine.server.HTTPServer', return_value=mock_server)
        mock_thread = mocker.patch('mcp_redmine.server.threading.Thread')
        mock_socket = mocker.patch('mcp_redmine.server.socket.socket')
        mock_socket_instance = Mock()
        mock_socket_instance.connect_ex.return_value = 0  # Success
        mock_socket.return_value = mock_socket_instance

        # Act
        result = start_health_server(port=9999)

        # Assert
        assert result == mock_server
        mock_httpserver.assert_called_once_with(('0.0.0.0', 9999), HealthCheckHandler)
        mock_thread.assert_called_once()
        assert mock_thread.call_args.kwargs['daemon'] is True

    @pytest.mark.unit
    def test_start_health_server_binds_to_all_interfaces(self, mocker):
        """Test that server binds to 0.0.0.0."""
        # Arrange
        mock_server = Mock()
        mock_httpserver = mocker.patch('mcp_redmine.server.HTTPServer', return_value=mock_server)
        mock_thread = mocker.patch('mcp_redmine.server.threading.Thread')
        mock_socket = mocker.patch('mcp_redmine.server.socket.socket')
        mock_socket_instance = Mock()
        mock_socket_instance.connect_ex.return_value = 0
        mock_socket.return_value = mock_socket_instance

        # Act
        start_health_server(port=8080)

        # Assert
        call_args = mock_httpserver.call_args
        server_address = call_args.args[0]
        assert server_address == ('0.0.0.0', 8080)

    @pytest.mark.unit
    def test_start_health_server_default_port(self, mocker):
        """Test default port is 8080."""
        # Arrange
        mock_server = Mock()
        mock_httpserver = mocker.patch('mcp_redmine.server.HTTPServer', return_value=mock_server)
        mock_thread = mocker.patch('mcp_redmine.server.threading.Thread')
        mock_socket = mocker.patch('mcp_redmine.server.socket.socket')
        mock_socket_instance = Mock()
        mock_socket_instance.connect_ex.return_value = 0
        mock_socket.return_value = mock_socket_instance

        # Act
        start_health_server()

        # Assert
        call_args = mock_httpserver.call_args
        server_address = call_args.args[0]
        assert server_address[1] == 8080

    @pytest.mark.unit
    def test_start_health_server_exception(self, mocker):
        """Test health server handles exceptions during startup."""
        # Arrange
        mocker.patch('mcp_redmine.server.HTTPServer', side_effect=OSError("Port in use"))

        # Act
        result = start_health_server(port=8080)

        # Assert
        assert result is None

    @pytest.mark.unit
    def test_start_health_server_thread_is_daemon(self, mocker):
        """Test that server thread is daemon thread."""
        # Arrange
        mock_server = Mock()
        mocker.patch('mcp_redmine.server.HTTPServer', return_value=mock_server)
        mock_thread_class = mocker.patch('mcp_redmine.server.threading.Thread')
        mock_socket = mocker.patch('mcp_redmine.server.socket.socket')
        mock_socket_instance = Mock()
        mock_socket_instance.connect_ex.return_value = 0
        mock_socket.return_value = mock_socket_instance

        # Act
        start_health_server()

        # Assert
        # Verify Thread was created with daemon=True
        call_kwargs = mock_thread_class.call_args.kwargs
        assert call_kwargs['daemon'] is True

    @pytest.mark.unit
    def test_start_health_server_verification_retry(self, mocker):
        """Test server verification with retries."""
        # Arrange
        mock_server = Mock()
        mocker.patch('mcp_redmine.server.HTTPServer', return_value=mock_server)
        mocker.patch('mcp_redmine.server.threading.Thread')

        mock_socket = mocker.patch('mcp_redmine.server.socket.socket')
        mock_socket_instance = Mock()
        # First 3 attempts fail, 4th succeeds
        mock_socket_instance.connect_ex.side_effect = [1, 1, 1, 0]
        mock_socket.return_value = mock_socket_instance

        mock_time = mocker.patch('mcp_redmine.server.time.sleep')

        # Act
        result = start_health_server()

        # Assert
        assert result == mock_server
        assert mock_socket_instance.connect_ex.call_count == 4
        assert mock_time.call_count >= 3  # Should sleep between retries

    @pytest.mark.unit
    def test_start_health_server_verification_max_attempts(self, mocker):
        """Test server verification respects max attempts."""
        # Arrange
        mock_server = Mock()
        mocker.patch('mcp_redmine.server.HTTPServer', return_value=mock_server)
        mocker.patch('mcp_redmine.server.threading.Thread')

        mock_socket = mocker.patch('mcp_redmine.server.socket.socket')
        mock_socket_instance = Mock()
        # All attempts fail
        mock_socket_instance.connect_ex.return_value = 1
        mock_socket.return_value = mock_socket_instance

        mocker.patch('mcp_redmine.server.time.sleep')

        # Act
        result = start_health_server()

        # Assert
        # Should still return server even if verification fails
        assert result == mock_server
        # Should attempt max_attempts times (10)
        assert mock_socket_instance.connect_ex.call_count == 10

    @pytest.mark.unit
    def test_start_health_server_sets_socket_timeout(self, mocker):
        """Test that socket timeout is set for verification."""
        # Arrange
        mock_server = Mock()
        mocker.patch('mcp_redmine.server.HTTPServer', return_value=mock_server)
        mocker.patch('mcp_redmine.server.threading.Thread')

        mock_socket = mocker.patch('mcp_redmine.server.socket.socket')
        mock_socket_instance = Mock()
        mock_socket_instance.connect_ex.return_value = 0
        mock_socket.return_value = mock_socket_instance

        # Act
        start_health_server()

        # Assert
        mock_socket_instance.settimeout.assert_called_with(1)
        mock_socket_instance.close.assert_called()


class TestHealthCheckIntegration:
    """Integration tests for health check functionality."""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_health_server_actual_startup(self):
        """Test actual health server can start and respond."""
        # This test actually starts a server (integration test)
        # Arrange
        port = 19999  # Use high port to avoid conflicts

        # Act
        from mcp_redmine.server import start_health_server
        server = start_health_server(port=port)

        try:
            # Give server time to start
            time.sleep(0.5)

            # Try to connect
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()

            # Assert
            assert server is not None
            assert result == 0  # Connection successful
        finally:
            # Cleanup
            if server:
                server.shutdown()
