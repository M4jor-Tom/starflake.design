# Validate the whole specification.
test: lint fetch
    uv run pytest

# Lint and check the formatting of the Python files.
lint:
    ruff check
    ruff format --check

# Fetch the ontology release pinned in design.lock.
fetch:
    tools/fetch-ontology.sh
