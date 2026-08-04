from datetime import date

import pandas as pd
import pytest

from access_control_analyzer.rules import (
    find_expired_active_credentials,
)


def test_returns_only_expired_active_credentials() -> None:
    dataframe = pd.DataFrame(
        {
            "cardholder_name": [
                "Expired Active",
                "Valid Active",
                "Expired Inactive",
                "Missing Date",
            ],
            "badge_number": [
                "10001",
                "10002",
                "10003",
                "10004",
            ],
            "credential_status": [
                "active",
                "active",
                "inactive",
                "active",
            ],
            "expiration_date": [
                "2025-12-31",
                "2027-01-01",
                "2025-01-01",
                None,
            ],
        }
    )

    results = find_expired_active_credentials(
        dataframe,
        as_of_date=date(2026, 7, 28),
    )

    assert len(results) == 1
    assert results.iloc[0]["badge_number"] == "10001"


def test_status_matching_is_case_insensitive() -> None:
    dataframe = pd.DataFrame(
        {
            "cardholder_name": ["Test User"],
            "badge_number": ["10001"],
            "credential_status": [" ACTIVE "],
            "expiration_date": ["2025-12-31"],
        }
    )

    results = find_expired_active_credentials(
        dataframe,
        as_of_date=date(2026, 7, 28),
    )

    assert len(results) == 1


def test_raises_error_when_required_columns_are_missing() -> None:
    dataframe = pd.DataFrame(
        {
            "cardholder_name": ["Test User"],
        }
    )

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        find_expired_active_credentials(dataframe)