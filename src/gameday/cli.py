import argparse
import sys

from rich.console import Console
from rich.table import Table

from gameday.config import (
    ScenarioConfigurationError,
    load_scenario,
)
from gameday.injector import FailureInjectionError
from gameday.recovery import RecoveryTimeoutError
from gameday.reporter import (
    save_json_report,
    save_markdown_report,
)
from gameday.runner import run_scenario
from gameday.safety import SafetyViolation

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=("Run a controlled Kubernetes resilience GameDay scenario.")
    )
    parser.add_argument(
        "scenario",
        help="Path to the YAML scenario configuration.",
    )
    parser.add_argument(
        "--output",
        default="reports",
        help="Directory where reports will be saved.",
    )
    return parser


def display_result(result) -> None:
    table = Table(title="Cloud Resilience GameDay Result")
    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Scenario", result.scenario_name)
    table.add_row("Status", result.status)
    table.add_row("Dry run", str(result.dry_run))
    table.add_row(
        "Recovery time",
        f"{result.recovery_seconds} seconds",
    )
    table.add_row(
        "Availability",
        f"{result.availability_percent}%",
    )
    table.add_row(
        "Error rate",
        f"{result.error_rate_percent}%",
    )

    console.print(table)

    for observation in result.observations:
        console.print(f"- {observation}")


def main() -> None:
    parser = build_parser()
    arguments = parser.parse_args()

    try:
        scenario = load_scenario(arguments.scenario)
        result = run_scenario(scenario)

        json_report = save_json_report(result, arguments.output)
        markdown_report = save_markdown_report(
            result,
            arguments.output,
        )

        display_result(result)
        console.print(f"JSON report: {json_report}")
        console.print(f"Markdown report: {markdown_report}")

        if not result.passed:
            sys.exit(1)

    except (
        ScenarioConfigurationError,
        SafetyViolation,
        FailureInjectionError,
        RecoveryTimeoutError,
    ) as error:
        console.print(f"[red]GameDay failed:[/red] {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
