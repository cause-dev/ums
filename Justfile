set dotenv-load

manage := "temp_dj_project/manage.py"

default:
    @just --list

[group("lifecycle")]
setup:
    uv sync --locked --all-groups
    uv run python {{ manage }} migrate

[group("lifecycle")]
dev *args:
    uv run python {{ manage }} runserver 127.0.0.1:8000 {{ args }}

[group("database")]
makemigrations *args:
    uv run python {{ manage }} makemigrations {{ args }}

[group("database")]
migrate *args:
    uv run python {{ manage }} migrate {{ args }}

[group("database")]
showmigrations:
    uv run python {{ manage }} showmigrations

[group("quality")]
lint:
    uv run ruff check ./src
    uv run ty check ./src
    uv run djangofmt check ./src

[group("quality")]
format:
    uv run ruff format ./src
    uv run djangofmt ./src

[group("quality")]
fix:
    uv run ruff check --fix ./src
    uv run djangofmt check --fix ./src

[group("shell")]
shell:
    uv run python {{ manage }} shell

[group("shell")]
doctor:
    @uv --version; uv run python --version; podman --version

[group("debug")]
debug:
    uv run python -m debugpy --listen 5678 --wait-for-client {{ manage }} runserver 127.0.0.1:8000 --noreload
