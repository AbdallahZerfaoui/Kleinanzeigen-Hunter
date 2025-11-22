# Multi-stage build for smaller final image
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy only dependency files first (better caching)
COPY pyproject.toml .

# Install Python dependencies with uv
RUN uv pip install --system --no-cache .

# Final stage - minimal runtime image
FROM python:3.12-slim

WORKDIR /app

# Install only runtime dependencies (no wget/curl needed in final image)
RUN apt-get update && apt-get install -y \
    # Playwright dependencies (only what's needed)
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Install Playwright browsers and dependencies
# First install system dependencies, then browser
RUN playwright install-deps chromium && \
    playwright install chromium

# Copy application code (do this last for better caching)
COPY . .

# Create non-root user for security
# RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
# USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]