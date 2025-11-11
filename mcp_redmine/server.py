import os, yaml, pathlib
import socket
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urljoin

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger

### Constants ###

VERSION = "2025.09.03.141435"

# Load OpenAPI spec
current_dir = pathlib.Path(__file__).parent
with open(current_dir / 'redmine_openapi.yml') as f:
    SPEC = yaml.safe_load(f)

# Constants from environment
REDMINE_URL = os.environ['REDMINE_URL']
REDMINE_API_KEY = os.environ['REDMINE_API_KEY']
if "REDMINE_REQUEST_INSTRUCTIONS" in os.environ and os.environ["REDMINE_REQUEST_INSTRUCTIONS"]:
    with open(os.environ["REDMINE_REQUEST_INSTRUCTIONS"]) as f:
        REDMINE_REQUEST_INSTRUCTIONS = f.read()
else:
    REDMINE_REQUEST_INSTRUCTIONS = ""


# Core
def request(path: str, method: str = 'get', data: dict = None, params: dict = None,
            content_type: str = 'application/json', content: bytes = None) -> dict:
    headers = {'X-Redmine-API-Key': REDMINE_API_KEY, 'Content-Type': content_type}
    url = urljoin(REDMINE_URL, path.lstrip('/'))

    try:
        response = httpx.request(method=method.lower(), url=url, json=data, params=params, headers=headers,
                                 content=content, timeout=60.0)
        response.raise_for_status()

        body = None
        if response.content:
            try:
                body = response.json()
            except ValueError:
                body = response.content

        return {"status_code": response.status_code, "body": body, "error": ""}
    except Exception as e:
        try:
            status_code = e.response.status_code
        except:
            status_code = 0

        try:
            body = e.response.json()
        except:
            try:
                body = e.response.text
            except:
                body = None

        return {"status_code": status_code, "body": body, "error": f"{e.__class__.__name__}: {e}"}
        
def yd(obj):
    # Allow direct Unicode output, prevent line wrapping for long lines, and avoid automatic key sorting.
    return yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=4096)


# Tools
mcp = FastMCP("Redmine MCP server")
get_logger(__name__).info(f"Starting MCP Redmine version {VERSION}")

@mcp.tool(description="""
Make a request to the Redmine API

Args:
    path: API endpoint path (e.g. '/issues.json')
    method: HTTP method to use (default: 'get')
    data: Dictionary for request body (for POST/PUT)
    params: Dictionary for query parameters

Returns:
    str: YAML string containing response status code, body and error message

{}""".format(REDMINE_REQUEST_INSTRUCTIONS).strip())
    
def redmine_request(path: str, method: str = 'get', data: dict = None, params: dict = None) -> str:
    return yd(request(path, method=method, data=data, params=params))

@mcp.tool()
def redmine_paths_list() -> str:
    """Return a list of available API paths from OpenAPI spec
    
    Retrieves all endpoint paths defined in the Redmine OpenAPI specification. Remember that you can use the
    redmine_paths_info tool to get the full specfication for a path.
    
    Returns:
        str: YAML string containing a list of path templates (e.g. '/issues.json')
    """
    return yd(list(SPEC['paths'].keys()))

@mcp.tool()
def redmine_paths_info(path_templates: list) -> str:
    """Get full path information for given path templates
    
    Args:
        path_templates: List of path templates (e.g. ['/issues.json', '/projects.json'])
        
    Returns:
        str: YAML string containing API specifications for the requested paths
    """
    info = {}
    for path in path_templates:
        if path in SPEC['paths']:
            info[path] = SPEC['paths'][path]

    return yd(info)

@mcp.tool()
def redmine_upload(file_path: str, description: str = None) -> str:
    """
    Upload a file to Redmine and get a token for attachment
    
    Args:
        file_path: Fully qualified path to the file to upload
        description: Optional description for the file
        
    Returns:
        str: YAML string containing response status code, body and error message
             The body contains the attachment token
    """
    try:
        path = pathlib.Path(file_path).expanduser()
        assert path.is_absolute(), f"Path must be fully qualified, got: {file_path}"
        assert path.exists(), f"File does not exist: {file_path}"

        params = {'filename': path.name}
        if description:
            params['description'] = description

        with open(path, 'rb') as f:
            file_content = f.read()

        result = request(path='uploads.json', method='post', params=params,
                         content_type='application/octet-stream', content=file_content)
        return yd(result)
    except Exception as e:
        return yd({"status_code": 0, "body": None, "error": f"{e.__class__.__name__}: {e}"})

