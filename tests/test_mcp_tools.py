"""
Unit tests for MCP tool functions in mcp_redmine.server module.
"""
import pytest
import yaml
from unittest.mock import Mock, patch, MagicMock
from mcp_redmine.server import (
    redmine_request,
    redmine_paths_list,
    redmine_paths_info,
)


class TestRedmineRequestTool:
    """Tests for the redmine_request() tool."""

    @pytest.mark.unit
    def test_redmine_request_success(self, mock_env, mocker):
        """Test successful Redmine request."""
        # Arrange
        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 200,
            'body': {'projects': [{'id': 1, 'name': 'Test'}]},
            'error': ''
        }

        # Act
        result = redmine_request('/projects.json', method='get')

        # Assert
        assert isinstance(result, str)
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 200
        assert parsed['body']['projects'][0]['name'] == 'Test'
        mock_request.assert_called_once_with('/projects.json', method='get', data=None, params=None)

    @pytest.mark.unit
    def test_redmine_request_with_params(self, mock_env, mocker):
        """Test Redmine request with query parameters."""
        # Arrange
        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 200,
            'body': {'issues': []},
            'error': ''
        }

        # Act
        result = redmine_request('/issues.json', method='get', params={'limit': 10, 'offset': 5})

        # Assert
        mock_request.assert_called_once_with(
            '/issues.json',
            method='get',
            data=None,
            params={'limit': 10, 'offset': 5}
        )

    @pytest.mark.unit
    def test_redmine_request_with_post_data(self, mock_env, mocker):
        """Test Redmine POST request with data."""
        # Arrange
        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 201,
            'body': {'issue': {'id': 1}},
            'error': ''
        }

        post_data = {'issue': {'subject': 'Test', 'project_id': 1}}

        # Act
        result = redmine_request('/issues.json', method='post', data=post_data)

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 201
        mock_request.assert_called_once_with(
            '/issues.json',
            method='post',
            data=post_data,
            params=None
        )

    @pytest.mark.unit
    def test_redmine_request_error_response(self, mock_env, mocker):
        """Test Redmine request with error response."""
        # Arrange
        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {
            'status_code': 404,
            'body': {'error': 'Not found'},
            'error': 'HTTPStatusError: 404 Not Found'
        }

        # Act
        result = redmine_request('/nonexistent.json')

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['status_code'] == 404
        assert 'error' in parsed['body']
        assert parsed['error'] != ''

    @pytest.mark.unit
    def test_redmine_request_default_method(self, mock_env, mocker):
        """Test that redmine_request defaults to GET method."""
        # Arrange
        mock_request = mocker.patch('mcp_redmine.server.request')
        mock_request.return_value = {'status_code': 200, 'body': {}, 'error': ''}

        # Act
        redmine_request('/test.json')

        # Assert
        call_args = mock_request.call_args
        assert call_args.kwargs['method'] == 'get'


class TestRedminePathsListTool:
    """Tests for the redmine_paths_list() tool."""

    @pytest.mark.unit
    def test_redmine_paths_list_returns_yaml(self, mock_env, mocker):
        """Test that redmine_paths_list returns YAML string."""
        # Arrange
        mock_spec = {
            'paths': {
                '/issues.json': {},
                '/projects.json': {},
                '/users.json': {}
            }
        }
        mocker.patch('mcp_redmine.server.SPEC', mock_spec)

        # Act
        result = redmine_paths_list()

        # Assert
        assert isinstance(result, str)
        parsed = yaml.safe_load(result)
        assert isinstance(parsed, list)

    @pytest.mark.unit
    def test_redmine_paths_list_contains_all_paths(self, mock_env, mocker):
        """Test that all paths from spec are included."""
        # Arrange
        mock_spec = {
            'paths': {
                '/issues.json': {},
                '/projects.json': {},
                '/time_entries.json': {}
            }
        }
        mocker.patch('mcp_redmine.server.SPEC', mock_spec)

        # Act
        result = redmine_paths_list()

        # Assert
        parsed = yaml.safe_load(result)
        assert '/issues.json' in parsed
        assert '/projects.json' in parsed
        assert '/time_entries.json' in parsed

    @pytest.mark.unit
    def test_redmine_paths_list_empty_spec(self, mock_env, mocker):
        """Test with empty spec."""
        # Arrange
        mock_spec = {'paths': {}}
        mocker.patch('mcp_redmine.server.SPEC', mock_spec)

        # Act
        result = redmine_paths_list()

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed == []


