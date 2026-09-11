from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

from gameday.models import FailureType, GameDayScenario


class FailureInjectionError(Exception):
    """Raised when a controlled failure cannot be injected."""


class KubernetesFailureInjector:
    def __init__(self) -> None:
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()

        self.apps_api = client.AppsV1Api()
        self.core_api = client.CoreV1Api()

    def inject(self, scenario: GameDayScenario) -> list[str]:
        if scenario.dry_run:
            return [
                "Dry-run: no resources were changed.",
                (f"Would inject {scenario.failure_type.value} into "
                f"{scenario.target.namespace}/{scenario.target.deployment}."),
            ]

        if scenario.failure_type != FailureType.POD_CRASH:
            raise FailureInjectionError(
                f"Live injection is not implemented for {scenario.failure_type.value}."
            )

        return self._delete_deployment_pod(scenario)

    def _delete_deployment_pod(
        self,
        scenario: GameDayScenario,
    ) -> list[str]:
        namespace = scenario.target.namespace
        deployment_name = scenario.target.deployment

        try:
            deployment = self.apps_api.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
            )

            labels = deployment.spec.selector.match_labels or {}
            selector = ",".join(f"{key}={value}" for key, value in labels.items())

            pods = self.core_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=selector,
            ).items

            if not pods:
                raise FailureInjectionError(f"No pods found for deployment {deployment_name}.")

            pod_name = pods[0].metadata.name

            self.core_api.delete_namespaced_pod(
                name=pod_name,
                namespace=namespace,
                grace_period_seconds=0,
            )

            return [
                f"Deleted pod {namespace}/{pod_name}.",
                "Kubernetes Deployment controller should create a replacement.",
            ]

        except ApiException as error:
            raise FailureInjectionError(f"Kubernetes API request failed: {error.reason}") from error
