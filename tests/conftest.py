"""
Pytest configuration and shared fixtures for MCP Redmine tests.
"""
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
import httpx


def pytest_configure(config):
    """
    Pytest hook that runs before test collection.
    Set environment variables before server.py is imported.
    """
    os.environ.setdefault('REDMINE_URL', 'https://test.redmine.example.com')
    os.environ.setdefault('REDMINE_API_KEY', 'test_api_key_12345')
    os.environ.setdefault('REDMINE_REQUEST_INSTRUCTIONS', '')


@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv('REDMINE_URL', 'https://test.redmine.example.com')
    monkeypatch.setenv('REDMINE_API_KEY', 'test_api_key_12345')
    monkeypatch.setenv('REDMINE_REQUEST_INSTRUCTIONS', '')
    return {
        'REDMINE_URL': 'https://test.redmine.example.com',
        'REDMINE_API_KEY': 'test_api_key_12345',
        'REDMINE_REQUEST_INSTRUCTIONS': ''
    }


@pytest.fixture
def mock_redmine_response():
    """Create a mock successful Redmine API response."""
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    response.content = b'{"projects": [{"id": 1, "name": "Test Project"}]}'
    response.json.return_value = {"projects": [{"id": 1, "name": "Test Project"}]}
    response.text = '{"projects": [{"id": 1, "name": "Test Project"}]}'
    return response


@pytest.fixture
def mock_redmine_error_response():
    """Create a mock error Redmine API response."""
    response = Mock(spec=httpx.Response)
    response.status_code = 404
    response.content = b'{"error": "Not found"}'
    response.json.return_value = {"error": "Not found"}
    response.text = '{"error": "Not found"}'
    return response


@pytest.fixture
def temp_file():
    """Create a temporary file for testing file operations."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test file content")
        temp_path = f.name

    yield Path(temp_path)

    # Cleanup
    if Path(temp_path).exists():
        Path(temp_path).unlink()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)

    # Cleanup
    import shutil
    if Path(temp_path).exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def mock_openapi_spec():
    """Mock OpenAPI specification for Redmine API."""
    return {
        'paths': {
            '/issues.json': {
                'get': {
                    'operationId': 'getIssues',
                    'parameters': [
                        {'name': 'limit', 'in': 'query', 'schema': {'type': 'integer'}}
                    ],
                    'responses': {
                        '200': {
                            'description': 'Successful response',
                            'content': {
                                'application/json': {
                                    'schema': {'type': 'object'}
                                }
                            }
                        }
                    }
                },
                'post': {
                    'operationId': 'createIssue',
                    'requestBody': {
                        'content': {
                            'application/json': {
                                'schema': {'type': 'object'}
                            }
                        }
                    }
                }
            },
            '/projects.json': {
                'get': {
                    'operationId': 'getProjects',
                    'responses': {
                        '200': {
                            'description': 'Successful response'
                        }
                    }
                }
            },
            '/uploads.json': {
                'post': {
                    'operationId': 'uploadFile',
                    'requestBody': {
                        'content': {
                            'application/octet-stream': {
                                'schema': {'type': 'string', 'format': 'binary'}
                            }
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_httpx_client(mocker):
    """Mock httpx client for testing HTTP requests."""
    mock_client = mocker.patch('httpx.request')
    return mock_client


@pytest.fixture
def sample_issue_data():
    """Sample issue data for testing."""
    return {
        "issue": {
            "id": 1,
            "subject": "Test Issue",
            "description": "Test Description",
            "status": {"id": 1, "name": "New"},
            "priority": {"id": 2, "name": "Normal"},
            "project": {"id": 1, "name": "Test Project"}
        }
    }


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "projects": [
            {"id": 1, "name": "Project One", "identifier": "project-one"},
            {"id": 2, "name": "Project Two", "identifier": "project-two"}
        ]
    }


@pytest.fixture
def sample_upload_response():
    """Sample upload response data for testing."""
    return {
        "upload": {
            "id": 7,
            "token": "7.ed32257a2ab0f7526c0d72c32994c58b131bb2c0775f7aa84aae01ea8397ea54"
        }
    }


@pytest.fixture
def sample_attachment_data():
    """Sample attachment data for testing."""
    return {
        "attachment": {
            "id": 1,
            "filename": "test_file.pdf",
            "filesize": 1024,
            "content_type": "application/pdf",
            "description": "Test attachment"
        }
    }
