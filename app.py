import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from access_control_analyzer.analyzer import (
    AnalysisResult,
    findings_to_dataframe,
    run_analysis,
)
from access_control_analyzer.loader import CsvSource, load_cardholder_csv
from access_control_analyzer.models import AnalysisSummary
from access_control_analyzer.presentation import (
    AUDIT_RULE_GUIDE,
    REQUIRED_CSV_COLUMNS,
    WORKFLOW_STEPS,
    build_summary_metrics,
    get_sample_cardholder_path,
)
from access_control_analyzer.reporting import generate_executive_report_html


def _load_analysis(source: CsvSource) -> AnalysisResult:
    return run_analysis(load_cardholder_csv(source))


def _filter_findings(
    findings: pd.DataFrame,
    *,
    selected_rules: list[str],
    selected_severities: list[str],
) -> pd.DataFrame:
    return findings.loc[
        findings["rule_name"].isin(selected_rules)
        & findings["severity"].isin(selected_severities)
    ]


def _render_exports(summary: AnalysisSummary, findings: pd.DataFrame) -> None:
    st.download_button(
        label="Download all findings",
        data=findings.to_csv(index=False),
        file_name="access_control_audit_findings.csv",
        mime="text/csv",
    )

    st.subheader("Executive report")
    report_html = generate_executive_report_html(summary, findings)

    st.download_button(
        label="Download executive report (HTML)",
        data=report_html,
        file_name="access_control_audit_report.html",
        mime="text/html",
    )

    with st.expander("Print preview"):
        components.html(report_html, height=600, scrolling=True)


st.set_page_config(
    page_title="Access Control Data Analyzer",
    page_icon="🔐",
    layout="wide",
)

st.title("Access Control Data Analyzer")

st.write(
    """
    Upload an access-control cardholder export to identify expired
    credentials and other data-quality issues.
    """
)

st.warning(
    """
    Use synthetic or approved test data only. Do not upload operational
    security data or personally identifiable information.
    """
)

with st.expander("How it works"):
    for index, step in enumerate(WORKFLOW_STEPS, start=1):
        st.write(f"{index}. {step}")

with st.expander("Audit rules"):
    for rule_name, severity in AUDIT_RULE_GUIDE:
        st.write(f"- **{rule_name}** — {severity}")

with st.expander("CSV format"):
    st.write("Required columns:")
    for column in REQUIRED_CSV_COLUMNS:
        st.write(f"- `{column}`")
    st.write(
        "Additional columns are preserved in the findings export. "
        "Column names are normalized by trimming whitespace and converting "
        "them to lowercase."
    )

data_source = st.radio(
    "Data source",
    ("Upload CSV", "Use sample data"),
    horizontal=True,
)

source = None

if data_source == "Upload CSV":
    source = st.file_uploader(
        "Upload cardholder CSV",
        type=["csv"],
    )
else:
    try:
        sample_path = get_sample_cardholder_path()
    except FileNotFoundError as exc:
        st.error(str(exc))
    else:
        st.info(
            "Using the built-in synthetic sample at "
            f"`{sample_path.name}`. No operational data is loaded."
        )
        source = sample_path

if source is not None:
    try:
        analysis = _load_analysis(source)
        typed_findings = analysis.findings
        summary = analysis.summary
        findings = findings_to_dataframe(typed_findings)
    except ValueError as exc:
        st.error(str(exc))
    else:
        summary_metrics = build_summary_metrics(summary)
        metric_columns = st.columns(len(summary_metrics))

        for column, (label, value) in zip(metric_columns, summary_metrics, strict=True):
            column.metric(label, value)

        st.subheader("Audit findings")

        if findings.empty:
            st.success("No audit findings were identified.")
        else:
            filter_one, filter_two = st.columns(2)
            rule_names = sorted(findings["rule_name"].unique())
            severities = [
                severity
                for severity in ("High", "Medium")
                if severity in findings["severity"].values
            ]

            selected_rules = filter_one.multiselect(
                "Rules",
                rule_names,
                default=rule_names,
            )
            selected_severities = filter_two.multiselect(
                "Severities",
                severities,
                default=severities,
            )

            visible_findings = _filter_findings(
                findings,
                selected_rules=selected_rules,
                selected_severities=selected_severities,
            )

            st.dataframe(
                visible_findings,
                use_container_width=True,
                hide_index=True,
            )

        _render_exports(summary, findings)
