# MCP Redmine Test Suite

This directory contains the test suite for the MCP Redmine server.

## Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_core_functions.py` - Unit tests for core functions (request, yd)
- `test_mcp_tools.py` - Unit tests for MCP tool functions
- `test_file_operations.py` - Unit tests for file upload/download operations
- `test_health_check.py` - Unit tests for health check server

## Running Tests

### Run all tests
```bash
uv run pytest
```

### Run with coverage
```bash
uv run pytest --cov=mcp_redmine --cov-report=html
```

### Run specific test file
```bash
uv run pytest tests/test_core_functions.py
```

### Run specific test class or function
```bash
uv run pytest tests/test_core_functions.py::TestRequestFunction::test_request_success_with_json_response
```

### Run only unit tests
```bash
uv run pytest -m unit
```

### Run only integration tests
```bash
uv run pytest -m integration
```

### Run with verbose output
```bash
uv run pytest -v
```

### Run with detailed output
```bash
uv run pytest -vv
```

## Test Markers

- `@pytest.mark.unit` - Fast unit tests with mocked dependencies
- `@pytest.mark.integration` - Integration tests that may interact with actual services
- `@pytest.mark.slow` - Slow-running tests

## Coverage Reports

After running tests with coverage, open the HTML report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Writing New Tests

### Example Test

```python
import pytest
from mcp_redmine.server import some_function

class TestSomeFunction:
    """Tests for some_function()."""

    @pytest.mark.unit
    def test_basic_functionality(self, mock_env):
        """Test basic functionality."""
        # Arrange
        input_data = "test"

        # Act
        result = some_function(input_data)

        # Assert
        assert result == expected_output
```

### Using Fixtures

Fixtures are defined in `conftest.py` and can be used by adding them as parameters:

```python
def test_with_temp_file(self, temp_file):
    """Test uses temporary file fixture."""
    assert temp_file.exists()
```

### Mocking

Use `pytest-mock` for mocking:

```python
def test_with_mock(self, mocker):
    """Test with mocked dependencies."""
    mock_func = mocker.patch('module.function')
    mock_func.return_value = "mocked"
    # ... test code
```

## Environment Variables

Tests use mocked environment variables via the `mock_env` fixture. No actual environment variables are required.

## Best Practices

1. **Arrange-Act-Assert** - Structure tests clearly
2. **One assertion per test** - Keep tests focused (when possible)
3. **Descriptive names** - Test names should describe what they test
4. **Use fixtures** - Reuse common setup code
5. **Mock external dependencies** - Tests should be fast and isolated
6. **Test edge cases** - Include error conditions and boundary cases
