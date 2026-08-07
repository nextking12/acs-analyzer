from datetime import date
from pathlib import Path

import pytest

from access_control_analyzer.analyzer import analyze_cardholders, findings_to_dataframe
from access_control_analyzer.loader import load_cardholder_csv
from access_control_analyzer.models import AnalysisSummary, Severity
from access_control_analyzer.presentation import (
    OTHER_STATUS_LABEL,
    SAMPLE_CARDHOLDERS_RELATIVE,
    build_summary_metrics,
    dataframe_to_safe_csv,
    get_sample_cardholder_path,
    sanitize_csv_cell,
)


def _summary(**overrides: int) -> AnalysisSummary:
    base: dict[str, object] = {
        "analysis_date": date(2026, 7, 28),
        "records_analyzed": 4,
        "active_credentials": 2,
        "inactive_credentials": 1,
        "other_status_credentials": 1,
        "total_findings": 3,
        "findings_by_severity": {Severity.HIGH: 3, Severity.MEDIUM: 0},
        "findings_by_rule": {
            "expired_active_credential": 1,
            "missing_or_invalid_expiration": 0,
            "duplicate_badge_number": 2,
            "active_missing_department": 0,
        },
    }
    base.update(overrides)
    return AnalysisSummary.model_validate(base)


def test_build_summary_metrics_returns_core_metrics_in_order() -> None:
    summary = _summary(other_status_credentials=0)

    metrics = build_summary_metrics(summary)

    assert metrics == [
        ("Records analyzed", 4),
        ("Active credentials", 2),
        ("Inactive credentials", 1),
        ("Total findings", 3),
        ("High-severity findings", 3),
        ("Medium-severity findings", 0),
    ]


def test_build_summary_metrics_omits_other_status_when_zero() -> None:
    summary = _summary(other_status_credentials=0)

    metrics = build_summary_metrics(summary)

    assert not any(label == OTHER_STATUS_LABEL for label, _ in metrics)


def test_build_summary_metrics_includes_other_status_when_nonzero() -> None:
    summary = _summary(other_status_credentials=2)

    metrics = build_summary_metrics(summary)

    assert metrics[-1] == (OTHER_STATUS_LABEL, 2)


def test_build_summary_metrics_reports_zero_findings() -> None:
    summary = _summary(
        records_analyzed=1,
        active_credentials=1,
        inactive_credentials=0,
        other_status_credentials=0,
        total_findings=0,
        findings_by_severity={Severity.HIGH: 0, Severity.MEDIUM: 0},
        findings_by_rule={
            "expired_active_credential": 0,
            "missing_or_invalid_expiration": 0,
            "duplicate_badge_number": 0,
            "active_missing_department": 0,
        },
    )

    metrics = build_summary_metrics(summary)

    assert metrics == [
        ("Records analyzed", 1),
        ("Active credentials", 1),
        ("Inactive credentials", 0),
        ("Total findings", 0),
        ("High-severity findings", 0),
        ("Medium-severity findings", 0),
    ]


def test_get_sample_cardholder_path_resolves_existing_file() -> None:
    path = get_sample_cardholder_path()

    assert path.is_file()
    assert path.name == SAMPLE_CARDHOLDERS_RELATIVE.name


def test_get_sample_cardholder_path_raises_when_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    fake_package_file = (
        tmp_path / "pkg" / "src" / "access_control_analyzer" / "presentation.py"
    )
    fake_package_file.parent.mkdir(parents=True)
    fake_package_file.write_text("# stub\n")
    monkeypatch.setattr(
        "access_control_analyzer.presentation.__file__",
        str(fake_package_file),
    )

    with pytest.raises(FileNotFoundError, match="Sample cardholder CSV not found"):
        get_sample_cardholder_path()


def test_sample_cardholders_trigger_all_rules() -> None:
    records = load_cardholder_csv(get_sample_cardholder_path())
    findings = analyze_cardholders(records, as_of_date=date(2026, 8, 6))
    results = findings_to_dataframe(findings)

    assert len(records) == 7
    assert set(results["rule_id"]) == {
        "expired_active_credential",
        "missing_or_invalid_expiration",
        "duplicate_badge_number",
        "active_missing_department",
    }


def test_sanitize_csv_cell_neutralizes_formula_prefixes() -> None:
    assert sanitize_csv_cell("=CMD()") == "'=CMD()"
    assert sanitize_csv_cell("+123") == "'+123"
    assert sanitize_csv_cell("-123") == "'-123"
    assert sanitize_csv_cell("@sum") == "'@sum"
    assert sanitize_csv_cell("\tTAB") == "'\tTAB"
    assert sanitize_csv_cell("safe") == "safe"
    assert sanitize_csv_cell(None) == ""


def test_dataframe_to_safe_csv_prefixes_formula_cells() -> None:
    import pandas as pd

    frame = pd.DataFrame(
        {
            "cardholder_name": ["=HYPERLINK()"],
            "badge_number": ["10001"],
        }
    )

    csv_text = dataframe_to_safe_csv(frame)

    assert "'=HYPERLINK()" in csv_text
    assert "=HYPERLINK()" in csv_text
    assert csv_text.splitlines()[1].startswith("'=")
