FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir uv

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy dependency files first for better layer caching
# Include README.md and LICENSE as they're referenced in pyproject.toml
COPY --chown=appuser:appuser pyproject.toml uv.lock README.md LICENSE ./

# Install dependencies (run as root, then fix ownership)
RUN uv sync --frozen && chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the MCP server
CMD ["uv", "run", "--directory", "/app", "-m", "mcp_redmine.server", "main"]