from datetime import UTC, date, datetime

import pandas as pd

from access_control_analyzer.models import Finding, Severity


def _value_or_none(value: object) -> str | None:
    return None if pd.isna(value) else str(value)


def _finding(
    row: pd.Series,
    *,
    rule_id: str,
    rule_name: str,
    severity: Severity,
    description: str,
    recommended_action: str,
) -> Finding:
    return Finding(
        rule_id=rule_id,
        rule_name=rule_name,
        severity=severity,
        source_row=int(row["_source_row"]),
        cardholder_name=_value_or_none(row["cardholder_name"]),
        badge_number=_value_or_none(row["badge_number"]),
        description=description,
        recommended_action=recommended_action,
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
    expiration_dates = pd.to_datetime(
        dataframe["expiration_date"],
        errors="coerce",
        format="mixed",
        utc=True,
    )
    mask = (
        dataframe["credential_status"].eq("active")
        & expiration_dates.notna()
        & expiration_dates.lt(comparison_date)
    )

    return [
        _finding(
            row,
            rule_id="expired_active_credential",
            rule_name="Expired active credential",
            severity=Severity.HIGH,
            description=(
                f"Active credential expired on {expiration.date().isoformat()}."
            ),
            recommended_action=(
                "Disable the credential or confirm and update its expiration date."
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
    expiration_dates = pd.to_datetime(
        dataframe["expiration_date"],
        errors="coerce",
        format="mixed",
        utc=True,
    )
    mask = dataframe["credential_status"].eq("active") & expiration_dates.isna()

    return [
        _finding(
            row,
            rule_id="missing_or_invalid_expiration",
            rule_name="Missing or invalid expiration date",
            severity=Severity.HIGH,
            description="Active credential has no valid expiration date.",
            recommended_action="Set a valid expiration date or disable the credential.",
        )
        for _, row in dataframe.loc[mask].iterrows()
    ]


def find_duplicate_badge_numbers(dataframe: pd.DataFrame) -> list[Finding]:
    duplicate_mask = dataframe["badge_number"].notna() & dataframe[
        "badge_number"
    ].duplicated(keep=False)
    duplicate_counts = dataframe.loc[duplicate_mask, "badge_number"].value_counts()

    return [
        _finding(
            row,
            rule_id="duplicate_badge_number",
            rule_name="Duplicate badge number",
            severity=Severity.HIGH,
            description=(
                "Badge number is assigned to "
                f"{duplicate_counts[row['badge_number']]} records."
            ),
            recommended_action=(
                "Verify ownership and assign a unique badge number to each record."
            ),
        )
        for _, row in dataframe.loc[duplicate_mask].iterrows()
    ]


def find_active_credentials_missing_departments(
    dataframe: pd.DataFrame,
) -> list[Finding]:
    mask = dataframe["credential_status"].eq("active") & dataframe["department"].isna()

    return [
        _finding(
            row,
            rule_id="active_missing_department",
            rule_name="Active credential missing department",
            severity=Severity.MEDIUM,
            description="Active credential is not assigned to a department.",
            recommended_action="Assign the cardholder to the appropriate department.",
        )
        for _, row in dataframe.loc[mask].iterrows()
    ]
