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

.PHONY: release-tag

# Usage: make release-tag VERSION=1.0.0
release-tag:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required. Use 'make release-tag VERSION=1.0.0'"; \
		exit 1; \
	fi
	@echo "Creating and pushing tag v$(VERSION)..."
	git checkout main
	git pull
	git tag -a v$(VERSION) -m "Release version $(VERSION)"
	git push origin v$(VERSION)
	@echo "Tag v$(VERSION) created and pushed successfully!"
