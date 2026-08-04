import streamlit as st

from access_control_analyzer.loader import load_cardholder_csv
from access_control_analyzer.rules import (
    find_expired_active_credentials,
)

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
        expired_credentials = find_expired_active_credentials(records)
    except ValueError as exc:
        st.error(str(exc))
    else:
        metric_one, metric_two = st.columns(2)

        metric_one.metric(
            "Records analyzed",
            len(records),
        )

        metric_two.metric(
            "Expired active credentials",
            len(expired_credentials),
        )

        st.subheader("Expired active credentials")

        if expired_credentials.empty:
            st.success("No expired active credentials were found.")
        else:
            st.dataframe(
                expired_credentials,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                label="Download findings",
                data=expired_credentials.to_csv(index=False),
                file_name="expired_active_credentials.csv",
                mime="text/csv",
            )