import os, yaml, pathlib
import socket
import threading
import time
import asyncio
import anyio
from functools import lru_cache
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urljoin

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger

### Constants ###

VERSION = "2026.01.01.000001"

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
mcp = FastMCP(
    "Redmine",
    dependencies=[
        "httpx>=0.28.1",
        "mcp[cli]>=1.3.0",
        "openapi-core>=0.19.4",
        "pyyaml>=6.0.2",
    ],
    transport="sse"
)
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
@lru_cache(maxsize=None)
def redmine_paths_list() -> str:
    """Return a list of available API paths from OpenAPI spec
    
    Retrieves all endpoint paths defined in the Redmine OpenAPI specification. Remember that you can use the
    redmine_paths_info tool to get the full specfication for a path.
    
    Returns:
        str: YAML string containing a list of path templates (e.g. '/issues.json')
    """
    return yd(list(SPEC['paths'].keys()))

@mcp.tool()
@lru_cache(maxsize=None)
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

@mcp.tool()
def redmine_search_issues(query: str, project_id: int = None, status_id: str = "open", limit: int = 10) -> str:
    """
    Smart search for issues using fuzzy matching on subject and description.
    
    Args:
        query: The search text to fuzzily match against issue subjects and descriptions
        project_id: Optional project ID to limit search
        status_id: Issue status filter (default: "open", use "*" for all)
        limit: Maximum number of results to return (default: 10)
        
    Returns:
        str: YAML string containing search results
    """
    params = {
        'text_search': query,
        'limit': limit,
        'status_id': status_id
    }
    if project_id:
        params['project_id'] = project_id
        
    return yd(request('/issues.json', method='get', params=params))

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

# Add necessary imports for custom SSE run with CORS
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from mcp.server.sse import SseServerTransport
import uvicorn
import mcp.server.stdio

async def run_sse_with_cors(mcp_instance, host, port):
    """Custom run loop to enable CORS for the SSE server"""
    # Create the SSE transport
    sse = SseServerTransport("/messages")

    async def dispatch_sse(scope, receive, send):
        if scope["type"] != "http":
            return
            
        request = Request(scope, receive)
        # Log headers for debugging auth
        get_logger(__name__).info(f"Incoming {request.method} request to {scope['path']}")
        get_logger(__name__).info(f"Headers: {dict(request.headers)}")
        
        if request.method == "POST":
            # Direct ASGI call - no return value expected by Mount
            await sse.handle_post_message(scope, receive, send)
        elif request.method == "GET":
            # Connect SSE stream and run request loop
            async with sse.connect_sse(scope, receive, send) as streams:
                await mcp_instance._mcp_server.run(
                    streams[0],
                    streams[1],
                    mcp_instance._mcp_server.create_initialization_options(),
                )
        else:
            response = JSONResponse({"error": "Method not allowed"}, status_code=405)
            await response(scope, receive, send)

    async def handle_root(request):
        return JSONResponse({"status": "online", "service": "mcp-redmine", "mode": "sse"})

    async def handle_health(request):
        return JSONResponse({"status": "ok"})

    # Configure CORS middleware
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins for Connector
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    # Create the Starlette app with CORS and routes
    starlette_app = Starlette(
        debug=True,
        middleware=middleware,
        routes=[
            Route("/", endpoint=handle_root),
            Route("/health", endpoint=handle_health),
            Mount("/sse", app=dispatch_sse),
            Mount("/messages", app=sse.handle_post_message),
        ],
    )

    # Run with Uvicorn
    config = uvicorn.Config(
        starlette_app,
        host=host,
        port=port,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()

def main():
    """Main entry point for the mcp-redmine package."""
    # Check for PORT environment variable (set by App Platform)
    port_env = os.environ.get('PORT')
    
    if port_env:
        # Remote/Docker Deployment: Run SSE with CORS
        port = int(port_env)
        get_logger(__name__).info(f"Starting MCP Redmine server on 0.0.0.0:{port} with CORS enabled (SSE mode)")
        try:
            anyio.run(run_sse_with_cors, mcp, "0.0.0.0", port)
        except Exception as e:
            get_logger(__name__).error(f"Failed to start server: {e}", exc_info=True)
            raise
    else:
        # Local Execution: Run standard stdio
        # This is what Claude Desktop expects when running locally
        get_logger(__name__).info("Starting MCP Redmine server in stdio mode (Local)")
        try:
            mcp.run(transport="stdio")
        except Exception as e:
            get_logger(__name__).error(f"Failed to start local server: {e}", exc_info=True)
            raise

if __name__ == "__main__":
    main()
