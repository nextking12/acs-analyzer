from collections import Counter
from datetime import UTC, date, datetime

import pandas as pd

from access_control_analyzer.models import AnalysisSummary, Finding, Severity
from access_control_analyzer.normalizer import normalize_cardholders
from access_control_analyzer.rules import (
    find_active_credentials_missing_departments,
    find_duplicate_badge_numbers,
    find_expired_active_credentials,
    find_missing_or_invalid_expiration_dates,
)

FINDING_COLUMNS = [
    "rule_id",
    "rule_name",
    "severity",
    "source_row",
    "cardholder_name",
    "badge_number",
    "description",
    "recommended_action",
]

RULE_IDS = (
    "expired_active_credential",
    "missing_or_invalid_expiration",
    "duplicate_badge_number",
    "active_missing_department",
)


def analyze_cardholders(
    dataframe: pd.DataFrame,
    *,
    as_of_date: date | None = None,
) -> list[Finding]:
    normalized = normalize_cardholders(dataframe)

    return [
        *find_expired_active_credentials(normalized, as_of_date=as_of_date),
        *find_missing_or_invalid_expiration_dates(normalized),
        *find_duplicate_badge_numbers(normalized),
        *find_active_credentials_missing_departments(normalized),
    ]


def summarize_cardholders(
    dataframe: pd.DataFrame,
    findings: list[Finding],
    *,
    as_of_date: date | None = None,
) -> AnalysisSummary:
    normalized = normalize_cardholders(dataframe)
    statuses = normalized["credential_status"]
    active_credentials = int(statuses.eq("active").sum())
    inactive_credentials = int(statuses.eq("inactive").sum())
    severity_counts = Counter(finding.severity for finding in findings)
    rule_counts = Counter(finding.rule_id for finding in findings)

    return AnalysisSummary(
        analysis_date=as_of_date or datetime.now(UTC).date(),
        records_analyzed=len(normalized),
        active_credentials=active_credentials,
        inactive_credentials=inactive_credentials,
        other_status_credentials=(
            len(normalized) - active_credentials - inactive_credentials
        ),
        total_findings=len(findings),
        findings_by_severity={
            severity: severity_counts[severity] for severity in Severity
        },
        findings_by_rule={rule_id: rule_counts[rule_id] for rule_id in RULE_IDS},
    )


def findings_to_dataframe(findings: list[Finding]) -> pd.DataFrame:
    records = []
    source_columns: dict[str, str] = {}

    for finding in findings:
        record = finding.model_dump(mode="json", exclude={"source_data"})
        for column, value in finding.source_data.items():
            if column not in source_columns:
                output_column = column
                reserved_columns = {*FINDING_COLUMNS, *source_columns.values()}
                while output_column in reserved_columns:
                    output_column = f"source_{output_column}"
                source_columns[column] = output_column
            record[source_columns[column]] = value
        records.append(record)

    return pd.DataFrame(
        records,
        columns=[*FINDING_COLUMNS, *source_columns.values()],
    )
