# 1. Start from official lightweight Python 3.12 Linux image ("slim" cuts ~800MB of unused OS bloat)
FROM python:3.12-slim

# 2. Copy the official 'uv' binary directly from Astral's image (no pip needed!)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Set working directory inside the container
WORKDIR /app

# 4. Optimize uv for Docker: pre-compile .pyc bytecode & copy files cleanly across layers
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 5. LAYER CACHE STEP: Copy ONLY dependency lockfiles first!
# As long as pyproject.toml and uv.lock don't change, Docker caches the next RUN step.
COPY pyproject.toml uv.lock ./

# 6. Install production dependencies into /app/.venv (skips pytest/dev tools & doesn't install project yet)
RUN uv sync --locked --no-install-project --no-dev

# 7. Now copy your actual Shop API code (main.py, models.py, schemas.py, database.py)
COPY . .

# 8. Sync the project itself (fast since all third-party packages are already cached!)
RUN uv sync --locked --no-dev

# 9. Add the container's .venv/bin to PATH so 'fastapi' and 'uvicorn' work directly without 'uv run'
ENV PATH="/app/.venv/bin:$PATH"

# 10. Security best practice: create and switch to a non-root user
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# 11. Document that the container listens on port 8000
EXPOSE 8000

# 12. Start FastAPI in production mode (0.0.0.0 is mandatory so external traffic can reach it!)
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]