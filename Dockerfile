# JobOrbit: API + built frontend in one image.

FROM node:22-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS app
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
WORKDIR /app/backend

# Dependencies first so they are cached until pyproject.toml / uv.lock change.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY backend/ ./
RUN uv sync --locked --no-dev
COPY --from=frontend /app/frontend/dist /app/frontend/dist

ENV PATH="/app/backend/.venv/bin:$PATH" \
    JOBORBIT_HOST=0.0.0.0 \
    JOBORBIT_DATA_DIR=/app/backend/data
RUN useradd --system --create-home joborbit \
    && mkdir -p /app/backend/data \
    && chown -R joborbit /app/backend/data
USER joborbit
VOLUME /app/backend/data
EXPOSE 8765

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/api/v1/health')"
CMD ["sh", "-c", "joborbit migrate && exec joborbit-api"]
