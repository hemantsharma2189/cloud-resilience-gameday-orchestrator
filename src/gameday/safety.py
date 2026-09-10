import os

from gameday.models import GameDayScenario


PROTECTED_NAMESPACES = {
    "kube-system",
    "kube-public",
    "kube-node-lease",
    "argocd",
    "monitoring",
}


class SafetyViolation(Exception):
    """Raised when a scenario violates a safety policy."""


def validate_safety(scenario: GameDayScenario) -> None:
    namespace = scenario.target.namespace

    if namespace in PROTECTED_NAMESPACES:
        raise SafetyViolation(
            f"Failure injection is blocked for protected namespace: {namespace}"
        )

    if scenario.dry_run:
        return

    if scenario.require_approval:
        approval = os.getenv("GAMEDAY_APPROVED", "").lower()

        if approval != "true":
            raise SafetyViolation(
                "Live execution requires GAMEDAY_APPROVED=true."
            )


def execution_mode(scenario: GameDayScenario) -> str:
    return "DRY-RUN" if scenario.dry_run else "LIVE"
