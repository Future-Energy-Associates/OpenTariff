# Shortcuts for build commands, linting, testing etc

SRC = opentariff

.PHONY: lint
lint:
	poetry run ruff check $(SRC)

.PHONY: lint.fix
lint.fix:
	poetry run ruff check --fix $(SRC)

.PHONY: format
format:
	poetry run ruff format $(SRC)

.PHONY: typecheck
typecheck:
	poetry run mypy $(SRC)

.PHONY: test.local
test.local:
	poetry run pytest

.PHONY: test.local.lf
test.local.lf:
	poetry run pytest --last-failed

.PHONY: pre-commit
pre-commit: lint.fix format typecheck

.PHONY: ci
ci: lint typecheck test.local
