import streamlit as st
import streamlit.components.v1 as components

from access_control_analyzer.analyzer import (
    analyze_cardholders,
    findings_to_dataframe,
    summarize_cardholders,
)
from access_control_analyzer.loader import load_cardholder_csv
from access_control_analyzer.presentation import build_summary_metrics
from access_control_analyzer.reporting import generate_executive_report_html

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

uploaded_file = st.file_uploader(
    "Upload cardholder CSV",
    type=["csv"],
)

if uploaded_file is not None:
    try:
        records = load_cardholder_csv(uploaded_file)
        typed_findings = analyze_cardholders(records)
        summary = summarize_cardholders(records, typed_findings)
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

            visible_findings = findings.loc[
                findings["rule_name"].isin(selected_rules)
                & findings["severity"].isin(selected_severities)
            ]

            st.dataframe(
                visible_findings,
                use_container_width=True,
                hide_index=True,
            )

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
