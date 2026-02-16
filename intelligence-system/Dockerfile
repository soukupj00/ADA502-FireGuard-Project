# intelligence-system/Dockerfile
FROM python:3.12-slim-bookworm

# 1. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 2. Install Dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

# 3. Copy Code
COPY src ./src

# 4. Setup Environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# 5. Security
RUN useradd -m fireguard && chown -R fireguard /app
USER fireguard

# 6. Run the script directly
CMD ["python", "src/main.py"]