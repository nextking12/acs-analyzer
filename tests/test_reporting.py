from datetime import date

import pandas as pd

from access_control_analyzer.analyzer import (
    analyze_cardholders,
    findings_to_dataframe,
    summarize_cardholders,
)
from access_control_analyzer.models import Severity
from access_control_analyzer.reporting import (
    DISCLAIMER,
    PRODUCT_NAME,
    RULE_NAMES,
    generate_executive_report_html,
)


def _sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "cardholder_name": ["Expired", "Duplicate A", "Duplicate B", "No Dept"],
            "badge_number": ["10001", "10001", "10001", "10004"],
            "department": ["Operations", "Engineering", "Finance", None],
            "credential_status": ["active", "active", "inactive", "active"],
            "expiration_date": ["2025-01-01", "2027-01-01", "2027-01-01", "2027-01-01"],
        }
    )


def _render(
    dataframe: pd.DataFrame | None = None,
    *,
    as_of_date: date = date(2026, 7, 28),
) -> str:
    dataframe = _sample_dataframe() if dataframe is None else dataframe
    findings = analyze_cardholders(dataframe, as_of_date=as_of_date)
    summary = summarize_cardholders(dataframe, findings, as_of_date=as_of_date)
    findings_df = findings_to_dataframe(findings)
    return generate_executive_report_html(summary, findings_df)


def test_report_includes_product_name_and_analysis_date() -> None:
    html_report = _render()

    assert PRODUCT_NAME in html_report
    assert "2026-07-28" in html_report


def test_report_includes_all_required_sections() -> None:
    html_report = _render()

    for heading in (
        "Executive summary",
        "Credential status",
        "Findings by severity and rule",
        "Detailed findings",
        "Recommended corrective actions",
    ):
        assert f"<h2>{heading}</h2>" in html_report


def test_report_includes_disclaimer() -> None:
    html_report = _render()

    assert DISCLAIMER in html_report


def test_report_includes_status_counts() -> None:
    html_report = _render()

    assert "Active credentials" in html_report
    assert "Inactive credentials" in html_report
    assert "Other / missing status credentials" in html_report
    assert "Total records analyzed" in html_report


def test_report_includes_rule_names_and_severity_labels() -> None:
    html_report = _render()

    for rule_name in RULE_NAMES.values():
        assert rule_name in html_report
    assert Severity.HIGH.value in html_report
    assert Severity.MEDIUM.value in html_report


def test_report_lists_triggered_recommended_actions_only() -> None:
    html_report = _render()

    # expired + duplicate + active_missing_department triggered;
    # missing_or_invalid_expiration is not.
    assert "Disable the credential" in html_report
    assert "Verify ownership and assign a unique badge" in html_report
    assert "Assign the cardholder to the appropriate department" in html_report
    assert "Set a valid expiration date" not in html_report


def test_report_renders_detailed_findings_table_with_rows() -> None:
    html_report = _render()

    assert "<table>" in html_report
    assert "Expired active credential" in html_report
    assert "10001" in html_report


def test_report_handles_zero_findings() -> None:
    dataframe = pd.DataFrame(
        {
            "cardholder_name": ["Valid"],
            "badge_number": ["10001"],
            "department": ["Operations"],
            "credential_status": ["active"],
            "expiration_date": ["2027-01-01"],
        }
    )
    findings = analyze_cardholders(dataframe, as_of_date=date(2026, 7, 28))
    summary = summarize_cardholders(dataframe, findings, as_of_date=date(2026, 7, 28))
    findings_df = findings_to_dataframe(findings)

    html_report = generate_executive_report_html(summary, findings_df)

    assert "No audit findings were identified." in html_report
    assert "No corrective actions are required." in html_report
    for rule_name in RULE_NAMES.values():
        assert rule_name in html_report


def test_report_is_deterministic_for_fixed_inputs() -> None:
    first = _render()
    second = _render()

    assert first == second


def test_report_escipes_user_supplied_text() -> None:
    dataframe = pd.DataFrame(
        {
            "cardholder_name": ["<script>alert(1)</script>"],
            "badge_number": ["10001"],
            "department": ["Ops"],
            "credential_status": ["active"],
            "expiration_date": ["2025-01-01"],
        }
    )
    html_report = _render(dataframe)

    assert "<script>alert(1)</script>" not in html_report
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_report
