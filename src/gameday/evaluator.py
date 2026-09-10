from gameday.models import GameDayResult, GameDayScenario


def evaluate_scenario(
    scenario: GameDayScenario,
    recovery_seconds: float,
    availability_percent: float,
    error_rate_percent: float,
    observations: list[str] | None = None,
) -> GameDayResult:
    criteria = scenario.success_criteria

    recovery_passed = (
        recovery_seconds <= criteria.max_recovery_seconds
    )
    availability_passed = (
        availability_percent
        >= criteria.minimum_availability_percent
    )
    error_rate_passed = (
        error_rate_percent
        <= criteria.maximum_error_rate_percent
    )

    passed = (
        recovery_passed
        and availability_passed
        and error_rate_passed
    )

    result_observations = list(observations or [])

    if not recovery_passed:
        result_observations.append(
            "Recovery time exceeded the configured objective."
        )

    if not availability_passed:
        result_observations.append(
            "Availability dropped below the configured SLO."
        )

    if not error_rate_passed:
        result_observations.append(
            "Error rate exceeded the configured threshold."
        )

    return GameDayResult(
        scenario_name=scenario.name,
        status="PASSED" if passed else "FAILED",
        dry_run=scenario.dry_run,
        recovery_seconds=recovery_seconds,
        availability_percent=availability_percent,
        error_rate_percent=error_rate_percent,
        passed=passed,
        observations=result_observations,
    )
