#!/usr/bin/env python3
"""
Scraper for JobList365 — test with 20 companies
Reads:  Joblist365_data.csv
Writes: data/Joblist365_data_updated_20.csv

Columns:
CompanyName, CompanyStateCode, CompanyIndustrialClassification, Website, Roles, LinkedIn
"""

import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------- CONFIG ----------
INPUT_PATH = "Joblist365_data.csv"
OUTPUT_PATH = "data/Joblist365_data_updated_20.csv"
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY", "")
LIMIT = 20
MAX_WORKERS = 5  # smaller number to test stability
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobList365Bot/1.0)"}
# ----------------------------

if not SCRAPERAPI_KEY:
    raise SystemExit("❌ ERROR: SCRAPERAPI_KEY not found. Add it to GitHub Secrets or Colab env variable.")

# ---------- HELPERS ----------
def scraperapi_get(url):
    """Fetch URL through ScraperAPI"""
    api = "http://api.scraperapi.com"
    params = {"api_key": SCRAPERAPI_KEY, "url": url, "country_code": "in"}
    try:
        r = requests.get(api, params=params, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            return r.text
        else:
            print(f"⚠️ ScraperAPI status: {r.status_code} for {url}")
    except Exception as e:
        print(f"⚠️ Request failed: {e}")
    return ""

def extract_first_valid_link(html, exclude_words=None):
    """Extract first valid external link from Google search HTML."""
    if not html:
        return ""
    if exclude_words is None:
        exclude_words = ["linkedin.com", "facebook.com", "youtube.com", "twitter.com",
                         "instagram.com", "justdial", "indiamart", "tradeindia"]

    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = re.search(r"/url\?q=(https?://[^&]+)", href)
        if m:
            link = m.group(1)
            if not any(bad in link.lower() for bad in exclude_words):
                links.append(link)
        elif href.startswith("http") and not any(bad in href.lower() for bad in exclude_words):
            links.append(href)
    return links[0] if links else ""

def google_search_official_website(company):
    q = quote_plus(f"{company} official website")
    html = scraperapi_get(f"https://www.google.com/search?q={q}")
    return extract_first_valid_link(html)

def google_search_linkedin(company):
    q = quote_plus(f"site:linkedin.com/company {company}")
    html = scraperapi_get(f"https://www.google.com/search?q={q}")
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        m = re.search(r"/url\?q=(https?://[^&]+)", a["href"])
        if m and "linkedin.com/company" in m.group(1).lower():
            return m.group(1)
    return ""

def find_roles_from_text(text):
    roles_pattern = r"\b(software engineer|developer|data scientist|analyst|manager|consultant|associate|officer|executive|qa engineer|project manager|sales executive|marketing manager|accountant|designer|intern|technician)\b"
    found = re.findall(roles_pattern, text, flags=re.IGNORECASE)
    return ", ".join(sorted(set([f.title() for f in found]))) if found else ""

def extract_roles(company, linkedin_url=""):
    if linkedin_url:
        html = scraperapi_get(linkedin_url)
        if html:
            text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
            roles = find_roles_from_text(text)
            if roles:
                return roles
    q = quote_plus(f"{company} jobs openings careers")
    html = scraperapi_get(f"https://www.google.com/search?q={q}")
    if html:
        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        roles = find_roles_from_text(text)
        if roles:
            return roles
    return ""

def process_company(i, row):
    company = str(row["CompanyName"])
    result = {"Website": "", "LinkedIn": "", "Roles": ""}
    print(f"🔍 [{i+1}] Searching: {company}")

    result["Website"] = google_search_official_website(company)
    result["LinkedIn"] = google_search_linkedin(company)
    result["Roles"] = extract_roles(company, result["LinkedIn"])

    print(f"✅ [{i+1}] {company} → W:{bool(result['Website'])}, L:{bool(result['LinkedIn'])}, R:{bool(result['Roles'])}")
    return result

# ---------- MAIN ----------
def main():
    if not os.path.exists(INPUT_PATH):
        raise SystemExit(f"❌ Missing file: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH, dtype=str)
    df.fillna("", inplace=True)

    if "CompanyName" not in df.columns:
        raise SystemExit("❌ Column 'CompanyName' missing in CSV!")

    df = df.head(LIMIT)
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = {exe.submit(process_company, i, row): i for i, row in df.iterrows()}
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                res = fut.result()
                for key, val in res.items():
                    df.at[i, key] = val
            except Exception as e:
                print(f"⚠️ Error processing row {i}: {e}")

    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n✅ Finished scraping {len(df)} companies.")
    print(f"📁 Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
