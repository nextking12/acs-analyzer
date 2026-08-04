import pandas as pd
import pytest

from access_control_analyzer.normalizer import normalize_cardholders


def test_normalizes_columns_values_and_source_rows() -> None:
    dataframe = pd.DataFrame(
        {
            " Cardholder_Name ": [" Test User "],
            "Badge_Number": [" 00123 "],
            "Department": [" Engineering "],
            "Credential_Status": [" ACTIVE "],
            "Expiration_Date": ["2027-01-01"],
        }
    )

    result = normalize_cardholders(dataframe)

    assert result.iloc[0]["_source_row"] == 2
    assert result.iloc[0]["cardholder_name"] == "Test User"
    assert result.iloc[0]["badge_number"] == "00123"
    assert result.iloc[0]["department"] == "Engineering"
    assert result.iloc[0]["credential_status"] == "active"


def test_raises_error_when_required_columns_are_missing() -> None:
    with pytest.raises(ValueError, match="department, expiration_date"):
        normalize_cardholders(
            pd.DataFrame(
                {
                    "cardholder_name": ["Test User"],
                    "badge_number": ["10001"],
                    "credential_status": ["active"],
                }
            )
        )


def test_raises_error_for_columns_that_duplicate_after_normalization() -> None:
    dataframe = pd.DataFrame(
        [["Test User", "Duplicate", "10001", "Engineering", "active", "2027-01-01"]],
        columns=[
            "cardholder_name",
            " Cardholder_Name ",
            "badge_number",
            "department",
            "credential_status",
            "expiration_date",
        ],
    )

    with pytest.raises(ValueError, match="Duplicate columns after normalization"):
        normalize_cardholders(dataframe)
