"""Every check on the specification: `just test`."""

import re
from pathlib import Path
from string import Formatter

import pytest
import yaml
from gherkin.parser import Parser
from linkml.validator import validate
from linkml_runtime import SchemaView

ROOT = Path(__file__).parent.parent
SCHEMA = ROOT / "schema/starflake_design.yaml"


def load(name: str) -> dict:
    return yaml.safe_load((ROOT / "spec" / f"{name}.yaml").read_text())


def errors(data: dict, root_class: str) -> list[str]:
    return [result.message for result in validate(data, str(SCHEMA), root_class).results]


def duplicate_ids(items: list[dict]) -> set[str]:
    ids = [item["id"] for item in items]
    return {i for i in ids if ids.count(i) > 1}


def hud_fields() -> set[str]:
    return set(SchemaView(str(SCHEMA)).get_enum("HudField").permissible_values)


def placeholders(template: str) -> set[str]:
    return {field for _, field, _, _ in Formatter().parse(template) if field}


def known_references() -> set[str]:
    hud, camera = load("hud"), load("camera")
    ids = {item["id"] for item in load("controls")["actions"] + hud["readouts"] + hud["messages"]}
    groups = {**load("tuning"), "hud": hud, "camera": camera}
    paths = {
        f"{group}.{slot}"
        for group, slots in groups.items()
        for slot, value in slots.items()
        if not isinstance(value, list)
    }
    return ids | paths


def scenarios(feature_text: str) -> list[dict]:
    """Scenarios and backgrounds of a feature, including those inside rules."""
    found = []
    children = Parser().parse(feature_text)["feature"]["children"]
    for child in children:
        if "rule" in child:
            children.extend(child["rule"]["children"])
        else:
            found.append(child)
    return found


def references(feature_text: str) -> set[str]:
    return {
        quoted
        for child in scenarios(feature_text)
        for block in child.values()
        for step in block["steps"]
        for quoted in re.findall(r'"([^"]*)"', step["text"])
    }


def scenario_count(feature_text: str) -> int:
    return sum("scenario" in child for child in scenarios(feature_text))


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


@pytest.mark.parametrize("group, slot, value", [
    ("flight", "drag_fraction", 1.5),
    ("loot", "pickup_radius", -1),
    ("enemy_ai", "aim_cone", -0.1),
])
def test_out_of_range_value_is_rejected(group, slot, value):
    tuning = load("tuning")
    tuning[group][slot] = value
    assert errors(tuning, "Tuning") != []


def test_hud_is_valid():
    hud = load("hud")
    assert errors(hud, "Hud") == []
    assert duplicate_ids(hud["readouts"] + hud["messages"]) == set()
    assert len(hud["readouts"]) == 10 and len(hud["messages"]) == 4
    fields = hud_fields()
    for item in hud["readouts"] + hud["messages"]:
        assert placeholders(item["text"]) <= fields, item["id"]


def test_placeholders_are_extracted():
    assert placeholders("Jump to {target_name}: {fuel_missing} more") == {"target_name", "fuel_missing"}
    assert placeholders("+") == set()


def test_unknown_anchor_is_rejected():
    hud = load("hud")
    hud["readouts"][0]["anchor"] = "top_center"
    assert errors(hud, "Hud") != []


# Minimum scenarios per feature: one per rule of the design document.
SCENARIOS = {
    "session": 3, "flight": 5, "combat": 6, "loot": 3, "jump": 4,
    "respawn": 1, "enemy_ai": 4, "hud": 4, "camera": 2,
}


def test_known_references_cover_ids_and_slot_paths():
    known = known_references()
    assert {"jump", "jump_refused", "fuel_tank_full", "loot.pickup_radius",
            "enemy_ai.aim_cone", "hud.message_duration_seconds", "camera.follow_rate"} <= known
    assert "hud.readouts" not in known


def test_references_are_extracted_from_steps():
    text = '''Feature: f
  Scenario: s
    Given a drop within the "loot.pickup_radius"
    When the player presses "jump"
    Then the HUD flashes "jumped"
'''
    assert references(text) == {"loot.pickup_radius", "jump", "jumped"}
    assert scenario_count(text) == 1


def test_unresolved_reference_is_detected():
    assert not {"loot.pickup_radus", "jmp"} & known_references()


@pytest.mark.parametrize("name", SCENARIOS)
def test_features(name):
    text = (ROOT / "features" / f"{name}.feature").read_text()
    assert references(text) <= known_references()
    assert scenario_count(text) >= SCENARIOS[name]


def test_every_feature_file_is_checked():
    assert {path.stem for path in (ROOT / "features").glob("*.feature")} == set(SCENARIOS)
