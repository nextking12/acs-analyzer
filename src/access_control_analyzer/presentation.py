from access_control_analyzer.models import AnalysisSummary, Severity

CORE_SUMMARY_METRICS: tuple[tuple[str, str], ...] = (
    ("Records analyzed", "records_analyzed"),
    ("Active credentials", "active_credentials"),
    ("Inactive credentials", "inactive_credentials"),
    ("Total findings", "total_findings"),
    ("High-severity findings", "high_findings"),
    ("Medium-severity findings", "medium_findings"),
)

OTHER_STATUS_LABEL = "Other / missing status credentials"


def build_summary_metrics(summary: AnalysisSummary) -> list[tuple[str, int]]:
    high = summary.findings_by_severity.get(Severity.HIGH, 0)
    medium = summary.findings_by_severity.get(Severity.MEDIUM, 0)

    values: dict[str, int] = {
        "records_analyzed": summary.records_analyzed,
        "active_credentials": summary.active_credentials,
        "inactive_credentials": summary.inactive_credentials,
        "total_findings": summary.total_findings,
        "high_findings": high,
        "medium_findings": medium,
    }

    metrics = [(label, values[key]) for label, key in CORE_SUMMARY_METRICS]

    if summary.other_status_credentials:
        metrics.append((OTHER_STATUS_LABEL, summary.other_status_credentials))

    return metrics
