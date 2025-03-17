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

.PHONY: release-tag  # Usage: make release-tag VERSION=1.0.0 MESSAGE="Release notes here"
release-tag:
	@if [ -z "$(VERSION)" ]; then \
		echo "Error: VERSION is required. Use 'make release-tag VERSION=1.0.0 MESSAGE=\"Your release notes\"'"; \
		exit 1; \
	fi
	@MESSAGE_TEXT="Release version $(VERSION)"; \
	if [ ! -z "$(MESSAGE)" ]; then \
		MESSAGE_TEXT="$(MESSAGE)"; \
	fi; \
	echo "Release message: $$MESSAGE_TEXT"
	@echo "Checking if tag v$(VERSION) already exists..."
	@if git tag | grep -q "^v$(VERSION)$$"; then \
		echo "Error: Tag v$(VERSION) already exists. Choose a different version."; \
		exit 1; \
	fi
	@echo "Updating remote URL to new repository location..."
	git remote set-url origin https://github.com/Future-Energy-Associates/OpenTariff.git
	@echo "Updating version to $(VERSION) in pyproject.toml..."
	@python -c "import re; \
		content = open('pyproject.toml', 'r').read(); \
		new_content = re.sub(r'version = \".*\"', f'version = \"$(VERSION)\"', content); \
		open('pyproject.toml', 'w').write(new_content)"
	@echo "Committing version change..."
	git add pyproject.toml
	git commit -m "Bump version to $(VERSION)"
	@echo "Creating and pushing tag v$(VERSION)..."
	git checkout main
	git pull
	git push origin main
	@MESSAGE_TEXT="Release version $(VERSION)"; \
	if [ ! -z "$(MESSAGE)" ]; then \
		MESSAGE_TEXT="$(MESSAGE)"; \
	fi; \
	git tag -a v$(VERSION) -m "$$MESSAGE_TEXT"
	git push origin v$(VERSION)
	@echo "Version updated to $(VERSION) and tag v$(VERSION) created and pushed successfully!"