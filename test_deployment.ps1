# Test script for deployed MCP Redmine server on Digital Ocean App Platform
# 
# Usage:
#   1. Get your App Platform URL from the Digital Ocean dashboard
#   2. Replace YOUR_APP_URL below or pass it as parameter
#   3. Run: .\test_deployment.ps1

param(
    [string]$AppUrl = "http://localhost:8080"
)

Write-Host "Testing MCP Redmine deployment at: $AppUrl" -ForegroundColor Cyan
Write-Host ""

# Test health endpoint
Write-Host "1. Testing /health endpoint..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "$AppUrl/health" -Method GET -UseBasicParsing
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "✓ Health check passed (HTTP $($healthResponse.StatusCode))" -ForegroundColor Green
        Write-Host "  Response: $($healthResponse.Content)" -ForegroundColor Gray
    } else {
        Write-Host "✗ Health check failed (HTTP $($healthResponse.StatusCode))" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test root endpoint
Write-Host "2. Testing / endpoint..." -ForegroundColor Yellow
try {
    $rootResponse = Invoke-WebRequest -Uri "$AppUrl/" -Method GET -UseBasicParsing
    if ($rootResponse.StatusCode -eq 200) {
        Write-Host "✓ Root endpoint works (HTTP $($rootResponse.StatusCode))" -ForegroundColor Green
        Write-Host "  Response: $($rootResponse.Content)" -ForegroundColor Gray
    } else {
        Write-Host "✗ Root endpoint failed (HTTP $($rootResponse.StatusCode))" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Root endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Note: The MCP server communicates via stdio, not HTTP." -ForegroundColor Yellow
Write-Host "To actually use the MCP tools, connect via Claude Desktop." -ForegroundColor Yellow
Write-Host ""
Write-Host "To get your App Platform URL:" -ForegroundColor Cyan
Write-Host "  1. Go to Digital Ocean Dashboard > Apps"
Write-Host "  2. Click on your 'mcp-redmine' app"
Write-Host "  3. Find the URL in the app settings or use the provided domain"

