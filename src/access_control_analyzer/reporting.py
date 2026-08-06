import html

import pandas as pd

from access_control_analyzer.models import AnalysisSummary, Severity

PRODUCT_NAME = "Access Control Data Analyzer"

RULE_NAMES: dict[str, str] = {
    "expired_active_credential": "Expired active credential",
    "missing_or_invalid_expiration": "Missing or invalid expiration date",
    "duplicate_badge_number": "Duplicate badge number",
    "active_missing_department": "Active credential missing department",
}

DEFAULT_RECOMMENDED_ACTIONS: dict[str, str] = {
    "expired_active_credential": (
        "Disable the credential or confirm and update its expiration date."
    ),
    "missing_or_invalid_expiration": (
        "Set a valid expiration date or disable the credential."
    ),
    "duplicate_badge_number": (
        "Verify ownership and assign a unique badge number to each record."
    ),
    "active_missing_department": (
        "Assign the cardholder to the appropriate department."
    ),
}

DISCLAIMER = (
    "This report was generated locally by the Access Control Data Analyzer. "
    "Cardholder data is processed on the user's machine and is not transmitted "
    "to any external service. Use synthetic or explicitly approved test data for "
    "demonstrations. Findings reflect the state of the supplied export at the "
    "analysis date and should be confirmed against the source access-control "
    "system before corrective action is taken."
)

_REPORT_CSS = """
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  margin: 32px;
  color: #1f2933;
}
h1 { margin-bottom: 0; }
.meta { color: #52606d; margin: 4px 0 24px; font-size: 0.95rem; }
section { margin-bottom: 28px; }
h2 { border-bottom: 1px solid #cbd2d9; padding-bottom: 6px; }
table { border-collapse: collapse; width: 100%; font-size: 0.9rem; }
th, td {
  border: 1px solid #cbd2d9;
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}
th { background: #f4f6f8; }
.severity-High { color: #c0392b; font-weight: 600; }
.severity-Medium { color: #b9770e; font-weight: 600; }
.counts td { text-align: right; }
.disclaimer {
  font-size: 0.85rem;
  color: #52606d;
  border-top: 1px solid #cbd2d9;
  padding-top: 12px;
}
@media print { body { margin: 12mm; } }
"""


def _escape(text: object) -> str:
    return html.escape(str(text) if text is not None else "", quote=False)


def _executive_summary_lines(summary: AnalysisSummary) -> list[str]:
    lines = [
        f"Analyzed {summary.records_analyzed} cardholder record"
        f"{'s' if summary.records_analyzed != 1 else ''} on "
        f"{summary.analysis_date.isoformat()}.",
        (
            f"Found {summary.total_findings} audit finding"
            f"{'s' if summary.total_findings != 1 else ''}, "
            f"of which {summary.findings_by_severity.get(Severity.HIGH, 0)} are "
            f"high severity and {summary.findings_by_severity.get(Severity.MEDIUM, 0)} "
            f"are medium severity."
        ),
    ]
    if not summary.total_findings:
        lines.append("No data-quality issues were detected in the supplied export.")
    return lines


def _status_counts_table(summary: AnalysisSummary) -> str:
    rows = [
        ("Active credentials", summary.active_credentials),
        ("Inactive credentials", summary.inactive_credentials),
        ("Other / missing status credentials", summary.other_status_credentials),
        ("Total records analyzed", summary.records_analyzed),
    ]
    body = "\n".join(
        f"      <tr><td>{_escape(label)}</td><td>{value}</td></tr>"
        for label, value in rows
    )
    return (
        '<table class="counts">\n'
        "  <thead><tr><th>Status</th><th>Count</th></tr></thead>\n"
        f"  <tbody>\n{body}\n  </tbody>\n</table>"
    )


