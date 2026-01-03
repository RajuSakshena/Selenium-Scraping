import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="Oracle Jobs Dashboard",
    layout="wide"
)

st.title("Oracle Jobs – India")
st.caption("Data auto-updated via GitHub Actions")

EXCEL_PATH = "output/oracle_india_jobs.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_PATH)

def convert_df_to_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)
    return buffer

try:
    df = load_data()

    st.success(f"Loaded {len(df)} jobs")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        location_filter = st.multiselect(
            "Filter by Location",
            options=sorted(df["Location"].dropna().unique())
        )

    with col2:
        title_filter = st.text_input("Search Job Title")

    if location_filter:
        df = df[df["Location"].isin(location_filter)]

    if title_filter:
        df = df[df["Title"].str.contains(title_filter, case=False, na=False)]

    st.dataframe(df, use_container_width=True)

    excel_file = convert_df_to_excel(df)

    st.download_button(
        label="Download Excel",
        data=excel_file,
        file_name="oracle_jobs_india.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

except FileNotFoundError:
    st.error("Excel file not found. Please wait for GitHub Actions to run.")
