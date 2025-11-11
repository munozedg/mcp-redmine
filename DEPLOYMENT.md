# Deploying MCP Redmine to Digital Ocean App Platform

This guide walks you through deploying the MCP Redmine server to Digital Ocean App Platform using their native GitHub integration.

## Prerequisites

- Digital Ocean account
- GitHub repository with the MCP Redmine code
- Redmine instance URL and API key
- App Platform access (may require subscription)

## Overview

Digital Ocean App Platform will:
- Automatically detect changes when you push to your GitHub repository
- Build the Docker image from the Dockerfile
- Deploy and run the container
- Manage scaling, health checks, and monitoring

## Step 1: Prepare Your Repository

Ensure your repository has:
- `Dockerfile` in the root directory
- `.do/app.yaml` configuration file (already included)
- All source code committed and pushed to GitHub

## Step 2: Create App in Digital Ocean

1. Log in to your [Digital Ocean Dashboard](https://cloud.digitalocean.com/)
2. Navigate to **Apps** in the left sidebar
3. Click **Create App**
4. Select **GitHub** as your source
5. Authorize Digital Ocean to access your GitHub account (if not already done)
6. Select your repository: `runekaagaard/mcp-redmine` (or your fork)
7. Select the branch: `main`
8. Digital Ocean will detect the `.do/app.yaml` file automatically

## Step 3: Configure Environment Variables

In the App Platform configuration:

1. Navigate to the **Environment Variables** section
2. Add the following environment variables:

### Required Variables

- **REDMINE_URL** (Type: Secret)
  - Value: Your Redmine instance URL
  - Example: `https://your-redmine-instance.example.com`
  - **Important**: Select "Encrypt" to store as a secret

- **REDMINE_API_KEY** (Type: Secret)
  - Value: Your Redmine API key
  - Get this from: Your Redmine instance > My account > API access key
  - **Important**: Select "Encrypt" to store as a secret

### Optional Variables

- **REDMINE_REQUEST_INSTRUCTIONS** (Type: General)
  - Value: Path to custom instructions file (e.g., `/app/INSTRUCTIONS.md`)
  - Leave empty if not using custom instructions
  - Note: If using this, you'll need to mount the file into the container

## Step 4: Review App Configuration

The `.do/app.yaml` file configures:

- **Instance Size**: `basic-xxs` (smallest/cheapest option)
  - MCP servers are lightweight and don't need much resources
  - You can upgrade later if needed

- **Health Checks**: Configured to check the service
  - Note: MCP servers communicate via stdio, so health checks may need adjustment
  - The current configuration uses HTTP path `/` which may not be applicable

- **Auto-deploy**: Enabled on push to `main` branch

## Step 5: Deploy

1. Review all settings in the App Platform dashboard
2. Click **Create Resources** or **Deploy**
3. Digital Ocean will:
   - Clone your repository
   - Build the Docker image
   - Deploy the container
   - Run health checks

## Step 6: Verify Deployment

1. Check the **Runtime Logs** in the App Platform dashboard
2. Look for: `Starting MCP Redmine version X.X.X.X`
3. Verify there are no error messages about missing environment variables

### Testing the Health Endpoint

You can test the health check endpoint using curl or the provided test scripts:

**Using curl:**
```bash
# Get your App Platform URL from the Digital Ocean dashboard
curl https://your-app-url.ondigitalocean.app/health
# Should return: {"status":"ok","service":"mcp-redmine"}
```

**Using the test script (Linux/Mac):**
```bash
bash test_deployment.sh https://your-app-url.ondigitalocean.app
```

**Using the test script (Windows PowerShell):**
```powershell
.\test_deployment.ps1 -AppUrl "https://your-app-url.ondigitalocean.app"
```

**To find your App Platform URL:**
1. Go to Digital Ocean Dashboard > Apps
2. Click on your `mcp-redmine` app
3. The URL will be shown in the app overview (e.g., `mcp-redmine-xxxxx.ondigitalocean.app`)

## Important Notes

### MCP Server Communication

MCP servers communicate via **stdio** (stdin/stdout), not HTTP. This means:

- The server doesn't expose an HTTP endpoint
- Health checks configured in App Platform may not work as expected
- The server is designed to be run as a subprocess by Claude Desktop

### Using with Claude Desktop

**Important**: The MCP server deployed on App Platform is running and healthy, but **it cannot be directly connected to Claude Desktop** because:

1. MCP servers communicate via **stdio** (stdin/stdout), not HTTP
2. Claude Desktop needs to launch the server as a subprocess
3. The App Platform deployment is containerized and not accessible via stdio

**To actually use the MCP server with Claude Desktop, you have two options:**

#### Option 1: Run Locally (Recommended)
Run the MCP server locally on your machine and connect to your Redmine instance:

```json
{
  "mcpServers": {
    "redmine": {
      "command": "uvx",
      "args": ["--from", "mcp-redmine", "mcp-redmine"],
      "env": {
        "REDMINE_URL": "https://your-redmine-instance.example.com",
        "REDMINE_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### Option 2: SSH to App Platform (Advanced)
If you need to use the deployed server, you would need to:
1. Set up SSH access to your App Platform container
2. Configure Claude Desktop to SSH into the container and run the server
3. This is complex and not recommended for most users

**The App Platform deployment is useful for:**
- Testing and validation
- Running the server in a managed environment
- Future integration with MCP gateways or proxies (when available)

### Alternative: Local Deployment

If you need the server to work directly with Claude Desktop, consider:

- Running the server locally using `uvx` or `docker`
- Using a VPN or SSH tunnel to access a remote Redmine instance
- Setting up an MCP gateway service

## Troubleshooting

### Build Failures

- Check that `Dockerfile` is in the root directory
- Verify Python 3.13-slim base image is available
- Check build logs for dependency installation errors

### Runtime Errors

- **Missing environment variables**: Ensure `REDMINE_URL` and `REDMINE_API_KEY` are set
- **Connection errors**: Verify your Redmine instance is accessible from Digital Ocean's network
- **API key errors**: Confirm the API key is valid and has proper permissions

### Health Check Failures

- MCP servers don't expose HTTP endpoints by default
- You may need to disable health checks or modify the server to expose a health endpoint
- Check logs to see if the server is actually running despite health check failures

## Updating the Deployment

1. Make changes to your code
2. Commit and push to the `main` branch
3. Digital Ocean will automatically detect the change
4. A new deployment will be triggered
5. Monitor the deployment in the App Platform dashboard

## Cost Considerations

- **basic-xxs**: ~$5/month (smallest instance)
- Data transfer costs may apply
- Review Digital Ocean's pricing for current rates

## Security Best Practices

1. **Never commit API keys** to your repository
2. **Use encrypted secrets** in App Platform for sensitive values
3. **Restrict access** to your Redmine instance if possible
4. **Monitor logs** for suspicious activity
5. **Keep dependencies updated** to avoid security vulnerabilities

## Support

For issues with:
- **MCP Redmine**: Check the [GitHub repository](https://github.com/runekaagaard/mcp-redmine)
- **Digital Ocean App Platform**: See [Digital Ocean Documentation](https://docs.digitalocean.com/products/app-platform/)
- **Redmine API**: Consult [Redmine API Documentation](https://www.redmine.org/projects/redmine/wiki/Rest_api)

