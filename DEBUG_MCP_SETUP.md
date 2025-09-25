# MCP Redmine Troubleshooting Guide

## Issue: "No tools, prompts, or resources" showing in Claude Desktop

This happens when the MCP server fails to start properly due to missing environment variables or configuration issues.

## Root Cause
The server code requires `REDMINE_URL` and `REDMINE_API_KEY` environment variables:

```python
REDMINE_URL = os.environ['REDMINE_URL']        # Fails if not set
REDMINE_API_KEY = os.environ['REDMINE_API_KEY']  # Fails if not set
```

## Solutions

### 1. Verify Claude Desktop Configuration

Check your Claude Desktop configuration file location:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Your configuration should look like this:

```json
{
  "mcpServers": {
    "redmine": {
      "command": "uvx",
      "args": ["--from", "mcp-redmine", "mcp-redmine"],
      "env": {
        "REDMINE_URL": "https://your-redmine-instance.example.com",
        "REDMINE_API_KEY": "your-actual-api-key-here"
      }
    }
  }
}
```

**Common mistakes:**
- Missing `env` section
- Wrong environment variable names
- Invalid JSON syntax
- Missing quotes around values

### 2. Test Local Installation

If using local development setup, your config should be:

```json
{
  "mcpServers": {
    "redmine": {
      "command": "uv",
      "args": ["run", "--directory", "C:\\Users\\munoz\\mcp-redmine", "-m", "mcp_redmine.server", "main"],
      "env": {
        "REDMINE_URL": "https://your-redmine-instance.example.com",
        "REDMINE_API_KEY": "your-actual-api-key-here"
      }
    }
  }
}
```

### 3. Validate Your Redmine Setup

Test your Redmine connection manually:

```bash
# Test if your Redmine instance is accessible
curl -H "X-Redmine-API-Key: YOUR_API_KEY" "https://your-redmine-instance.com/issues.json?limit=1"
```

### 4. Check Claude Desktop Logs

Look for error messages in Claude Desktop:
- Restart Claude Desktop completely
- Check if there are any error notifications
- Look in system logs if available

### 5. Debug the Server Directly

Test the server manually:

```bash
# Set environment variables
set REDMINE_URL=https://your-redmine-instance.com
set REDMINE_API_KEY=your-api-key

# Run server directly
cd C:\Users\munoz\mcp-redmine
uv run -m mcp_redmine.server main
```

## Quick Fix Checklist

- [ ] Environment variables are set in Claude Desktop config
- [ ] JSON syntax is valid in config file
- [ ] Redmine URL is correct and accessible
- [ ] API key is valid and has proper permissions  
- [ ] Claude Desktop has been completely restarted
- [ ] No firewall/network issues blocking connection

## Expected Tools

When working correctly, you should see these tools:
- `redmine_request` - Make API requests
- `redmine_paths_list` - List available endpoints  
- `redmine_paths_info` - Get endpoint details
- `redmine_upload` - Upload files
- `redmine_download` - Download attachments

## Additional Debugging

If still not working, add error handling to see what's failing:

1. Check if OpenAPI spec file exists
2. Verify network connectivity to Redmine
3. Test API key permissions
4. Check Claude Desktop version compatibility