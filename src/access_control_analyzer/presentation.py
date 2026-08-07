from pathlib import Path

import pandas as pd

from access_control_analyzer.models import AnalysisSummary, Severity

CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

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

AUDIT_RULE_GUIDE: tuple[tuple[str, str], ...] = (
    ("Expired active credential", "High"),
    ("Missing or invalid expiration date on an active credential", "High"),
    ("Duplicate nonblank badge number", "High"),
    ("Active credential missing a department", "Medium"),
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


def sanitize_csv_cell(value: object) -> str:
    if value is None:
        return ""
    try:
        if bool(pd.isna(value)):  # type: ignore[call-overload]
            return ""
    except (TypeError, ValueError):
        pass

    text = str(value)
    if text.startswith(CSV_FORMULA_PREFIXES):
        return f"'{text}"
    return text


def dataframe_to_safe_csv(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        return dataframe.to_csv(index=False)

    sanitized = dataframe.copy()
    for column in sanitized.columns:
        sanitized[column] = sanitized[column].map(sanitize_csv_cell)
    return sanitized.to_csv(index=False)
