.SILENT:

run:
	docker compose down
	clear
	docker compose build --no-cache
	docker compose up

lint:
	uvx ruff check

update:
	uv sync -U
	uv pip compile pyproject.toml > requirements.txt
