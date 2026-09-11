from gameday.evaluator import evaluate_scenario
from gameday.injector import KubernetesFailureInjector
from gameday.models import GameDayResult, GameDayScenario
from gameday.recovery import (
    RecoveryTimeoutError,
    wait_for_deployment_recovery,
)
from gameday.safety import validate_safety


def run_scenario(scenario: GameDayScenario) -> GameDayResult:
    validate_safety(scenario)

    if scenario.dry_run:
        return evaluate_scenario(
            scenario=scenario,
            recovery_seconds=0.0,
            availability_percent=100.0,
            error_rate_percent=0.0,
            observations=[
                "Safety validation passed.",
                f"Dry-run validated failure type: {scenario.failure_type.value}.",
                "No Kubernetes resources were changed.",
            ],
        )

    injector = KubernetesFailureInjector()
    observations = injector.inject(scenario)

    try:
        recovery_seconds = wait_for_deployment_recovery(
            apps_api=injector.apps_api,
            scenario=scenario,
        )
    except RecoveryTimeoutError as error:
        recovery_seconds = float(scenario.success_criteria.max_recovery_seconds + 1)
        observations.append(str(error))

    measurement_window = max(
        scenario.success_criteria.max_recovery_seconds,
        1,
    )

    availability_percent = max(
        0.0,
        round(
            100 - (recovery_seconds / measurement_window * 100),
            2,
        ),
    )
    error_rate_percent = round(
        100 - availability_percent,
        2,
    )

    observations.append(
        "Availability and error rate were estimated from the "
        "configured recovery measurement window."
    )

    return evaluate_scenario(
        scenario=scenario,
        recovery_seconds=recovery_seconds,
        availability_percent=availability_percent,
        error_rate_percent=error_rate_percent,
        observations=observations,
    )
