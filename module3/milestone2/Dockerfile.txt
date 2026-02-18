# ============================================
# Builder Stage - Install dependencies
# ============================================
FROM python:3.11-slim as builder

WORKDIR /build

# Copy only requirements first (better caching)
COPY app/requirements.txt .

# Install dependencies to user directory
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# Runtime Stage - Minimal production image
# ============================================
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app/ .

# Set PATH to include user-installed packages
ENV PATH=/root/.local/bin:$PATH

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run application
CMD ["python", "app.py"]