class TestRedminePathsInfoTool:
    """Tests for the redmine_paths_info() tool."""

    @pytest.mark.unit
    def test_redmine_paths_info_single_path(self, mock_env, mocker):
        """Test getting info for a single path."""
        # Arrange
        mock_spec = {
            'paths': {
                '/issues.json': {
                    'get': {
                        'operationId': 'getIssues',
                        'parameters': [{'name': 'limit'}]
                    }
                },
                '/projects.json': {
                    'get': {'operationId': 'getProjects'}
                }
            }
        }
        mocker.patch('mcp_redmine.server.SPEC', mock_spec)

        # Act
        result = redmine_paths_info(['/issues.json'])

        # Assert
        parsed = yaml.safe_load(result)
        assert '/issues.json' in parsed
        assert '/projects.json' not in parsed
        assert parsed['/issues.json']['get']['operationId'] == 'getIssues'

    @pytest.mark.unit
    def test_redmine_paths_info_multiple_paths(self, mock_env, mocker):
        """Test getting info for multiple paths."""
        # Arrange
        mock_spec = {
            'paths': {
                '/issues.json': {'get': {'operationId': 'getIssues'}},
                '/projects.json': {'get': {'operationId': 'getProjects'}},
                '/users.json': {'get': {'operationId': 'getUsers'}}
            }
        }
        mocker.patch('mcp_redmine.server.SPEC', mock_spec)

        # Act
        result = redmine_paths_info(['/issues.json', '/projects.json'])

        # Assert
        parsed = yaml.safe_load(result)
        assert '/issues.json' in parsed
        assert '/projects.json' in parsed
        assert '/users.json' not in parsed

    @pytest.mark.unit
    def test_redmine_paths_info_nonexistent_path(self, mock_env, mocker):
        """Test requesting info for non-existent path."""
        # Arrange
        mock_spec = {
            'paths': {
                '/issues.json': {'get': {'operationId': 'getIssues'}}
            }
        }
        mocker.patch('mcp_redmine.server.SPEC', mock_spec)

        # Act
        result = redmine_paths_info(['/nonexistent.json'])

        # Assert
        parsed = yaml.safe_load(result)
        assert '/nonexistent.json' not in parsed
        assert parsed == {}

    @pytest.mark.unit
    def test_redmine_paths_info_mixed_valid_invalid(self, mock_env, mocker):
        """Test with mix of valid and invalid paths."""
        # Arrange
        mock_spec = {
            'paths': {
                '/issues.json': {'get': {'operationId': 'getIssues'}},
                '/projects.json': {'get': {'operationId': 'getProjects'}}
            }
        }
        mocker.patch('mcp_redmine.server.SPEC', mock_spec)

        # Act
        result = redmine_paths_info(['/issues.json', '/invalid.json', '/projects.json'])

        # Assert
        parsed = yaml.safe_load(result)
        assert '/issues.json' in parsed
        assert '/projects.json' in parsed
        assert '/invalid.json' not in parsed

    @pytest.mark.unit
    def test_redmine_paths_info_empty_list(self, mock_env, mocker):
        """Test with empty path list."""
        # Arrange
        mock_spec = {
            'paths': {
                '/issues.json': {'get': {'operationId': 'getIssues'}}
            }
        }
        mocker.patch('mcp_redmine.server.SPEC', mock_spec)

        # Act
        result = redmine_paths_info([])

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed == {}

    @pytest.mark.unit
    def test_redmine_paths_info_preserves_structure(self, mock_env, mocker):
        """Test that path info structure is preserved."""
        # Arrange
        path_data = {
            'get': {
                'operationId': 'getIssues',
                'parameters': [
                    {'name': 'limit', 'type': 'integer'},
                    {'name': 'offset', 'type': 'integer'}
                ],
                'responses': {
                    '200': {'description': 'Success'}
                }
            },
            'post': {
                'operationId': 'createIssue',
                'requestBody': {'content': {}}
            }
        }
        mock_spec = {
            'paths': {
                '/issues.json': path_data
            }
        }
        mocker.patch('mcp_redmine.server.SPEC', mock_spec)

        # Act
        result = redmine_paths_info(['/issues.json'])

        # Assert
        parsed = yaml.safe_load(result)
        assert parsed['/issues.json'] == path_data
        assert 'get' in parsed['/issues.json']
        assert 'post' in parsed['/issues.json']
        assert len(parsed['/issues.json']['get']['parameters']) == 2
