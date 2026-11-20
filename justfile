# Validate the whole specification.
test: fetch
    uv run pytest

# Fetch the ontology release pinned in design.lock.
fetch:
    tools/fetch-ontology.sh
