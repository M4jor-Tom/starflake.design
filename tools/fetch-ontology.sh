#!/usr/bin/env bash
# Clone the ontology release pinned in design.lock into .ontology/ (gitignored).
# Override for an unpublished local checkout:
#   STARFLAKE_ONTOLOGY_REPO=file://$PWD/../ontology tools/fetch-ontology.sh
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck source=../design.lock
source design.lock

if [ "$(git -C .ontology describe --tags --exact-match 2>/dev/null)" = "$ONTOLOGY_REF" ] \
  && [ "$(git -C .ontology rev-parse --show-toplevel)" = "$PWD/.ontology" ]; then
  exit 0
fi
rm -rf .ontology
git -c advice.detachedHead=false clone --quiet --depth 1 --branch "$ONTOLOGY_REF" \
  "${STARFLAKE_ONTOLOGY_REPO:-$ONTOLOGY_REPO}" .ontology
