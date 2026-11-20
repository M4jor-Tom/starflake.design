"""Every check on the specification: `just test`."""

from pathlib import Path

import pytest
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


def test_controls_are_valid():
    controls = load("controls")
    assert errors(controls, "ControlScheme") == []
    assert duplicate_ids(controls["actions"]) == set()
    assert len(controls["actions"]) == 11


@pytest.mark.parametrize("binding", [
    {"device": "keyboard", "button": "left"},
    {"device": "mouse", "key": "KeyW"},
    {"device": "keyboard", "key": "KeyW", "button": "left"},
    {"device": "keyboard"},
    {"device": "keyboard", "key": "KeyZ"},
])
def test_inconsistent_binding_is_rejected(binding):
    scheme = {"actions": [{"id": "a", "kind": "hold", "bindings": [binding]}]}
    assert errors(scheme, "ControlScheme") != []


def test_action_without_binding_is_rejected():
    assert errors({"actions": [{"id": "a", "kind": "hold", "bindings": []}]}, "ControlScheme") != []


def test_duplicate_ids_are_found():
    assert duplicate_ids([{"id": "a"}, {"id": "b"}, {"id": "a"}]) == {"a"}


def duplicate_ids(items: list[dict]) -> set[str]:
    ids = [item["id"] for item in items]
    return {i for i in ids if ids.count(i) > 1}
