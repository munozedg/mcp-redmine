#!/usr/bin/env python3
"""
Direct test script for Redmine API through the MCP server functions
This bypasses the MCP protocol and directly tests the Redmine API functions
"""

import os
import sys
import yaml
from pathlib import Path

# Add the current directory to the path so we can import mcp_redmine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_env_file(env_path=".env"):
    """Load environment variables from .env file"""
    env_file = Path(env_path)
    if env_file.exists():
        print(f"Loading environment variables from {env_path}...")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    # Set environment variable (override existing if in .env)
                    if key:
                        os.environ[key] = value
        print("✓ Environment variables loaded from .env file")
        return True
    return False


# Load .env file BEFORE importing mcp_redmine.server
# because server.py reads environment variables at import time
load_env_file(".env")

# Now we can safely import the server module
from mcp_redmine.server import request, redmine_paths_list, redmine_paths_info, redmine_request

def test_redmine_connection():
    """Test basic Redmine connection"""
    print("=" * 60)
    print("Test 1: Testing Redmine Connection")
    print("=" * 60)
    
    try:
        result = request("/projects.json", method="get", params={"limit": 1})
        print(f"Status Code: {result['status_code']}")
        if result['status_code'] == 200:
            print("✓ Successfully connected to Redmine!")
            if result['body'] and 'projects' in result['body']:
                print(f"  Found {len(result['body']['projects'])} project(s)")
        else:
            print(f"✗ Connection failed: {result.get('error', 'Unknown error')}")
        print()
        return result['status_code'] == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        return False


def test_list_paths():
    """Test listing available API paths"""
    print("=" * 60)
    print("Test 2: List Available Redmine API Paths")
    print("=" * 60)
    
    try:
        paths = redmine_paths_list()
        paths_list = yaml.safe_load(paths)
        print(f"✓ Found {len(paths_list)} available API paths")
        print("\nFirst 10 paths:")
        for path in paths_list[:10]:
            print(f"  - {path}")
        if len(paths_list) > 10:
            print(f"  ... and {len(paths_list) - 10} more")
        print()
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        return False


def test_get_projects():
    """Test getting projects"""
    print("=" * 60)
    print("Test 3: Get Redmine Projects")
    print("=" * 60)
    
    try:
        result = redmine_request("/projects.json", method="get", params={"limit": 5})
        result_dict = yaml.safe_load(result)
        
        if result_dict.get('status_code') == 200:
            projects = result_dict.get('body', {}).get('projects', [])
            print(f"✓ Successfully retrieved {len(projects)} project(s)")
            for project in projects[:5]:
                print(f"  - {project.get('name', 'Unknown')} (ID: {project.get('id', 'N/A')})")
        else:
            print(f"✗ Failed: {result_dict.get('error', 'Unknown error')}")
        print()
        return result_dict.get('status_code') == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_get_issues():
    """Test getting issues"""
    print("=" * 60)
    print("Test 4: Get Redmine Issues")
    print("=" * 60)
    
    try:
        result = redmine_request("/issues.json", method="get", params={"limit": 5})
        result_dict = yaml.safe_load(result)
        
        if result_dict.get('status_code') == 200:
            issues = result_dict.get('body', {}).get('issues', [])
            print(f"✓ Successfully retrieved {len(issues)} issue(s)")
            for issue in issues[:5]:
                subject = issue.get('subject', 'No subject')
                issue_id = issue.get('id', 'N/A')
                status = issue.get('status', {}).get('name', 'Unknown')
                print(f"  - #{issue_id}: {subject} [{status}]")
        else:
            print(f"✗ Failed: {result_dict.get('error', 'Unknown error')}")
        print()
        return result_dict.get('status_code') == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_get_issue_by_id(issue_id=1):
    """Test getting a specific issue"""
    print("=" * 60)
    print(f"Test 5: Get Issue #{issue_id}")
    print("=" * 60)
    
    try:
        result = redmine_request(f"/issues/{issue_id}.json", method="get")
        result_dict = yaml.safe_load(result)
        
        if result_dict.get('status_code') == 200:
            issue = result_dict.get('body', {}).get('issue', {})
            print(f"✓ Successfully retrieved issue #{issue_id}")
            print(f"  Subject: {issue.get('subject', 'N/A')}")
            print(f"  Status: {issue.get('status', {}).get('name', 'N/A')}")
            print(f"  Priority: {issue.get('priority', {}).get('name', 'N/A')}")
            if issue.get('assigned_to'):
                print(f"  Assigned to: {issue.get('assigned_to', {}).get('name', 'N/A')}")
        else:
            print(f"✗ Failed: {result_dict.get('error', 'Unknown error')}")
            if result_dict.get('status_code') == 404:
                print(f"  Issue #{issue_id} not found")
        print()
        return result_dict.get('status_code') == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        return False


def main():
    """Run all tests"""
    print("MCP Redmine Server - Direct API Test")
    print("=" * 60)
    print()
    
    # Note: .env file is already loaded before importing the module
    # Check if it was loaded
    env_file = Path(".env")
    if not env_file.exists():
        print("No .env file found, using environment variables...")
    print()
    
    # Check environment variables
    if not os.environ.get("REDMINE_URL"):
        print("ERROR: REDMINE_URL environment variable not set")
        print()
        print("Create a .env file in the project root with:")
        print("  REDMINE_URL=https://your-redmine-instance.com")
        print("  REDMINE_API_KEY=your-api-key")
        print()
        print("Or set environment variables:")
        print("  export REDMINE_URL='https://your-redmine-instance.com'")
        print("  export REDMINE_API_KEY='your-api-key'")
        print("  (On Windows: set REDMINE_URL=... and set REDMINE_API_KEY=...)")
        sys.exit(1)
    
    if not os.environ.get("REDMINE_API_KEY"):
        print("ERROR: REDMINE_API_KEY environment variable not set")
        print()
        print("Create a .env file in the project root with:")
        print("  REDMINE_URL=https://your-redmine-instance.com")
        print("  REDMINE_API_KEY=your-api-key")
        print()
        print("Or set environment variables:")
        print("  export REDMINE_API_KEY='your-api-key'")
        print("  (On Windows: set REDMINE_API_KEY=...)")
        sys.exit(1)
    
    print(f"Redmine URL: {os.environ.get('REDMINE_URL')}")
    print(f"API Key: {'*' * 20} (hidden)")
    print()
    
    results = []
    
    try:
        # Run tests
        results.append(("Connection Test", test_redmine_connection()))
        results.append(("List API Paths", test_list_paths()))
        results.append(("Get Projects", test_get_projects()))
        results.append(("Get Issues", test_get_issues()))
        results.append(("Get Issue #3844", test_get_issue_by_id(3844)))
        
        # Summary
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        passed = sum(1 for _, result in results if result)
        total = len(results)
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")
        print()
        print(f"Total: {passed}/{total} tests passed")
        print("=" * 60)
        
        if passed == total:
            print("All tests passed! ✓")
            sys.exit(0)
        else:
            print("Some tests failed. Check the output above for details.")
            sys.exit(1)
            
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

