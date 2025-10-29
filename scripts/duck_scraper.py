#!/usr/bin/env python3
"""
DuckDuckGo Scraper for JobList365 (Free + Safe)
Reads:  Joblist365_data.csv
Writes: data/Joblist365_data_duckduck_updated.csv

Columns handled:
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
INPUT_PATH = "JobList365_data.csv"
OUTPUT_PATH = "data/Joblist365_data_duckduck_updated.csv"
LIMIT = 10               # process 10 companies for testing
MAX_WORKERS = 5
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobList365Bot/1.0)"}
# ----------------------------

def duckduckgo_search(query):
    """Fetch HTML from DuckDuckGo search results."""
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        print(f"⚠️ DuckDuckGo error: {e}")
    return ""

def extract_first_link(html, include=None, exclude=None):
    """Extract first relevant link from DuckDuckGo HTML."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.select("a.result__a[href]"):
        href = a["href"]
        if exclude and any(x in href.lower() for x in exclude):
            continue
        if include and not any(x in href.lower() for x in include):
            continue
        return href
    return ""

def find_roles_in_text(text):
    """Extract possible role/job titles from raw text."""
    pattern = r"\b(software engineer|developer|data scientist|analyst|manager|consultant|associate|officer|executive|qa engineer|project manager|sales executive|marketing manager|technician|intern|accountant)\b"
    found = re.findall(pattern, text, flags=re.IGNORECASE)
    return ", ".join(sorted(set([f.title() for f in found]))) if found else ""

def extract_roles(company):
    """Search jobs or openings for the company."""
    html = duckduckgo_search(f"{company} jobs OR openings OR careers")
    if not html:
        return ""
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    return find_roles_in_text(text)

def process_company(i, row):
    company = str(row["CompanyName"])
    result = {"Website": "", "LinkedIn": "", "Roles": ""}
    print(f"🔍 [{i+1}] Searching: {company}")

    # Official website
    html = duckduckgo_search(f"{company} official website")
    result["Website"] = extract_first_link(html, exclude=["linkedin", "facebook", "justdial", "indiamart"])

    # LinkedIn
    html_ln = duckduckgo_search(f"site:linkedin.com/company {company}")
    result["LinkedIn"] = extract_first_link(html_ln, include=["linkedin.com/company"])

    # Roles
    result["Roles"] = extract_roles(company)

    print(f"✅ [{i+1}] {company} → W:{bool(result['Website'])}, L:{bool(result['LinkedIn'])}, R:{bool(result['Roles'])}")
    return result

def main():
    if not os.path.exists(INPUT_PATH):
        raise SystemExit(f"❌ Missing input file: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH, dtype=str)
    df.fillna("", inplace=True)
    if "CompanyName" not in df.columns:
        raise SystemExit("❌ Column 'CompanyName' missing in CSV!")

    df = df.head(LIMIT)
    os.makedirs("data", exist_ok=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = {exe.submit(process_company, i, row): i for i, row in df.iterrows()}
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                res = fut.result()
                for k, v in res.items():
                    df.at[i, k] = v
            except Exception as e:
                print(f"⚠️ Row {i} failed: {e}")

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n✅ Finished scraping {len(df)} companies.")
    print(f"📁 Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
