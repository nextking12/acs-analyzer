from datetime import UTC, date, datetime

import pandas as pd

REQUIRED_COLUMNS = {
    "cardholder_name",
    "badge_number",
    "credential_status",
    "expiration_date",
}


def find_expired_active_credentials(
    dataframe: pd.DataFrame,
    *,
    as_of_date: date | None = None,
) -> pd.DataFrame:
    """
    Return active credentials whose expiration date is before as_of_date.

    Records with missing or invalid expiration dates are not included.
    Those records should be handled by a separate data-quality rule.
    """
    missing_columns = REQUIRED_COLUMNS.difference(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    comparison_date = pd.Timestamp(as_of_date or datetime.now(UTC).date())

    normalized_status = (
        dataframe["credential_status"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    expiration_dates = pd.to_datetime(
        dataframe["expiration_date"],
        errors="coerce",
    )

    expired_active_mask = (
        normalized_status.eq("active")
        & expiration_dates.notna()
        & expiration_dates.lt(comparison_date)
    )

    results = dataframe.loc[expired_active_mask].copy()
    results["expiration_date"] = expiration_dates.loc[expired_active_mask]

    return results
