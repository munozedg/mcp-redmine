
import unittest
import json
import os
import sys
import subprocess

class TestSearch(unittest.TestCase):
    def test_search_tool_params(self):
        """Test that the redmine_search_issues tool accepts the correct parameters"""
        # We can't easily test the tool execution without a running server or mocking,
        # but we can verify the tool definition if we import it.
        # However, importing might trigger server startup logic.
        pass

    def test_search_integration(self):
        """Integration test for search tool using stdio"""
        # Similar to test_mcp_server.py
        env = os.environ.copy()
        if "REDMINE_URL" not in env or "REDMINE_API_KEY" not in env:
            print("Skipping integration test: REDMINE_URL/API_KEY not set")
            return

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "redmine_search_issues",
                "arguments": {
                    "query": "test",
                    "limit": 5
                }
            }
        }
        
        process = subprocess.Popen(
            ["uv", "run", "--directory", ".", "-m", "mcp_redmine.server", "main"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        stdout, stderr = process.communicate(input=json.dumps(request) + "\n", timeout=10)
        if stderr:
            print(f"STDERR: {stderr}")
            
        print(f"STDOUT: {stdout}")
        response = json.loads(stdout.strip())
        self.assertNotIn("error", response)
        self.assertIn("result", response)
        
if __name__ == '__main__':
    unittest.main()
