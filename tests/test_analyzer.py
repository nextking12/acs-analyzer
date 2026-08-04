from datetime import date

import pandas as pd

from access_control_analyzer.analyzer import (
    FINDING_COLUMNS,
    analyze_cardholders,
    findings_to_dataframe,
)


def test_analyzer_consolidates_all_rule_findings() -> None:
    dataframe = pd.DataFrame(
        {
            "cardholder_name": [
                "Expired",
                "Duplicate",
                "Missing Date",
                "No Department",
            ],
            "badge_number": ["10001", "10001", "10003", "10004"],
            "department": ["Operations", "Engineering", "Finance", None],
            "credential_status": ["active", "active", "active", "active"],
            "expiration_date": ["2025-01-01", "2027-01-01", None, "2027-01-01"],
            "last_access_date": ["2026-01-01", None, "2026-02-01", "2026-03-01"],
        }
    )

    findings = analyze_cardholders(dataframe, as_of_date=date(2026, 7, 28))
    results = findings_to_dataframe(findings)

    assert len(results) == 5
    assert results["rule_id"].value_counts().to_dict() == {
        "duplicate_badge_number": 2,
        "expired_active_credential": 1,
        "missing_or_invalid_expiration": 1,
        "active_missing_department": 1,
    }
    assert results.loc[0, "last_access_date"] == "2026-01-01"


def test_empty_findings_dataframe_keeps_export_columns() -> None:
    results = findings_to_dataframe([])

    assert results.empty
    assert results.columns.tolist() == FINDING_COLUMNS


def test_preserves_source_columns_that_conflict_with_report_fields() -> None:
    dataframe = pd.DataFrame(
        {
            "cardholder_name": ["Expired"],
            "badge_number": ["10001"],
            "department": ["Operations"],
            "credential_status": ["active"],
            "expiration_date": ["2025-01-01"],
            "severity": ["Vendor priority"],
            "_vendor_id": ["ABC-123"],
        }
    )

    findings = analyze_cardholders(dataframe, as_of_date=date(2026, 7, 28))
    results = findings_to_dataframe(findings)

    assert results.loc[0, "source_severity"] == "Vendor priority"
    assert results.loc[0, "_vendor_id"] == "ABC-123"
