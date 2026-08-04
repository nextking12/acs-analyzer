from datetime import date

import pandas as pd

from access_control_analyzer.models import Severity
from access_control_analyzer.normalizer import normalize_cardholders
from access_control_analyzer.rules import (
    find_active_credentials_missing_departments,
    find_duplicate_badge_numbers,
    find_expired_active_credentials,
    find_missing_or_invalid_expiration_dates,
)


def _normalized_records() -> pd.DataFrame:
    return normalize_cardholders(
        pd.DataFrame(
            {
                "cardholder_name": [
                    "Expired Active",
                    "Valid Active",
                    "Expired Inactive",
                    "Missing Date",
                    "Invalid Date",
                ],
                "badge_number": ["10001", "10002", "10003", "10004", "10005"],
                "department": ["Operations", "Engineering", "Security", None, "Legal"],
                "credential_status": [
                    "active",
                    "active",
                    "inactive",
                    "active",
                    "active",
                ],
                "expiration_date": [
                    "2025-12-31",
                    "2027-01-01",
                    "2025-01-01",
                    None,
                    "not-a-date",
                ],
            }
        )
    )


def test_finds_only_expired_active_credentials() -> None:
    findings = find_expired_active_credentials(
        _normalized_records(),
        as_of_date=date(2026, 7, 28),
    )

    assert len(findings) == 1
    assert findings[0].badge_number == "10001"
    assert findings[0].severity is Severity.HIGH
    assert findings[0].source_row == 2


def test_handles_timezone_aware_expiration_dates() -> None:
    records = _normalized_records()
    records.loc[0, "expiration_date"] = "2025-12-31T23:00:00-05:00"

    findings = find_expired_active_credentials(
        records,
        as_of_date=date(2026, 7, 28),
    )

    assert len(findings) == 1


def test_finds_missing_and_invalid_dates_only_for_active_credentials() -> None:
    records = _normalized_records()
    records.loc[2, "expiration_date"] = None

    findings = find_missing_or_invalid_expiration_dates(records)

    assert {finding.badge_number for finding in findings} == {"10004", "10005"}


def test_finds_each_record_with_a_duplicate_nonblank_badge() -> None:
    records = _normalized_records()
    records.loc[1, "badge_number"] = "10001"
    records.loc[2, "badge_number"] = None

    findings = find_duplicate_badge_numbers(records)

    assert [finding.source_row for finding in findings] == [2, 3]
    assert all("2 records" in finding.description for finding in findings)


def test_finds_missing_departments_only_for_active_credentials() -> None:
    records = _normalized_records()
    records.loc[2, "department"] = None

    findings = find_active_credentials_missing_departments(records)

    assert len(findings) == 1
    assert findings[0].badge_number == "10004"
    assert findings[0].severity is Severity.MEDIUM
