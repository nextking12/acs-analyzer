from datetime import date

from access_control_analyzer.analyzer import (
    analyze_cardholders,
    findings_to_dataframe,
    summarize_cardholders,
)
from access_control_analyzer.loader import load_cardholder_csv
from access_control_analyzer.presentation import (
    build_summary_metrics,
    dataframe_to_safe_csv,
    get_sample_cardholder_path,
)
from access_control_analyzer.reporting import generate_executive_report_html


def test_sample_end_to_end_workflow() -> None:
    records = load_cardholder_csv(get_sample_cardholder_path())
    findings = analyze_cardholders(records, as_of_date=date(2026, 8, 6))
    summary = summarize_cardholders(records, findings, as_of_date=date(2026, 8, 6))
    findings_frame = findings_to_dataframe(findings)
    metrics = build_summary_metrics(summary)
    report_html = generate_executive_report_html(summary, findings_frame)
    findings_csv = dataframe_to_safe_csv(findings_frame)

    assert summary.records_analyzed == 7
    assert summary.total_findings > 0
    assert metrics[0] == ("Records analyzed", 7)
    assert not findings_frame.empty
    assert "Executive summary" in report_html
    assert "Recommended corrective actions" in report_html
    assert "rule_id" in findings_csv
    assert "Expired active credential" in findings_csv