def _finding_counts_tables(summary: AnalysisSummary) -> str:
    severity_rows = "\n".join(
        f"      <tr><td>{_escape(severity.value)}</td><td>{count}</td></tr>"
        for severity, count in summary.findings_by_severity.items()
    )
    rule_rows = "\n".join(
        f"      <tr><td>{_escape(RULE_NAMES.get(rule_id, rule_id))}</td>"
        f"<td>{count}</td></tr>"
        for rule_id, count in summary.findings_by_rule.items()
    )
    return (
        '<table class="counts">\n'
        "  <thead><tr><th>Severity</th><th>Findings</th></tr></thead>\n"
        f"  <tbody>\n{severity_rows}\n  </tbody>\n</table>\n"
        '<table class="counts">\n'
        "  <thead><tr><th>Rule</th><th>Findings</th></tr></thead>\n"
        f"  <tbody>\n{rule_rows}\n  </tbody>\n</table>"
    )


def _findings_table(findings: pd.DataFrame) -> str:
    if findings.empty:
        return "<p>No audit findings were identified.</p>"

    headers = "\n".join(
        f"      <th>{_escape(column)}</th>" for column in findings.columns
    )
    body_rows = []
    for _, row in findings.iterrows():
        cells = "\n".join(f"        <td>{_escape(value)}</td>" for value in row.values)
        severity_class = (
            f' class="severity-{_escape(row["severity"])}"'
            if "severity" in findings.columns
            else ""
        )
        body_rows.append(f"      <tr{severity_class}>\n{cells}\n      </tr>")

    return (
        "<table>\n"
        f"  <thead>\n    <tr>\n{headers}\n    </tr>\n  </thead>\n"
        f"  <tbody>\n{chr(10).join(body_rows)}\n  </tbody>\n</table>"
    )


def _recommended_actions(summary: AnalysisSummary, findings: pd.DataFrame) -> str:
    triggered_rules = [
        rule_id for rule_id, count in summary.findings_by_rule.items() if count
    ]

    if not triggered_rules:
        return "<p>No corrective actions are required.</p>"

    observed_actions: dict[str, str] = dict(DEFAULT_RECOMMENDED_ACTIONS)
    has_action_columns = (
        not findings.empty
        and "rule_id" in findings.columns
        and "recommended_action" in findings.columns
    )
    if has_action_columns:
        for rule_id, action in zip(
            findings["rule_id"], findings["recommended_action"], strict=True
        ):
            observed_actions[str(rule_id)] = str(action)

    items = "\n".join(
        f"  <li><strong>{_escape(RULE_NAMES.get(rule_id, rule_id))}:</strong> "
        f"{_escape(observed_actions.get(rule_id, ''))}</li>"
        for rule_id in triggered_rules
    )
    return f"<ul>\n{items}\n</ul>"


def generate_executive_report_html(
    summary: AnalysisSummary,
    findings: pd.DataFrame,
) -> str:
    executive_lines = "\n".join(
        f"    <p>{_escape(line)}</p>" for line in _executive_summary_lines(summary)
    )
    status_table = _status_counts_table(summary)
    counts_tables = _finding_counts_tables(summary)
    findings_table = _findings_table(findings)
    actions = _recommended_actions(summary, findings)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{_escape(PRODUCT_NAME)} - Audit Report</title>
<style>{_REPORT_CSS}</style>
</head>
<body>
<h1>{_escape(PRODUCT_NAME)}</h1>
<p class="meta">Executive audit report &middot; analysis date
{_escape(summary.analysis_date.isoformat())}</p>

<section>
<h2>Executive summary</h2>
{executive_lines}
</section>

<section>
<h2>Credential status</h2>
{status_table}
</section>

<section>
<h2>Findings by severity and rule</h2>
{counts_tables}
</section>

<section>
<h2>Detailed findings</h2>
{findings_table}
</section>

<section>
<h2>Recommended corrective actions</h2>
{actions}
</section>

<p class="disclaimer">{_escape(DISCLAIMER)}</p>
</body>
</html>
"""
