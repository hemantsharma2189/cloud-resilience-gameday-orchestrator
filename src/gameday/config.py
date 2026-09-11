from pathlib import Path

import yaml
from pydantic import ValidationError

from gameday.models import GameDayScenario


class ScenarioConfigurationError(Exception):
    """Raised when a game day scenario is missing or invalid."""


def load_scenario(file_path: str | Path) -> GameDayScenario:
    path = Path(file_path)

    if not path.exists():
        raise ScenarioConfigurationError(f"Scenario file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as scenario_file:
            data = yaml.safe_load(scenario_file)
    except yaml.YAMLError as error:
        raise ScenarioConfigurationError(f"Invalid YAML in scenario file: {error}") from error

    if not isinstance(data, dict):
        raise ScenarioConfigurationError(
            "Scenario configuration must contain YAML key-value pairs."
        )

    try:
        return GameDayScenario.model_validate(data)
    except ValidationError as error:
        raise ScenarioConfigurationError(f"Scenario validation failed:\n{error}") from error
