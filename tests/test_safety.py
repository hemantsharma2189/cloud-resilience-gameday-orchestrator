import pytest

from gameday.models import (
    FailureType,
    GameDayScenario,
    Target,
)
from gameday.safety import SafetyViolation, validate_safety


def create_scenario(
    namespace: str,
    dry_run: bool = True,
) -> GameDayScenario:
    return GameDayScenario(
        name="safety-test",
        description="Validate safety policies",
        failure_type=FailureType.POD_CRASH,
        target=Target(
            namespace=namespace,
            deployment="demo-api",
        ),
        dry_run=dry_run,
        require_approval=True,
    )


def test_dry_run_is_allowed_in_application_namespace() -> None:
    scenario = create_scenario("gameday-demo")

    validate_safety(scenario)


def test_protected_namespace_is_blocked() -> None:
    scenario = create_scenario("kube-system")

    with pytest.raises(SafetyViolation):
        validate_safety(scenario)


def test_live_execution_requires_approval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GAMEDAY_APPROVED", raising=False)
    scenario = create_scenario(
        namespace="gameday-demo",
        dry_run=False,
    )

    with pytest.raises(SafetyViolation):
        validate_safety(scenario)


def test_live_execution_with_approval_is_allowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GAMEDAY_APPROVED", "true")
    scenario = create_scenario(
        namespace="gameday-demo",
        dry_run=False,
    )

    validate_safety(scenario)
