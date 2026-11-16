set dotenv-load

default:
    @just --list

_compose *args:
    podman compose -f .devcontainer/compose.yaml {{ args }}

[group("lifecycle")]
up *args:
    @just _compose up {{ args }}

[group("lifecycle")]
down *args:
    @just _compose down {{ args }}

[group("lifecycle")]
start *args:
    @just _compose start {{ args }}

[group("lifecycle")]
stop *args:
    @just _compose stop {{ args }}

[group("lifecycle")]
restart *args:
    @just _compose restart {{ args }}

[group("lifecycle")]
build *args:
    @just _compose build --no-cache {{ args }}

[group("lifecycle")]
ps:
    @just _compose ps

[group("database")]
makemigrations *args:
    @just _compose exec backend uv run python temp_dj_project/manage.py makemigrations {{ args }}

[group("database")]
migrate *args:
    @just _compose exec backend uv run python temp_dj_project/manage.py migrate {{ args }}

[group("database")]
showmigrations:
    @just _compose exec backend uv run python temp_dj_project/manage.py showmigrations

[group("quality")]
lint:
    @just _compose exec backend uv run ruff check ./src
    @just _compose exec backend uv run ty check ./src
    @just _compose exec backend uv run djangofmt check ./src

[group("quality")]
format:
    @just _compose exec backend uv run ruff format ./src
    @just _compose exec backend uv run djangofmt ./src

[group("quality")]
fix:
    @just _compose exec backend uv run ruff check --fix ./src
    @just _compose exec backend uv run djangofmt check --fix ./src

[group("shell")]
shell-backend:
    @just _compose exec backend bash

[group("shell")]
logs *args:
    @just _compose logs -f {{ args }}
