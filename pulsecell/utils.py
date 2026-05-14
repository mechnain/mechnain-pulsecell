"""File and serialization helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from pulsecell.models import ScenarioConfig


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_scenario_json(path: str | Path) -> ScenarioConfig:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return ScenarioConfig.from_dict(data)


def scenario_to_json(scenario: ScenarioConfig) -> str:
    return json.dumps(scenario.to_dict(), indent=2)


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def load_example_scenarios() -> dict[str, ScenarioConfig]:
    examples_dir = project_root() / "examples"
    scenarios: dict[str, ScenarioConfig] = {}
    if not examples_dir.exists():
        return scenarios
    for path in sorted(examples_dir.glob("*.json")):
        scenario = load_scenario_json(path)
        scenarios[scenario.scenario_name] = scenario
    return scenarios
