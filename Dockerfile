FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --compile-bytecode

COPY ./src/ ./src/

ENTRYPOINT ["uv", "run", "./src/main.py"]
