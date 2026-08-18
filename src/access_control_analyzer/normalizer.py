import pandas as pd

REQUIRED_COLUMNS = {
    "badge_number",
    "cardholder_name",
    "credential_status",
    "department",
    "expiration_date",
}


def normalize_cardholders(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return cardholder data normalized for audit rule evaluation."""
    normalized = dataframe.copy()
    normalized.columns = [column.strip().lower() for column in normalized.columns]

    if normalized.columns.duplicated().any():
        duplicates = sorted(set(normalized.columns[normalized.columns.duplicated()]))
        raise ValueError(
            f"Duplicate columns after normalization: {', '.join(duplicates)}"
        )

    missing_columns = REQUIRED_COLUMNS.difference(normalized.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    text_columns = (
        "badge_number",
        "cardholder_name",
        "credential_status",
        "department",
    )
    for column in text_columns:
        values = normalized[column].astype("string").str.strip()
        normalized[column] = values.mask(values.eq(""))

    normalized["credential_status"] = normalized["credential_status"].str.lower()
    normalized["_source_row"] = range(2, len(normalized) + 2)

    return normalized
