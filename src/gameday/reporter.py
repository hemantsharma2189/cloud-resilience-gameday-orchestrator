import json
from datetime import UTC, datetime
from pathlib import Path

from gameday.models import GameDayResult


def save_json_report(
    result: GameDayResult,
    output_directory: str | Path = "reports",
) -> Path:
    report_directory = Path(output_directory)
    report_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    report_path = report_directory / f"gameday-{timestamp}.json"

    report_data = {
        "generated_at": datetime.now(UTC).isoformat(),
        **result.model_dump(),
    }

    report_path.write_text(
        json.dumps(report_data, indent=2),
        encoding="utf-8",
    )

    return report_path


def save_markdown_report(
    result: GameDayResult,
    output_directory: str | Path = "reports",
) -> Path:
    report_directory = Path(output_directory)
    report_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    report_path = report_directory / f"gameday-{timestamp}.md"

    observations = (
        "\n".join(f"- {observation}" for observation in result.observations)
        or "- No additional observations."
    )

    content = f"""# GameDay Incident Report

## Summary

- **Scenario:** {result.scenario_name}
- **Status:** {result.status}
- **Execution mode:** {"Dry-run" if result.dry_run else "Live"}
- **Recovery time:** {result.recovery_seconds} seconds
- **Availability:** {result.availability_percent}%
- **Error rate:** {result.error_rate_percent}%

## Observations

{observations}

## Decision

{"Recovery objectives were satisfied." if result.passed else "Recovery objectives were not satisfied. Review remediation actions before another experiment."}
"""

    report_path.write_text(content, encoding="utf-8")
    return report_path
