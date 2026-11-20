"""Checks on spec/ and schema/. Part of `just test`."""

from functools import cache
from pathlib import Path
from string import Formatter

import pytest
import yaml
from linkml.validator import validate
from linkml_runtime import SchemaView

ROOT = Path(__file__).parent.parent
SCHEMA = ROOT / "schema/starflake_design.yaml"


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / "spec" / f"{name}.yaml").read_text())


def errors(data: dict, root_class: str) -> list[str]:
    return [
        result.message for result in validate(data, str(SCHEMA), root_class).results
    ]


def duplicate_ids(items: list[dict]) -> set[str]:
    ids = [item["id"] for item in items]
    return {i for i in ids if ids.count(i) > 1}


@cache
def hud_fields() -> set[str]:
    return set(SchemaView(str(SCHEMA)).get_enum("HudField").permissible_values)


def placeholders(template: str) -> set[str]:
    """`{hull}` gives "hull"; `{key:jump}` gives "key:jump"."""
    return {
        f"{field}:{spec}" if spec else field
        for _, field, spec, _ in Formatter().parse(template)
        if field
    }


def key_placeholders() -> set[str]:
    return {f"key:{action['id']}" for action in load("controls")["actions"]}


def unknown_placeholders(hud: dict) -> set[str]:
    used = set().union(
        *(placeholders(item["text"]) for item in hud["readouts"] + hud["messages"])
    )
    return used - hud_fields() - key_placeholders()


def slot_values() -> dict[str, object]:
    """Every scalar or object slot of the spec by its path, like "loot.magnet_speed"."""
    groups = {**load("tuning"), "hud": load("hud"), "camera": load("camera")}
    return {
        f"{group}.{slot}": value
        for group, slots in groups.items()
        for slot, value in slots.items()
        if not isinstance(value, list)
    }


# LinkML has no exclusive minimum: the schema lets these be zero.
POSITIVE = ["enemy_ai.steering_gain", "camera.fov_degrees", "camera.follow_rate"]


def not_positive(values: dict[str, object]) -> set[str]:
    return {path for path in POSITIVE if values[path] <= 0}


def test_schema_imports_the_pinned_ontology():
    view = SchemaView(str(SCHEMA))
    assert "Vector3D" in view.all_classes()
    assert {"Distance", "Speed", "Amount"} <= set(view.all_types())


def test_controls_are_valid():
    controls = load("controls")
    assert errors(controls, "ControlScheme") == []
    assert len(controls["actions"]) == 11


@pytest.mark.parametrize(
    "binding",
    [
        {"device": "keyboard", "button": "left"},
        {"device": "mouse", "key": "KeyW"},
        {"device": "keyboard", "key": "KeyW", "button": "left"},
        {"device": "keyboard"},
        {"device": "keyboard", "key": "KeyZ"},
    ],
)
def test_inconsistent_binding_is_rejected(binding):
    scheme = {"actions": [{"id": "a", "kind": "hold", "bindings": [binding]}]}
    assert errors(scheme, "ControlScheme") != []


def test_action_without_binding_is_rejected():
    assert (
        errors(
            {"actions": [{"id": "a", "kind": "hold", "bindings": []}]}, "ControlScheme"
        )
        != []
    )


def test_duplicate_ids_are_found():
    assert duplicate_ids([{"id": "a"}, {"id": "b"}, {"id": "a"}]) == {"a"}


def test_tuning_and_camera_are_valid():
    assert errors(load("tuning"), "Tuning") == []
    assert errors(load("camera"), "CameraRig") == []


def test_unknown_key_is_rejected():
    tuning = load("tuning")
    tuning["loot"]["pickup_raduis"] = 30
    assert errors(tuning, "Tuning") != []


def test_missing_slot_is_rejected():
    tuning = load("tuning")
    del tuning["loot"]["magnet_speed"]
    assert errors(tuning, "Tuning") != []


@pytest.mark.parametrize(
    "group, slot, value",
    [
        ("flight", "drag_fraction", 1.5),
        ("loot", "pickup_radius", -1),
        ("enemy_ai", "aim_cone", -0.1),
    ],
)
def test_out_of_range_value_is_rejected(group, slot, value):
    tuning = load("tuning")
    tuning[group][slot] = value
    assert errors(tuning, "Tuning") != []


def test_list_slots_have_no_path():
    assert "hud.readouts" not in slot_values()


def test_positive_slots_are_positive():
    assert not_positive(slot_values()) == set()


@pytest.mark.parametrize("path", POSITIVE)
def test_zero_in_a_positive_slot_is_rejected(path):
    assert not_positive(slot_values() | {path: 0}) == {path}


def test_hud_is_valid():
    hud = load("hud")
    assert errors(hud, "Hud") == []
    assert len(hud["readouts"]) == 10 and len(hud["messages"]) == 4
    assert unknown_placeholders(hud) == set()


def test_unknown_placeholder_is_detected():
    hud = load("hud")
    hud["messages"][0]["text"] = "{hul} left, press {key:jmp} or {key:jump}"
    assert unknown_placeholders(hud) == {"hul", "key:jmp"}


def test_controls_help_names_every_action_by_its_key():
    text = next(
        r["text"] for r in load("hud")["readouts"] if r["id"] == "controls_help"
    )
    assert placeholders(text) == key_placeholders()


def test_placeholders_are_extracted():
    assert placeholders("Jump to {target_name}: {fuel_missing} more") == {
        "target_name",
        "fuel_missing",
    }
    assert placeholders("+") == set()


def test_unknown_anchor_is_rejected():
    hud = load("hud")
    hud["readouts"][0]["anchor"] = "top_center"
    assert errors(hud, "Hud") != []


# Size limits. No published limit exists for LinkML modules: 150 lines keeps
# one module per spec file. ESLint's max-lines defaults to 300 for code.
MAX_LINES = {
    "schema/*.yaml": 150,
    "spec/*.yaml": 150,
    "features/*.feature": 150,
    "tests/*.py": 300,
}


@pytest.mark.parametrize("pattern", MAX_LINES)
def test_files_stay_short(pattern):
    lengths = {
        path.name: len(path.read_text().splitlines()) for path in ROOT.glob(pattern)
    }
    assert lengths, pattern
    assert {name: n for name, n in lengths.items() if n > MAX_LINES[pattern]} == {}
