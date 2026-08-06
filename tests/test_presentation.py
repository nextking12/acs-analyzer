from datetime import date

from access_control_analyzer.models import AnalysisSummary, Severity
from access_control_analyzer.presentation import (
    OTHER_STATUS_LABEL,
    build_summary_metrics,
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
