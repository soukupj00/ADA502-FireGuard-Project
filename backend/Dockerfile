# Use a single stage to guarantee path consistency
FROM python:3.12-slim-bookworm

# 1. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 2. Configure uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 3. Copy dependency files
COPY pyproject.toml uv.lock ./

# 4. Install dependencies
# --no-dev: Exclude dev dependencies
# --no-install-project: Don't install the 'app' package itself, just libs
RUN uv sync --python 3.12 --no-dev --no-install-project

# 5. Copy application code
COPY src ./src

# 6. Set PATHs
# PYTHONPATH includes /app/src so we can do "import app" and "import frcm"
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# 7. Security: Create non-root user
RUN useradd -m fireguard && chown -R fireguard /app
USER fireguard

EXPOSE 8000

# 8. Run uvicorn
# FIX: Changed "src.app.main:app" to "app.main:app"
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
