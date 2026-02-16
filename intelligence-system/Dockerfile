# intelligence-system/Dockerfile
FROM python:3.12-slim-bookworm

# 1. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 2. Configure uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 3. Install Dependencies
COPY pyproject.toml uv.lock ./
# Force uv to use the container's python (3.12)
RUN uv sync --python 3.12 --no-dev --no-install-project

# 4. Copy Code
COPY src ./src

# 5. Setup Environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# 6. Security
RUN useradd -m fireguard && chown -R fireguard /app
USER fireguard

# 7. Run the script
CMD ["python", "src/main.py"]