"""Every check on the specification: `just test`."""

from pathlib import Path

import yaml
from linkml.validator import validate
from linkml_runtime import SchemaView

ROOT = Path(__file__).parent.parent
SCHEMA = ROOT / "schema/starflake_design.yaml"


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / "spec" / f"{name}.yaml").read_text())


def errors(data: dict, root_class: str) -> list[str]:
    return [result.message for result in validate(data, str(SCHEMA), root_class).results]


def test_schema_imports_the_pinned_ontology():
    view = SchemaView(str(SCHEMA))
    assert "Vector3D" in view.all_classes()
    assert {"Distance", "Speed", "Amount"} <= set(view.all_types())
