# Scrapers/oracle_jobs_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import time

URL = (
    "https://estm.fa.em2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs"
    "?location=India&locationId=300000000440677&locationLevel=country&mode=location"
)

OUTPUT_FILE = "output/oracle_india_jobs.xlsx"


def safe_text(parent, by, value):
    try:
        return parent.find_element(by, value).text.strip()
    except:
        return ""


def get_driver():
    options = Options()
    options.add_argument("--headless=new")       # Headless mode for CI / GitHub Actions
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def scrape_jobs():
    driver = get_driver()
    wait = WebDriverWait(driver, 30)

    driver.get(URL)

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.job-grid-item__content")
        )
    )

    time.sleep(3)  # ensure all jobs loaded

    cards = driver.find_elements(By.CSS_SELECTOR, "div.job-grid-item__content")
    print(f"✅ Found {len(cards)} jobs")

    jobs = []

    for card in cards:
        title = safe_text(card, By.CSS_SELECTOR, "span.job-tile__title")
        location = safe_text(card, By.CSS_SELECTOR, "span[data-bind*='primaryLocation']")
        posting_date = safe_text(card, By.XPATH, ".//div[contains(text(),'Posting Date')]/following::div[1]")

        # ✅ CRITICAL FIX: get <a> as PRECEDING sibling
        try:
            apply_link = card.find_element(
                By.XPATH,
                "ancestor::div[contains(@class,'job-grid-item__link')]/preceding-sibling::a[@class='job-grid-item__link']"
            ).get_attribute("href")
        except:
            apply_link = ""

        if title or apply_link:
            jobs.append({
                "Source": "Oracle Careers",
                "Title": title,
                "Location": location,
                "Posting_Date": posting_date,
                "Apply_Link": apply_link
            })

    driver.quit()
    return pd.DataFrame(jobs)


def save_to_excel(df):
    os.makedirs("output", exist_ok=True)

    if df.empty:
        print("⚠️ No data found, creating empty Excel")
        df = pd.DataFrame(columns=[
            "Source", "Title", "Location", "Posting_Date", "Apply_Link"
        ])

    # Make Apply link clickable
    df["Apply_Link"] = df["Apply_Link"].apply(
        lambda x: f'=HYPERLINK("{x}", "Apply")' if x else ""
    )

    df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
    print(f"✅ Excel file created: {OUTPUT_FILE}")


def main():
    df = scrape_jobs()
    save_to_excel(df)


if __name__ == "__main__":
    main()