@mcp.tool()
def redmine_download(attachment_id: int, save_path: str, filename: str = None) -> str:
    """
    Download an attachment from Redmine and save it to a local file
    
    Args:
        attachment_id: The ID of the attachment to download
        save_path: Fully qualified path where the file should be saved to
        filename: Optional filename to use for the attachment. If not provided, 
                 will be determined from attachment data or URL
        
    Returns:
        str: YAML string containing download status, file path, and any error messages
    """
    try:
        path = pathlib.Path(save_path).expanduser()
        assert path.is_absolute(), f"Path must be fully qualified, got: {save_path}"
        assert not path.is_dir(), f"Path can't be a directory, got: {save_path}"

        if not filename:
            attachment_response = request(f"attachments/{attachment_id}.json", "get")
            if attachment_response["status_code"] != 200:
                return yd(attachment_response)

            filename = attachment_response["body"]["attachment"]["filename"]

        response = request(f"attachments/download/{attachment_id}/{filename}", "get",
                           content_type="application/octet-stream")
        if response["status_code"] != 200 or not response["body"]:
            return yd(response)

        with open(path, 'wb') as f:
            f.write(response["body"])

        return yd({"status_code": 200, "body": {"saved_to": str(path), "filename": filename}, "error": ""})
    except Exception as e:
        return yd({"status_code": 0, "body": None, "error": f"{e.__class__.__name__}: {e}"})

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks."""
    def do_GET(self):
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"mcp-redmine"}\n')
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_HEAD(self):
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP server logs
        pass

# Global reference to keep the health server alive
_health_server = None

def start_health_server(port=8080):
    """Start a simple HTTP server for health checks in a background thread."""
    global _health_server
    try:
        # Explicitly bind to 0.0.0.0 to accept connections from any interface
        server_address = ('0.0.0.0', port)
        get_logger(__name__).info(f"Starting health check server on {server_address[0]}:{server_address[1]}")
        server = HTTPServer(server_address, HealthCheckHandler)
        _health_server = server  # Keep global reference
        
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        
        # Wait for the server to be ready and verify it's listening
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(0.2)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                get_logger(__name__).info(f"Health check server is listening on 0.0.0.0:{port}")
                return server
            if attempt < max_attempts - 1:
                get_logger(__name__).debug(f"Waiting for health server to be ready (attempt {attempt + 1}/{max_attempts})")
        
        get_logger(__name__).warning(f"Health check server started but verification failed after {max_attempts} attempts")
        return server
    except Exception as e:
        get_logger(__name__).error(f"Failed to start health check server: {e}", exc_info=True)
        _health_server = None
        return None

def main():
    """Main entry point for the mcp-redmine package."""
    # Start health check server if PORT environment variable is set (App Platform)
    # App Platform sets PORT automatically based on http_port
    health_port = os.environ.get('PORT', '8080')
    health_server = None
    try:
        health_server = start_health_server(int(health_port))
        if health_server is None:
            get_logger(__name__).warning("Health check server failed to start, continuing without it")
    except (ValueError, OSError) as e:
        # If port is not set or not available, continue without health server
        get_logger(__name__).warning(f"Could not start health check server: {e}")
    
    # Check if we're in a containerized environment (App Platform)
    # If PORT is set, we're likely in App Platform and should keep the process alive
    # for health checks, even if MCP server can't run without stdio
    if os.environ.get('PORT'):
        get_logger(__name__).info("Running in containerized environment - keeping process alive for health checks")
        # Keep the process alive indefinitely for health checks
        # The health server runs in a background thread
        try:
            while True:
                time.sleep(60)
                # Log periodically to show the process is alive
                get_logger(__name__).debug("Health check server is running")
        except KeyboardInterrupt:
            get_logger(__name__).info("Shutting down...")
    else:
        # Run the MCP server (stdio-based) - normal operation for Claude Desktop
        # This blocks, so the health server thread will continue running
        mcp.run()

if __name__ == "__main__":
    main()
