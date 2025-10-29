#!/usr/bin/env python3
"""
Github-run scraper for JobList365 (joblist365.github.io)
Reads:  JobList365_data.csv
Writes: data/JobList365_data_updated_20.csv
"""

import os
import re
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

# ---------- CONFIG ----------
INPUT_PATH = "JobList365_data.csv"
OUTPUT_PATH = "data/JobList365_data_updated_20.csv"
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY", "")
LIMIT = 20
MAX_WORKERS = 10
REQUEST_TIMEOUT = 15
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobList365Bot/1.0)"}

# Make sure data folder exists
os.makedirs("data", exist_ok=True)

if not SCRAPERAPI_KEY:
    raise SystemExit("❌ ERROR: SCRAPERAPI_KEY not found. Add it to GitHub Secrets.")

# ---------- HELPERS ----------
def scraperapi_get(url):
    api = "http://api.scraperapi.com"
    params = {"api_key": SCRAPERAPI_KEY, "url": url, "render": "false", "country_code": "in"}
    try:
        r = requests.get(api, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return ""

def pick_official_site_from_search_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/url?q="):
            m = re.search(r"/url\?q=(https?://[^&]+)", href)
            if m:
                link = m.group(1)
                if not any(bad in link for bad in ["linkedin", "facebook", "youtube", "instagram", "justdial", "indiamart"]):
                    return link
    return ""

def google_search_company_site(company):
    q = quote_plus(f"{company} official website")
    html = scraperapi_get(f"https://www.google.com/search?q={q}")
    return pick_official_site_from_search_html(html)

def google_search_linkedin(company):
    q = quote_plus(f"site:linkedin.com/company {company}")
    html = scraperapi_get(f"https://www.google.com/search?q={q}")
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = re.search(r"/url\?q=(https?://[^&]+)", href)
        if m:
            link = m.group(1)
            if "linkedin.com/company" in link:
                return link
    return ""

def find_roles(text):
    pattern = r"\b(software engineer|developer|analyst|manager|consultant|associate|executive|marketing|qa engineer|project manager|sales executive)\b"
    return ", ".join(set(re.findall(pattern, text, flags=re.IGNORECASE)))

def worker(i, company):
    res = {"CompanyName": company, "Website": "", "LinkedIn": "", "Roles": ""}
    try:
        res["Website"] = google_search_company_site(company)
        res["LinkedIn"] = google_search_linkedin(company)
        if res["LinkedIn"]:
            html = scraperapi_get(res["LinkedIn"])
            if html:
                roles = find_roles(html)
                if roles:
                    res["Roles"] = roles
    except Exception:
        pass
    return res

# ---------- MAIN ----------
def main():
    df = pd.read_csv(INPUT_PATH, dtype=str)
    df = df.head(LIMIT)
    print(f"Scraping first {len(df)} companies...")

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = {exe.submit(worker, i, str(row["CompanyName"])): i for i, row in df.iterrows()}
        for fut in as_completed(futures):
            results.append(fut.result())

    out_df = pd.DataFrame(results)
    out_df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Done! Results saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
