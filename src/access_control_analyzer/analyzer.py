from datetime import date

import pandas as pd

from access_control_analyzer.models import Finding
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
