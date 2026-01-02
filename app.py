import streamlit as st
from Scrapers.oracle_jobs_scraper import scrape_oracle_jobs
# from Scrapers.another_site import scrape_another_site  # Future scraper

st.set_page_config(page_title="Job Scraper Dashboard", layout="wide")
st.title("Job Scraper Dashboard")

st.write("Click the button below to scrape Oracle India Jobs.")

if st.button("Scrape Oracle Jobs"):
    with st.spinner("Scraping Oracle Jobs..."):
        df = scrape_oracle_jobs()
        st.success(f"✅ Found {len(df)} jobs")
        st.dataframe(df)

        excel_data = df.to_excel(index=False, engine="openpyxl")
        st.download_button(
            label="Download Oracle Jobs Excel",
            data=excel_data,
            file_name="oracle_india_jobs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
