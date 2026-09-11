from gameday.evaluator import evaluate_scenario
from gameday.models import (
    FailureType,
    GameDayScenario,
    SuccessCriteria,
    Target,
)


def create_scenario() -> GameDayScenario:
    return GameDayScenario(
        name="test-pod-crash",
        description="Test controlled pod failure",
        failure_type=FailureType.POD_CRASH,
        target=Target(
            namespace="gameday-demo",
            deployment="demo-api",
        ),
        dry_run=True,
        success_criteria=SuccessCriteria(
            max_recovery_seconds=120,
            minimum_availability_percent=99.0,
            maximum_error_rate_percent=5.0,
        ),
    )


def test_scenario_passes_when_all_objectives_are_met() -> None:
    result = evaluate_scenario(
        scenario=create_scenario(),
        recovery_seconds=30,
        availability_percent=99.9,
        error_rate_percent=0.1,
    )

    assert result.passed is True
    assert result.status == "PASSED"


def test_scenario_fails_when_recovery_is_too_slow() -> None:
    result = evaluate_scenario(
        scenario=create_scenario(),
        recovery_seconds=150,
        availability_percent=98.0,
        error_rate_percent=7.0,
    )

    assert result.passed is False
    assert result.status == "FAILED"
    assert len(result.observations) == 3
