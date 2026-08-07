from io import BytesIO
from pathlib import Path

import pytest

from access_control_analyzer.loader import (
    MAX_RECORDS,
    MAX_UPLOAD_BYTES,
    load_cardholder_csv,
)


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


def test_loads_utf8_bom_csv() -> None:
    source = BytesIO(b"\xef\xbb\xbfcardholder_name,badge_number\nTest User,00123\n")

    result = load_cardholder_csv(source)

    assert list(result.columns) == ["cardholder_name", "badge_number"]
    assert result.iloc[0]["badge_number"] == "00123"


def test_loads_cp1252_csv() -> None:
    source = BytesIO(
        "cardholder_name,badge_number\nTest Us\xe9,00123\n".encode("cp1252")
    )

    result = load_cardholder_csv(source)

    assert result.iloc[0]["cardholder_name"] == "Test Usé"


def test_rejects_csv_exceeding_byte_limit(tmp_path: Path) -> None:
    path = tmp_path / "large.csv"
    path.write_bytes(b"a" * (MAX_UPLOAD_BYTES + 1))

    with pytest.raises(ValueError, match="maximum size"):
        load_cardholder_csv(path)


def test_rejects_stream_exceeding_byte_limit() -> None:
    source = BytesIO(b"a" * (MAX_UPLOAD_BYTES + 1))

    with pytest.raises(ValueError, match="maximum size"):
        load_cardholder_csv(source)


def test_rejects_csv_exceeding_record_limit() -> None:
    header = "cardholder_name,badge_number\n"
    rows = "".join(f"User {index},{index}\n" for index in range(MAX_RECORDS + 1))
    source = BytesIO((header + rows).encode("utf-8"))

    with pytest.raises(ValueError, match="maximum of"):
        load_cardholder_csv(source, max_bytes=10 * 1024 * 1024)
