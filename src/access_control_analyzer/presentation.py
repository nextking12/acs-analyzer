from pathlib import Path

from access_control_analyzer.models import AnalysisSummary, Severity
from access_control_analyzer.rules import RULE_DEFINITIONS

CORE_SUMMARY_METRICS: tuple[tuple[str, str], ...] = (
    ("Records analyzed", "records_analyzed"),
    ("Active credentials", "active_credentials"),
    ("Inactive credentials", "inactive_credentials"),
    ("Total findings", "total_findings"),
    ("High-severity findings", "high_findings"),
    ("Medium-severity findings", "medium_findings"),
)

OTHER_STATUS_LABEL = "Other / missing status credentials"

SAMPLE_CARDHOLDERS_RELATIVE = Path("sample_data") / "sample_cardholders.csv"

WORKFLOW_STEPS: tuple[str, ...] = (
    "Load a cardholder CSV export, or use the built-in synthetic sample.",
    "Review the analysis summary and filtered audit findings.",
    "Download the detailed findings CSV for investigation.",
    "Download or print the executive report for stakeholders.",
)

AUDIT_RULE_GUIDE: tuple[tuple[str, str], ...] = tuple(
    (rule.guide_name or rule.name, rule.severity.value) for rule in RULE_DEFINITIONS
)

REQUIRED_CSV_COLUMNS: tuple[str, ...] = (
    "cardholder_name",
    "badge_number",
    "department",
    "credential_status",
    "expiration_date",
)


def get_sample_cardholder_path() -> Path:
    candidates = (
        Path.cwd() / SAMPLE_CARDHOLDERS_RELATIVE,
        Path(__file__).resolve().parents[2] / SAMPLE_CARDHOLDERS_RELATIVE,
    )
    for path in candidates:
        if path.is_file():
            return path.resolve()

    raise FileNotFoundError(
        "Sample cardholder CSV not found. Expected "
        f"{SAMPLE_CARDHOLDERS_RELATIVE.as_posix()} in the project root."
    )


def build_summary_metrics(summary: AnalysisSummary) -> list[tuple[str, int]]:
    high = summary.findings_by_severity.get(Severity.HIGH, 0)
    medium = summary.findings_by_severity.get(Severity.MEDIUM, 0)

    values: dict[str, int] = {
        "records_analyzed": summary.records_analyzed,
        "active_credentials": summary.active_credentials,
        "inactive_credentials": summary.inactive_credentials,
        "total_findings": summary.total_findings,
        "high_findings": high,
        "medium_findings": medium,
    }

    metrics = [(label, values[key]) for label, key in CORE_SUMMARY_METRICS]

    if summary.other_status_credentials:
        metrics.append((OTHER_STATUS_LABEL, summary.other_status_credentials))

    return metrics
