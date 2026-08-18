from dataclasses import dataclass
from datetime import UTC, date, datetime

import pandas as pd

from access_control_analyzer.models import Finding, Severity


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    name: str
    severity: Severity
    recommended_action: str


RULE_DEFINITIONS = (
    RuleDefinition(
        "expired_active_credential",
        "Expired active credential",
        Severity.HIGH,
        "Disable the credential or confirm and update its expiration date.",
    ),
    RuleDefinition(
        "missing_or_invalid_expiration",
        "Missing or invalid expiration date",
        Severity.HIGH,
        "Set a valid expiration date or disable the credential.",
    ),
    RuleDefinition(
        "duplicate_badge_number",
        "Duplicate badge number",
        Severity.HIGH,
        "Verify ownership and assign a unique badge number to each record.",
    ),
    RuleDefinition(
        "active_missing_department",
        "Active credential missing department",
        Severity.MEDIUM,
        "Assign the cardholder to the appropriate department.",
    ),
)


RULES = {definition.rule_id: definition for definition in RULE_DEFINITIONS}


def _value_or_none(value: object) -> str | None:
    return None if pd.isna(value) else str(value)


def _expiration_dates(dataframe: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(
        dataframe["expiration_date"],
        errors="coerce",
        format="mixed",
        utc=True,
    )


def _finding(
    row: pd.Series,
    *,
    rule: RuleDefinition,
    description: str,
) -> Finding:
    return Finding(
        rule_id=rule.rule_id,
        rule_name=rule.name,
        severity=rule.severity,
        source_row=int(row["_source_row"]),
        cardholder_name=_value_or_none(row["cardholder_name"]),
        badge_number=_value_or_none(row["badge_number"]),
        description=description,
        recommended_action=rule.recommended_action,
        source_data={
            str(column): _value_or_none(value)
            for column, value in row.items()
            if column not in {"_source_row", "cardholder_name", "badge_number"}
        },
    )


def find_expired_active_credentials(
    dataframe: pd.DataFrame,
    *,
    as_of_date: date | None = None,
) -> list[Finding]:
    comparison_date = pd.Timestamp(
        as_of_date or datetime.now(UTC).date(),
        tz="UTC",
    )
    expiration_dates = _expiration_dates(dataframe)
    rule = RULES["expired_active_credential"]
    mask = (
        dataframe["credential_status"].eq("active")
        & expiration_dates.notna()
        & expiration_dates.lt(comparison_date)
    )

    return [
        _finding(
            row,
            rule=rule,
            description=(
                f"Active credential expired on {expiration.date().isoformat()}."
            ),
        )
        for (_, row), expiration in zip(
            dataframe.loc[mask].iterrows(),
            expiration_dates.loc[mask],
            strict=True,
        )
    ]


def find_missing_or_invalid_expiration_dates(
    dataframe: pd.DataFrame,
) -> list[Finding]:
    expiration_dates = _expiration_dates(dataframe)
    mask = dataframe["credential_status"].eq("active") & expiration_dates.isna()
    rule = RULES["missing_or_invalid_expiration"]

    return [
        _finding(
            row,
            rule=rule,
            description="Active credential has no valid expiration date.",
        )
        for _, row in dataframe.loc[mask].iterrows()
    ]


def find_duplicate_badge_numbers(dataframe: pd.DataFrame) -> list[Finding]:
    duplicate_mask = dataframe["badge_number"].notna() & dataframe[
        "badge_number"
    ].duplicated(keep=False)
    duplicate_counts = dataframe.loc[duplicate_mask, "badge_number"].value_counts()
    rule = RULES["duplicate_badge_number"]

    return [
        _finding(
            row,
            rule=rule,
            description=(
                "Badge number is assigned to "
                f"{duplicate_counts[row['badge_number']]} records."
            ),
        )
        for _, row in dataframe.loc[duplicate_mask].iterrows()
    ]


def find_active_credentials_missing_departments(
    dataframe: pd.DataFrame,
) -> list[Finding]:
    mask = dataframe["credential_status"].eq("active") & dataframe["department"].isna()
    rule = RULES["active_missing_department"]

    return [
        _finding(
            row,
            rule=rule,
            description="Active credential is not assigned to a department.",
        )
        for _, row in dataframe.loc[mask].iterrows()
    ]
