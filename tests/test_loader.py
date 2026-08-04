from io import BytesIO

import pytest

from access_control_analyzer.loader import load_cardholder_csv


def test_loads_every_field_as_text() -> None:
    source = BytesIO(
        b"cardholder_name,badge_number,expiration_date\nTest User,00123,2027-01-01\n"
    )

    result = load_cardholder_csv(source)

    assert result.iloc[0]["badge_number"] == "00123"


def test_rejects_a_csv_without_records() -> None:
    source = BytesIO(b"cardholder_name,badge_number\n")

    with pytest.raises(ValueError, match="contains no records"):
        load_cardholder_csv(source)


def test_rejects_malformed_csv() -> None:
    source = BytesIO(b'cardholder_name,badge_number\n"Unclosed,10001\n')

    with pytest.raises(ValueError, match="not a valid CSV"):
        load_cardholder_csv(source)


def test_rejects_duplicate_headers_before_pandas_renames_them() -> None:
    source = BytesIO(
        b"cardholder_name,badge_number,badge_number\nTest User,10001,10002\n"
    )

    with pytest.raises(ValueError, match="Duplicate columns after normalization"):
        load_cardholder_csv(source)


def test_rejects_duplicate_headers_after_a_leading_blank_line() -> None:
    source = BytesIO(
        b"\ncardholder_name,badge_number,badge_number\nTest User,10001,10002\n"
    )

    with pytest.raises(ValueError, match="Duplicate columns after normalization"):
        load_cardholder_csv(source)
