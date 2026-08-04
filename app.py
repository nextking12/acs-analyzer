import streamlit as st

from access_control_analyzer.analyzer import (
    analyze_cardholders,
    findings_to_dataframe,
)
from access_control_analyzer.loader import load_cardholder_csv

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
        findings = findings_to_dataframe(analyze_cardholders(records))
    except ValueError as exc:
        st.error(str(exc))
    else:
        metric_one, metric_two, metric_three = st.columns(3)

        metric_one.metric(
            "Records analyzed",
            len(records),
        )

        metric_two.metric(
            "Total findings",
            len(findings),
        )

        metric_three.metric(
            "High-severity findings",
            findings["severity"].eq("High").sum(),
        )

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
