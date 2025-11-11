#!/usr/bin/env python3
"""
Test script for MCP Redmine server
Tests the MCP server by sending JSON-RPC requests via stdio
"""

import json
import sys
import subprocess
import os
from typing import Dict, Any

def send_mcp_request(method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Send a JSON-RPC request to the MCP server via stdio"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
    }
    if params:
        request["params"] = params
    
    request_json = json.dumps(request) + "\n"
    
    # Start the MCP server process
    env = os.environ.copy()
    if "REDMINE_URL" not in env:
        print("ERROR: REDMINE_URL environment variable not set")
        sys.exit(1)
    if "REDMINE_API_KEY" not in env:
        print("ERROR: REDMINE_API_KEY environment variable not set")
        sys.exit(1)
    
    try:
        # Run the MCP server
        process = subprocess.Popen(
            ["uv", "run", "--directory", ".", "-m", "mcp_redmine.server", "main"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Send request
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        if stderr:
            print(f"STDERR: {stderr}", file=sys.stderr)
        
        # Parse response
        if stdout:
            try:
                response = json.loads(stdout.strip())
                return response
            except json.JSONDecodeError as e:
                print(f"Failed to parse response: {e}")
                print(f"Response was: {stdout}")
                return {"error": "Failed to parse response"}
        else:
            return {"error": "No response from server"}
            
    except subprocess.TimeoutExpired:
        process.kill()
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": str(e)}


def test_list_tools():
    """Test listing available tools"""
    print("=" * 60)
    print("Test 1: List available tools")
    print("=" * 60)
    
    response = send_mcp_request("tools/list")
    print(json.dumps(response, indent=2))
    print()


def test_redmine_paths_list():
    """Test redmine_paths_list tool"""
    print("=" * 60)
    print("Test 2: List Redmine API paths")
    print("=" * 60)
    
    response = send_mcp_request("tools/call", {
        "name": "redmine_paths_list",
        "arguments": {}
    })
    print(json.dumps(response, indent=2))
    print()


def test_redmine_request():
    """Test redmine_request tool - get projects"""
    print("=" * 60)
    print("Test 3: Get Redmine projects")
    print("=" * 60)
    
    response = send_mcp_request("tools/call", {
        "name": "redmine_request",
        "arguments": {
            "path": "/projects.json",
            "method": "get"
        }
    })
    print(json.dumps(response, indent=2))
    print()


def test_redmine_request_issues():
    """Test redmine_request tool - get issues"""
    print("=" * 60)
    print("Test 4: Get Redmine issues (limit 5)")
    print("=" * 60)
    
    response = send_mcp_request("tools/call", {
        "name": "redmine_request",
        "arguments": {
            "path": "/issues.json",
            "method": "get",
            "params": {
                "limit": 5
            }
        }
    })
    print(json.dumps(response, indent=2))
    print()


def main():
    """Run all tests"""
    print("MCP Redmine Server Test Suite")
    print("=" * 60)
    print()
    
    # Check environment variables
    if not os.environ.get("REDMINE_URL"):
        print("ERROR: REDMINE_URL environment variable not set")
        print("Set it with: export REDMINE_URL='https://your-redmine-instance.com'")
        sys.exit(1)
    
    if not os.environ.get("REDMINE_API_KEY"):
        print("ERROR: REDMINE_API_KEY environment variable not set")
        print("Set it with: export REDMINE_API_KEY='your-api-key'")
        sys.exit(1)
    
    print(f"Redmine URL: {os.environ.get('REDMINE_URL')}")
    print(f"API Key: {'*' * 20} (hidden)")
    print()
    
    try:
        # Run tests
        test_list_tools()
        test_redmine_paths_list()
        test_redmine_request()
        test_redmine_request_issues()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

