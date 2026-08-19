from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime

import pandas as pd

from access_control_analyzer.models import AnalysisSummary, Finding, Severity
from access_control_analyzer.normalizer import normalize_cardholders
from access_control_analyzer.rules import (
    RULE_DEFINITIONS,
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

RULE_IDS = tuple(rule.rule_id for rule in RULE_DEFINITIONS)


@dataclass(frozen=True)
class AnalysisResult:
    summary: AnalysisSummary
    findings: list[Finding]


def _default_analysis_date(as_of_date: date | None) -> date:
    return as_of_date or datetime.now(UTC).date()


def _findings_for_normalized(
    dataframe: pd.DataFrame, *, as_of_date: date
) -> list[Finding]:
    return [
        *find_expired_active_credentials(dataframe, as_of_date=as_of_date),
        *find_missing_or_invalid_expiration_dates(dataframe),
        *find_duplicate_badge_numbers(dataframe),
        *find_active_credentials_missing_departments(dataframe),
    ]


def _summary_for_normalized(
    dataframe: pd.DataFrame,
    findings: list[Finding],
    *,
    analysis_date: date,
) -> AnalysisSummary:
    statuses = dataframe["credential_status"]
    active_credentials = int(statuses.eq("active").sum())
    inactive_credentials = int(statuses.eq("inactive").sum())
    severity_counts = Counter(finding.severity for finding in findings)
    rule_counts = Counter(finding.rule_id for finding in findings)

    return AnalysisSummary(
        analysis_date=analysis_date,
        records_analyzed=len(dataframe),
        active_credentials=active_credentials,
        inactive_credentials=inactive_credentials,
        other_status_credentials=(
            len(dataframe) - active_credentials - inactive_credentials
        ),
        total_findings=len(findings),
        findings_by_severity={
            severity: severity_counts[severity] for severity in Severity
        },
        findings_by_rule={rule_id: rule_counts[rule_id] for rule_id in RULE_IDS},
    )


def run_analysis(
    dataframe: pd.DataFrame,
    *,
    as_of_date: date | None = None,
) -> AnalysisResult:
    analysis_date = _default_analysis_date(as_of_date)
    normalized = normalize_cardholders(dataframe)
    findings = _findings_for_normalized(normalized, as_of_date=analysis_date)
    summary = _summary_for_normalized(
        normalized,
        findings,
        analysis_date=analysis_date,
    )
    return AnalysisResult(summary=summary, findings=findings)


def analyze_cardholders(
    dataframe: pd.DataFrame,
    *,
    as_of_date: date | None = None,
) -> list[Finding]:
    analysis_date = _default_analysis_date(as_of_date)
    normalized = normalize_cardholders(dataframe)
    return _findings_for_normalized(normalized, as_of_date=analysis_date)


def summarize_cardholders(
    dataframe: pd.DataFrame,
    findings: list[Finding],
    *,
    as_of_date: date | None = None,
) -> AnalysisSummary:
    normalized = normalize_cardholders(dataframe)
    return _summary_for_normalized(
        normalized,
        findings,
        analysis_date=_default_analysis_date(as_of_date),
    )


def findings_to_dataframe(findings: list[Finding]) -> pd.DataFrame:
    records = []
    source_columns: dict[str, str] = {}
    reserved = set(FINDING_COLUMNS)

    for finding in findings:
        record = finding.model_dump(mode="json", exclude={"source_data"})
        for column, value in finding.source_data.items():
            output_column = source_columns.get(column)
            if output_column is None:
                output_column = column
                while output_column in reserved:
                    output_column = f"source_{output_column}"
                source_columns[column] = output_column
                reserved.add(output_column)
            record[output_column] = value
        records.append(record)

    return pd.DataFrame(
        records,
        columns=[*FINDING_COLUMNS, *source_columns.values()],
    )
