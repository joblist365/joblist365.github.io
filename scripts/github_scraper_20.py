#!/usr/bin/env python3
"""
Github-run scraper for JobList365 (joblist365.github.io)

Reads:  JobList365_data.csv
Writes: data/JobList365_data_updated.csv

Columns:
CompanyName, CompanyStateCode, CompanyIndustrialClassification, Website, Roles, LinkedIn
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
OUTPUT_PATH = "data/JobList365_data_updated.csv"
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY", "")
LIMIT = 20                 # number of companies to process
MAX_WORKERS = 20           # threads
REQUEST_TIMEOUT = 15
SAVE_EVERY = 5
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobList365Bot/1.0)"}
# ----------------------------

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
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = re.search(r"/url\?q=(https?://[^&]+)", href)
        if m:
            link = m.group(1)
            if not any(x in link.lower() for x in [
                "linkedin.com", "facebook.com", "twitter.com", "instagram.com",
                "youtube.com", "indiamart", "justdial", "tradeindia"
            ]):
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
        m = re.search(r"/url\?q=(https?://[^&]+)", a["href"])
        if m:
            link = m.group(1)
            if "linkedin.com/company" in link.lower():
                return link
    return ""

def find_roles_in_text(text):
    pattern = r"\b(software engineer|developer|data scientist|data engineer|analyst|manager|consultant|associate|officer|executive|qa engineer|project manager|nurse|doctor|medical coder|claims analyst|revenue cycle|receptionist|sales executive|marketing manager)\b"
    found = re.findall(pattern, text, flags=re.IGNORECASE)
    roles = []
    for f in found:
        role = f.title()
        if role not in roles:
            roles.append(role)
        if len(roles) >= 20:
            break
    return roles

def extract_roles(company, linkedin_url=""):
    roles = []
    if linkedin_url:
        html = scraperapi_get(linkedin_url)
        if html:
            text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
            roles = find_roles_in_text(text)
    if not roles:
        q = quote_plus(f"site:linkedin.com/jobs {company}")
        html = scraperapi_get(f"https://www.google.com/search?q={q}")
        if html:
            text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
            roles = find_roles_in_text(text)
    return ", ".join(roles[:10]) if roles else ""

def worker(i, company):
    result = {"CompanyName": company, "Website": "", "LinkedIn": "", "Roles": ""}
    try:
        result["Website"] = google_search_company_site(company)
        result["LinkedIn"] = google_search_linkedin(company)
        result["Roles"] = extract_roles(company, result["LinkedIn"])
    except Exception:
        pass
    return result

# ---------- MAIN ----------
def main():
    if not os.path.exists(INPUT_PATH):
        raise SystemExit(f"❌ Missing input file: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH, dtype=str).fillna("")
    df = df.head(LIMIT)

    for col in ["Website", "Roles", "LinkedIn"]:
        if col not in df.columns:
            df[col] = ""

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as exe:
        futures = {exe.submit(worker, i, df.at[i, "CompanyName"]): i for i in range(len(df))}
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                res = fut.result()
                for k in ["Website", "LinkedIn", "Roles"]:
                    df.at[i, k] = res.get(k, df.at[i, k])
            except Exception:
                pass

    final_cols = ["CompanyName", "CompanyStateCode", "CompanyIndustrialClassification", "Website", "Roles", "LinkedIn"]
    for c in final_cols:
        if c not in df.columns:
            df[c] = ""
    df = df[final_cols]
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Done. Updated file saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
