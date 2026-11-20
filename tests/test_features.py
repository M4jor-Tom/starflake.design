"""Checks on features/. Part of `just test`."""

import re

import pytest
from gherkin.parser import Parser
from test_spec import ROOT, duplicate_ids, load, slot_values

# Minimum scenarios per feature: one per rule of the design document.
SCENARIOS = {
    "session": 3,
    "flight": 4,
    "system_bounds": 1,
    "combat": 5,
    "destruction": 1,
    "loot": 3,
    "jump": 4,
    "respawn": 1,
    "enemy_ai": 4,
    "hud": 4,
    "camera": 2,
}
# gplint's and gherkin-lint's max-scenarios-per-file default.
MAX_SCENARIOS = 10
# gherkin_lint's TooManySteps flags a scenario of 10 steps or more.
MAX_STEPS = 9


def identified() -> dict[str, list[dict]]:
    """Everything a step can quote by id, by kind."""
    hud = load("hud")
    return {
        "action": load("controls")["actions"],
        "readout": hud["readouts"],
        "message": hud["messages"],
    }


def kind(step_text: str, reference: str) -> str:
    """What a quoted reference must name, judged by the wording of its step."""
    if "." in reference:
        return "slot"
    if "HUD shows" in step_text:
        return "readout"
    if "flashes" in step_text or "show" in step_text:
        return "message"
    return "action"


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


def unresolved(feature_text: str) -> set[str]:
    """Quoted references that do not name something of the kind their step expects."""
    known = {
        name: {item["id"] for item in items} for name, items in identified().items()
    }
    known["slot"] = set(slot_values())
    return {
        quoted
        for child in scenarios(feature_text)
        for block in child.values()
        for step in block["steps"]
        for quoted in re.findall(r'"([^"]*)"', step["text"])
        if quoted not in known[kind(step["text"], quoted)]
    }


def scenario_count(feature_text: str) -> int:
    return sum("scenario" in child for child in scenarios(feature_text))


def test_ids_are_unique_across_files():
    assert duplicate_ids(sum(identified().values(), [])) == set()


def test_unresolved_references_are_detected():
    text = """Feature: f
  Scenario: s
    Given a drop within the "loot.pickup_radius"
    And a drop within the "loot.pickup_radus"
    When the player presses "jump"
    And the player presses "jmp"
    And the player presses "welcome"
    Then the HUD flashes "jumped"
    And the HUD shows "ship_destroyed"
"""
    assert unresolved(text) == {"loot.pickup_radus", "jmp", "welcome", "ship_destroyed"}
    assert scenario_count(text) == 1


@pytest.mark.parametrize("name", SCENARIOS)
def test_features(name):
    text = (ROOT / "features" / f"{name}.feature").read_text()
    assert unresolved(text) == set()
    assert scenario_count(text) >= SCENARIOS[name]


def test_every_feature_file_is_checked():
    assert {path.stem for path in (ROOT / "features").glob("*.feature")} == set(
        SCENARIOS
    )


@pytest.mark.parametrize("name", SCENARIOS)
def test_features_stay_small(name):
    text = (ROOT / "features" / f"{name}.feature").read_text()
    assert scenario_count(text) <= MAX_SCENARIOS
    steps = {
        block["name"]: len(block["steps"])
        for child in scenarios(text)
        for block in child.values()
    }
    assert {title: n for title, n in steps.items() if n > MAX_STEPS} == {}
