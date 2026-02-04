# STAGE 1: Builder
# Use the official uv image to handle dependency installation
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: Ensures exact versions from uv.lock are used
# --no-dev: Exclude development dependencies (like pytest)
# --no-install-project: We only want dependencies installed in .venv, not the app code yet
RUN uv sync --frozen --no-dev --no-install-project

# STAGE 2: Runtime
# Use a slim Python image for the final container
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the application source code
COPY src ./src

# Set environment variables
# Add the virtual env to PATH so we can run 'uvicorn' directly
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Create a non-root user for security
RUN useradd -m fireguard && chown -R fireguard /app
USER fireguard

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
