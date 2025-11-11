#!/bin/bash

# Test script for deployed MCP Redmine server on Digital Ocean App Platform
# 
# Usage:
#   1. Get your App Platform URL from the Digital Ocean dashboard
#   2. Replace YOUR_APP_URL below with your actual app URL
#   3. Run: bash test_deployment.sh

APP_URL="${1:-http://localhost:8080}"

echo "Testing MCP Redmine deployment at: $APP_URL"
echo ""

# Test health endpoint
echo "1. Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$APP_URL/health")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Health check passed (HTTP $HTTP_CODE)"
    echo "  Response: $BODY"
else
    echo "✗ Health check failed (HTTP $HTTP_CODE)"
    echo "  Response: $BODY"
fi

echo ""

# Test root endpoint
echo "2. Testing / endpoint..."
ROOT_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$APP_URL/")
HTTP_CODE=$(echo "$ROOT_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$ROOT_RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Root endpoint works (HTTP $HTTP_CODE)"
    echo "  Response: $BODY"
else
    echo "✗ Root endpoint failed (HTTP $HTTP_CODE)"
    echo "  Response: $BODY"
fi

echo ""
echo "Note: The MCP server communicates via stdio, not HTTP."
echo "To actually use the MCP tools, connect via Claude Desktop."
echo ""
echo "To get your App Platform URL:"
echo "  1. Go to Digital Ocean Dashboard > Apps"
echo "  2. Click on your 'mcp-redmine' app"
echo "  3. Find the URL in the app settings or use the provided domain"

