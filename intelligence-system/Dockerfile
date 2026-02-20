# intelligence-system/Dockerfile
FROM python:3.12-slim-bookworm

# 1. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 2. Configure uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 3. Create the virtual environment and set path
RUN uv venv
ENV PATH="/app/.venv/bin:$PATH"

# 4. Install Application-Specific Dependencies
COPY ./intelligence-system/pyproject.toml ./intelligence-system/uv.lock ./
RUN uv sync --no-dev

# 5. Copy Application Code
COPY ./intelligence-system/src ./src

# 6. Set the PYTHONPATH to include the 'src' directory
ENV PYTHONPATH="/app/src"

# 7. Security
RUN useradd -m fireguard && chown -R fireguard /app
USER fireguard

# 8. Run the script
CMD ["/app/.venv/bin/python", "src/main.py"]
