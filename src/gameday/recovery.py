import time

from kubernetes.client.exceptions import ApiException

from gameday.models import GameDayScenario
from kubernetes import client


class RecoveryTimeoutError(Exception):
    """Raised when a deployment does not recover within its objective."""


def wait_for_deployment_recovery(
    apps_api: client.AppsV1Api,
    scenario: GameDayScenario,
) -> float:
    namespace = scenario.target.namespace
    deployment_name = scenario.target.deployment
    timeout = scenario.success_criteria.max_recovery_seconds
    start_time = time.monotonic()

    while time.monotonic() - start_time <= timeout:
        try:
            deployment = apps_api.read_namespaced_deployment_status(
                name=deployment_name,
                namespace=namespace,
            )
        except ApiException as error:
            raise RecoveryTimeoutError(
                f"Unable to read deployment status: {error.reason}"
            ) from error

        desired_replicas = deployment.spec.replicas or 0
        available_replicas = deployment.status.available_replicas or 0
        updated_replicas = deployment.status.updated_replicas or 0

        if (
            desired_replicas > 0
            and available_replicas >= desired_replicas
            and updated_replicas >= desired_replicas
        ):
            return round(time.monotonic() - start_time, 2)

        time.sleep(2)

    raise RecoveryTimeoutError(
        f"Deployment {namespace}/{deployment_name} did not recover within {timeout} seconds."
    )
