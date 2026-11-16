ARG PYTHON_VERSION=3.15
ARG UV_VERSION=0.13.8

ARG DEV_IMAGE=dhi.io/uv:${UV_VERSION}-debian13-dev

# -------------------------------------------
# Development image
# -------------------------------------------

FROM ${DEV_IMAGE} AS dev

ARG PYTHON_VERSION

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/root/.cache/uv \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH=/app/.venv/bin:$PATH

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    git netcat-openbsd bash curl gzip libstdc++6

RUN uv python install ${PYTHON_VERSION} \
    && uv venv --python ${PYTHON_VERSION} /app/.venv

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --all-groups --no-install-project

EXPOSE 8000

ENTRYPOINT []

CMD ["uv", "run", "python", "temp_dj_project/manage.py", "runserver", "0.0.0.0:8000"]
